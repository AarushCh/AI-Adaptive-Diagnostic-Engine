"""
AI-Driven Adaptive Diagnostic Engine — FastAPI Application Entry Point.

This application implements a 1-Dimension Adaptive Testing system using
Item Response Theory (IRT) to dynamically adjust question difficulty based
on student performance.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.utils.database import Database
from app.routes import quiz, insights


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle: connect/disconnect MongoDB."""
    await Database.connect()
    yield
    await Database.disconnect()


app = FastAPI(
    title="AI-Driven Adaptive Diagnostic Engine",
    description=(
        "A 1-Dimension Adaptive Testing Prototype using IRT (Item Response Theory) "
        "to dynamically select questions and estimate student ability. "
        "Includes AI-generated personalized study plans via LLM integration."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Register route modules
app.include_router(quiz.router)
app.include_router(insights.router)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Adaptive Diagnostic Engine",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/session": "Start a new test session",
            "GET /api/next-question?session_id=": "Get next adaptive question",
            "POST /api/submit-answer": "Submit an answer",
            "GET /api/session/{id}": "View session details",
            "GET /api/session/{id}/plan": "Get AI study plan (after 10 questions)",
        },
    }
