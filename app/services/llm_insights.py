"""
LLM Insights Service — generates personalized study plans via OpenRouter.

After the student completes 10 questions, this service:
1. Aggregates performance data (weak topics, accuracy, final ability).
2. Constructs a focused prompt for the LLM.
3. Returns a 3-step personalized study plan.
"""

from openai import AsyncOpenAI
from app.config import get_settings
from app.models.schemas import UserSession

settings = get_settings()

# Lazy client initialization to avoid import-time httpx issues
_client: AsyncOpenAI | None = None


def _get_client() -> AsyncOpenAI:
    """Return the OpenAI client, creating it on first use."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
        )
    return _client


def _build_performance_summary(session: UserSession) -> tuple[str, list[str]]:
    """Build a structured performance summary from the session history."""

    total = session.questions_answered
    correct = session.total_correct
    accuracy = (correct / total * 100) if total > 0 else 0

    # Aggregate per-topic stats
    topic_stats: dict[str, dict] = {}
    for record in session.history:
        if record.topic not in topic_stats:
            topic_stats[record.topic] = {"total": 0, "correct": 0, "difficulties": []}
        topic_stats[record.topic]["total"] += 1
        topic_stats[record.topic]["difficulties"].append(record.difficulty)
        if record.is_correct:
            topic_stats[record.topic]["correct"] += 1

    # Identify weak topics (accuracy < 60%)
    weak_topics = []
    topic_breakdown = []
    for topic, stats in topic_stats.items():
        t_accuracy = stats["correct"] / stats["total"] * 100
        avg_diff = sum(stats["difficulties"]) / len(stats["difficulties"])
        topic_breakdown.append(
            f"  - {topic}: {stats['correct']}/{stats['total']} correct "
            f"({t_accuracy:.0f}%), avg difficulty {avg_diff:.2f}"
        )
        if t_accuracy < 60:
            weak_topics.append(topic)

    summary = (
        f"Student Performance Summary:\n"
        f"- Total Questions: {total}\n"
        f"- Overall Accuracy: {correct}/{total} ({accuracy:.1f}%)\n"
        f"- Final Ability Estimate: {session.current_ability:.3f} (scale 0-1)\n"
        f"- Topic Breakdown:\n" + "\n".join(topic_breakdown) + "\n"
        f"- Weak Topics: {', '.join(weak_topics) if weak_topics else 'None identified'}"
    )

    return summary, weak_topics


async def generate_study_plan(session: UserSession) -> tuple[str, list[str]]:
    """
    Generate a personalized 3-step study plan using the LLM.

    Args:
        session: The completed UserSession with full history.

    Returns:
        Tuple of (study_plan_text, weak_topics_list).
    """

    performance_summary, weak_topics = _build_performance_summary(session)

    prompt = f"""You are an expert educational tutor analyzing a student's GRE practice test results.

{performance_summary}

Based on this performance data, generate a **concise, actionable 3-step study plan** tailored to this student's specific weaknesses. 

Requirements:
- Each step should be specific, targeting their weak areas.
- Include recommended resources or practice strategies.
- Be encouraging but honest about areas needing improvement.
- Format as a numbered list with clear step titles and descriptions.

Respond ONLY with the 3-step study plan, no preamble."""

    response = await _get_client().chat.completions.create(
        model=settings.llm_model,
        messages=[
            {
                "role": "system",
                "content": "You are a knowledgeable GRE tutor. Provide actionable, personalized study advice.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=800,
    )

    plan_text = response.choices[0].message.content
    return plan_text, weak_topics
