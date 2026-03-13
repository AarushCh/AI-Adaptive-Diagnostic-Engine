"""
Database Seeder — Populates the question bank with 20+ GRE-style questions.

Usage:
    python -m scripts.seed

Each question includes: text, options, correct_answer, difficulty (0.1-1.0), topic, tags.
Topics span: Algebra, Vocabulary, Reading Comprehension, Geometry, Data Interpretation.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

settings = get_settings()

QUESTIONS = [
    # ── Algebra (5 questions) ──
    {
        "text": "If 3x + 7 = 22, what is the value of x?",
        "options": ["3", "5", "7", "15"],
        "correct_answer": "5",
        "difficulty": 0.2,
        "topic": "Algebra",
        "tags": ["linear-equations", "basic"],
    },
    {
        "text": "What is the value of x² - 4x + 4 when x = 2?",
        "options": ["0", "2", "4", "8"],
        "correct_answer": "0",
        "difficulty": 0.3,
        "topic": "Algebra",
        "tags": ["quadratic", "substitution"],
    },
    {
        "text": "If f(x) = 2x² + 3x - 5, what is f(-1)?",
        "options": ["-6", "-4", "0", "6"],
        "correct_answer": "-6",
        "difficulty": 0.4,
        "topic": "Algebra",
        "tags": ["functions", "evaluation"],
    },
    {
        "text": "Solve: |2x - 5| = 11. What is the sum of both solutions?",
        "options": ["5", "8", "3", "10"],
        "correct_answer": "5",
        "difficulty": 0.6,
        "topic": "Algebra",
        "tags": ["absolute-value", "equations"],
    },
    {
        "text": "If log₂(x) + log₂(x-2) = 3, what is x?",
        "options": ["4", "2", "6", "8"],
        "correct_answer": "4",
        "difficulty": 0.8,
        "topic": "Algebra",
        "tags": ["logarithms", "advanced"],
    },
    # ── Vocabulary (5 questions) ──
    {
        "text": "Choose the word most nearly opposite in meaning to 'LACONIC'.",
        "options": ["Verbose", "Terse", "Calm", "Quiet"],
        "correct_answer": "Verbose",
        "difficulty": 0.3,
        "topic": "Vocabulary",
        "tags": ["antonyms", "gre-words"],
    },
    {
        "text": "Select the synonym of 'EPHEMERAL'.",
        "options": ["Permanent", "Transient", "Ethereal", "Solid"],
        "correct_answer": "Transient",
        "difficulty": 0.4,
        "topic": "Vocabulary",
        "tags": ["synonyms", "gre-words"],
    },
    {
        "text": "The professor's _______ lecture left the audience confused and disengaged.",
        "options": ["lucid", "abstruse", "cogent", "pellucid"],
        "correct_answer": "abstruse",
        "difficulty": 0.6,
        "topic": "Vocabulary",
        "tags": ["sentence-completion", "context-clues"],
    },
    {
        "text": "Choose the word that best completes: 'Her _______ demeanor belied the turmoil within.'",
        "options": ["agitated", "placid", "querulous", "volatile"],
        "correct_answer": "placid",
        "difficulty": 0.5,
        "topic": "Vocabulary",
        "tags": ["sentence-completion", "contrast"],
    },
    {
        "text": "OBFUSCATE most nearly means:",
        "options": ["Clarify", "Confuse", "Illuminate", "Decorate"],
        "correct_answer": "Confuse",
        "difficulty": 0.7,
        "topic": "Vocabulary",
        "tags": ["definitions", "gre-words"],
    },
    # ── Reading Comprehension (4 questions) ──
    {
        "text": "A passage argues that deforestation leads to biodiversity loss. The author's primary purpose is to:",
        "options": [
            "Advocate for reforestation policies",
            "Describe the economic benefits of logging",
            "Detail the scientific causes of extinction",
            "Compare tropical and temperate forests",
        ],
        "correct_answer": "Advocate for reforestation policies",
        "difficulty": 0.4,
        "topic": "Reading Comprehension",
        "tags": ["main-idea", "inference"],
    },
    {
        "text": "Based on the passage: 'The proliferation of misinformation online has eroded public trust in institutions.' The word 'proliferation' most closely means:",
        "options": ["Decline", "Rapid increase", "Slow growth", "Stagnation"],
        "correct_answer": "Rapid increase",
        "difficulty": 0.3,
        "topic": "Reading Comprehension",
        "tags": ["vocabulary-in-context"],
    },
    {
        "text": "A historian argues that the Industrial Revolution was primarily driven by access to capital, not technological innovation. Which of the following, if true, would most weaken this argument?",
        "options": [
            "Many early factories were self-funded",
            "Key inventions preceded major capital investment",
            "Capital markets expanded in the 19th century",
            "Labor was abundant during this period",
        ],
        "correct_answer": "Key inventions preceded major capital investment",
        "difficulty": 0.7,
        "topic": "Reading Comprehension",
        "tags": ["critical-reasoning", "weaken"],
    },
    {
        "text": "The passage suggests that epigenetic changes can be inherited. The author would most likely agree with which statement?",
        "options": [
            "DNA sequence is the sole determinant of traits",
            "Environmental factors can influence heritable traits",
            "Genetic mutations are always harmful",
            "Evolution occurs only through natural selection",
        ],
        "correct_answer": "Environmental factors can influence heritable traits",
        "difficulty": 0.8,
        "topic": "Reading Comprehension",
        "tags": ["inference", "science-passage"],
    },
    # ── Geometry (3 questions) ──
    {
        "text": "What is the area of a circle with radius 7? (Use π ≈ 22/7)",
        "options": ["154", "44", "49", "22"],
        "correct_answer": "154",
        "difficulty": 0.2,
        "topic": "Geometry",
        "tags": ["circles", "area"],
    },
    {
        "text": "In a right triangle, the legs are 5 and 12. What is the hypotenuse?",
        "options": ["13", "17", "15", "11"],
        "correct_answer": "13",
        "difficulty": 0.3,
        "topic": "Geometry",
        "tags": ["pythagorean-theorem", "triangles"],
    },
    {
        "text": "A regular hexagon has a side length of 6. What is its area?",
        "options": ["54√3", "36√3", "24√3", "72√3"],
        "correct_answer": "54√3",
        "difficulty": 0.7,
        "topic": "Geometry",
        "tags": ["polygons", "advanced"],
    },
    # ── Data Interpretation (3 questions) ──
    {
        "text": "A bar chart shows sales of 120, 150, 90, and 180 for Q1-Q4. What is the average quarterly sales?",
        "options": ["135", "120", "145", "150"],
        "correct_answer": "135",
        "difficulty": 0.2,
        "topic": "Data Interpretation",
        "tags": ["averages", "bar-charts"],
    },
    {
        "text": "If a company's revenue grew from $2M to $2.5M, what is the percentage increase?",
        "options": ["20%", "25%", "50%", "15%"],
        "correct_answer": "25%",
        "difficulty": 0.3,
        "topic": "Data Interpretation",
        "tags": ["percentages", "growth"],
    },
    {
        "text": "A pie chart shows: Marketing 30%, R&D 25%, Operations 35%, Admin 10%. If the total budget is $400K, how much is allocated to R&D and Marketing combined?",
        "options": ["$220K", "$200K", "$240K", "$180K"],
        "correct_answer": "$220K",
        "difficulty": 0.5,
        "topic": "Data Interpretation",
        "tags": ["pie-charts", "combined-analysis"],
    },
]


async def seed():
    """Insert all questions into MongoDB, clearing existing data first."""
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.database_name]

    # Clear existing data
    await db.questions.delete_many({})
    await db.sessions.delete_many({})

    # Insert questions
    result = await db.questions.insert_many(QUESTIONS)
    print(f"✅ Seeded {len(result.inserted_ids)} questions into '{settings.database_name}.questions'")

    # Print summary by topic
    topics = {}
    for q in QUESTIONS:
        topics[q["topic"]] = topics.get(q["topic"], 0) + 1
    print("\n📊 Questions by topic:")
    for topic, count in sorted(topics.items()):
        print(f"   {topic}: {count}")

    # Create indexes for performance
    await db.questions.create_index("difficulty")
    await db.questions.create_index("topic")
    await db.sessions.create_index("student_id")
    print("\n📇 Database indexes created.")

    client.close()
    print("🎓 Database is ready for adaptive testing!")


if __name__ == "__main__":
    asyncio.run(seed())
