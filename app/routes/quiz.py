"""
Quiz Routes — Core adaptive test endpoints.

Endpoints:
    POST /api/session       — Start a new adaptive test session.
    GET  /api/next-question  — Get the next optimal question for a session.
    POST /api/submit-answer  — Submit an answer and get updated ability.
    GET  /api/session/{id}   — Retrieve session details.
"""

from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from app.utils.database import Database
from app.models.schemas import SessionCreate, AnswerSubmit, AnswerRecord
from app.services.adaptive_logic import select_next_question, update_ability

router = APIRouter(prefix="/api", tags=["Quiz"])


def _serialize_doc(doc: dict) -> dict:
    """Convert MongoDB ObjectId to string for JSON serialization."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.post("/session", status_code=status.HTTP_201_CREATED)
async def create_session(body: SessionCreate):
    """
    Start a new adaptive test session.

    Initializes the student at baseline ability of 0.5.
    """
    db = Database.get_db()

    session_doc = {
        "student_id": body.student_id,
        "current_ability": 0.5,
        "questions_answered": 0,
        "total_correct": 0,
        "history": [],
        "is_complete": False,
    }

    result = await db.sessions.insert_one(session_doc)
    session_doc["_id"] = str(result.inserted_id)

    return {
        "message": "Session created. Begin your adaptive test!",
        "session": session_doc,
    }


@router.get("/next-question")
async def get_next_question(session_id: str):
    """
    Retrieve the next optimal question for the student.

    Uses Maximum Fisher Information to select the question whose
    difficulty is closest to the student's current ability estimate.
    """
    db = Database.get_db()

    # Validate session
    session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session.get("is_complete"):
        raise HTTPException(
            status_code=400,
            detail="Test is complete. Retrieve your study plan at GET /api/session/{id}/plan.",
        )

    # Get answered question IDs
    answered_ids = [record["question_id"] for record in session.get("history", [])]

    # Get all questions from the bank
    questions = await db.questions.find().to_list(length=100)
    if not questions:
        raise HTTPException(status_code=500, detail="Question bank is empty. Seed the database first.")

    # Select the optimal next question
    next_q = select_next_question(
        ability=session["current_ability"],
        available_questions=questions,
        answered_ids=answered_ids,
    )

    if next_q is None:
        raise HTTPException(status_code=400, detail="No more unanswered questions available.")

    return {
        "question": {
            "id": str(next_q["_id"]),
            "text": next_q["text"],
            "options": next_q["options"],
            "topic": next_q["topic"],
            "difficulty": next_q["difficulty"],
        },
        "current_ability": round(session["current_ability"], 4),
        "questions_answered": session["questions_answered"],
    }


@router.post("/submit-answer")
async def submit_answer(body: AnswerSubmit):
    """
    Submit an answer and update the student's ability estimate.

    Applies IRT-based ability update and marks the session complete
    after 10 questions.
    """
    db = Database.get_db()

    # Validate session
    session = await db.sessions.find_one({"_id": ObjectId(body.session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session.get("is_complete"):
        raise HTTPException(status_code=400, detail="Test is already complete.")

    # Validate question
    question = await db.questions.find_one({"_id": ObjectId(body.question_id)})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found.")

    # Check if already answered
    answered_ids = [r["question_id"] for r in session.get("history", [])]
    if body.question_id in answered_ids:
        raise HTTPException(status_code=400, detail="Question already answered in this session.")

    # Evaluate answer
    is_correct = body.selected_answer.strip().lower() == question["correct_answer"].strip().lower()

    # Update ability using IRT
    new_ability = update_ability(
        current_ability=session["current_ability"],
        difficulty=question["difficulty"],
        is_correct=is_correct,
        questions_answered=session["questions_answered"],
    )

    # Build history record
    record = AnswerRecord(
        question_id=body.question_id,
        question_text=question["text"],
        topic=question["topic"],
        difficulty=question["difficulty"],
        selected_answer=body.selected_answer,
        correct_answer=question["correct_answer"],
        is_correct=is_correct,
    )

    # Update session in MongoDB
    new_count = session["questions_answered"] + 1
    new_correct = session["total_correct"] + (1 if is_correct else 0)
    is_complete = new_count >= 10

    await db.sessions.update_one(
        {"_id": ObjectId(body.session_id)},
        {
            "$set": {
                "current_ability": new_ability,
                "questions_answered": new_count,
                "total_correct": new_correct,
                "is_complete": is_complete,
            },
            "$push": {"history": record.model_dump()},
        },
    )

    response = {
        "is_correct": is_correct,
        "correct_answer": question["correct_answer"],
        "previous_ability": round(session["current_ability"], 4),
        "new_ability": round(new_ability, 4),
        "questions_answered": new_count,
        "is_complete": is_complete,
    }

    if is_complete:
        response["message"] = (
            "🎉 Test complete! Retrieve your personalized study plan at "
            f"GET /api/session/{body.session_id}/plan"
        )
    else:
        response["message"] = (
            f"{'✅ Correct!' if is_correct else '❌ Incorrect.'} "
            f"Ability updated: {session['current_ability']:.4f} → {new_ability:.4f}"
        )

    return response


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Retrieve session details by ID."""
    db = Database.get_db()

    session = await db.sessions.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    return _serialize_doc(session)
