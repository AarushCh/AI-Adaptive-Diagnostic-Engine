"""
Insights Routes — AI-generated study plan endpoint.

Endpoints:
    GET /api/session/{id}/plan — Get a personalized 3-step study plan (after 10 questions).
"""

from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.utils.database import Database
from app.models.schemas import UserSession, StudyPlan
from app.services.llm_insights import generate_study_plan

router = APIRouter(prefix="/api", tags=["AI Insights"])


@router.get("/session/{session_id}/plan")
async def get_study_plan(session_id: str):
    """
    Generate a personalized 3-step study plan using an LLM.

    The session must have at least 10 answered questions (is_complete = True).
    Constructs a performance summary and sends it to the LLM via OpenRouter.
    """
    db = Database.get_db()

    session_doc = await db.sessions.find_one({"_id": ObjectId(session_id)})
    if not session_doc:
        raise HTTPException(status_code=404, detail="Session not found.")

    if not session_doc.get("is_complete"):
        answered = session_doc.get("questions_answered", 0)
        raise HTTPException(
            status_code=400,
            detail=f"Test not complete yet. {answered}/10 questions answered. Keep going!",
        )

    # Build a UserSession object for the insights service
    session_doc["_id"] = str(session_doc["_id"])
    session = UserSession(**session_doc)

    # Generate the plan via LLM
    plan_text, weak_topics = await generate_study_plan(session)

    result = StudyPlan(
        session_id=session_id,
        student_id=session.student_id,
        final_ability=round(session.current_ability, 4),
        total_questions=session.questions_answered,
        total_correct=session.total_correct,
        weak_topics=weak_topics,
        plan=plan_text,
    )

    return result
