from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Question(BaseModel):
    """Represents a single test question in the question bank."""

    id: Optional[str] = Field(default=None, alias="_id")
    text: str
    options: List[str]
    correct_answer: str
    difficulty: float = Field(ge=0.1, le=1.0, description="Difficulty from 0.1 (easy) to 1.0 (hard)")
    topic: str
    tags: List[str] = []

    class Config:
        populate_by_name = True


class AnswerRecord(BaseModel):
    """Tracks a single answered question within a session."""

    question_id: str
    question_text: str
    topic: str
    difficulty: float
    selected_answer: str
    correct_answer: str
    is_correct: bool


class SessionCreate(BaseModel):
    """Request body to create a new test session."""

    student_id: str


class AnswerSubmit(BaseModel):
    """Request body to submit an answer."""

    session_id: str
    question_id: str
    selected_answer: str


class UserSession(BaseModel):
    """Tracks a student's adaptive test session."""

    id: Optional[str] = Field(default=None, alias="_id")
    student_id: str
    current_ability: float = 0.5
    questions_answered: int = 0
    total_correct: int = 0
    history: List[AnswerRecord] = []
    is_complete: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class StudyPlan(BaseModel):
    """The AI-generated personalized study plan."""

    session_id: str
    student_id: str
    final_ability: float
    total_questions: int
    total_correct: int
    weak_topics: List[str]
    plan: str