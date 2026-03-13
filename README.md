# 🧠 AI-Driven Adaptive Diagnostic Engine

A **1-Dimension Adaptive Testing Prototype** built with FastAPI, MongoDB, and LLM integration. The system dynamically selects GRE-style questions based on student performance using Item Response Theory (IRT), then generates a personalized study plan powered by AI.

---

## 🚀 How to Run

### Prerequisites
- **Python 3.10+**
- **MongoDB** (local via [MongoDB Compass](https://www.mongodb.com/products/compass) or Atlas)

### Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd HighScores-AI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
# Edit .env with your MongoDB URI and OpenRouter API Key
cp .env.example .env

# 4. Seed the question bank (20+ GRE-style questions)
python -m scripts.seed

# 5. Start the server
uvicorn app.main:app --reload
```

The API will be live at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive Swagger UI.

---

## 📐 Adaptive Algorithm Logic (IRT)

This system implements the **1-Parameter Logistic Model (Rasch Model)** from Item Response Theory:

### Probability Function
```
P(correct | θ, b) = 1 / (1 + exp(-a × (θ - b)))
```
- **θ (theta)**: Student's estimated ability (0.0 – 1.0)
- **b**: Question difficulty (0.1 – 1.0)
- **a**: Discrimination parameter (fixed at 4.0)

### Question Selection
Uses **Maximum Fisher Information** — selects the question whose difficulty is closest to the student's current ability. This is the question where P(correct) ≈ 0.5, providing the most diagnostic information.

### Ability Update
After each response, the ability estimate is updated via a gradient step:
```
θ_new = θ_old + lr × (response - P(correct))
```
- `response` = 1 (correct) or 0 (incorrect)
- `lr` = 0.4 / √(n + 1) — decaying learning rate for convergence
- The estimate is clamped within `[0.05, 0.95]`

### Flow
1. Student starts at **ability = 0.5** (baseline).
2. Correct answer → ability **increases** → harder question selected.
3. Incorrect answer → ability **decreases** → easier question selected.
4. After **10 questions**, the test completes and an AI study plan is generated.

---

## 📡 API Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/session` | Start a new test session |
| `GET` | `/api/next-question?session_id=<id>` | Get next adaptive question |
| `POST` | `/api/submit-answer` | Submit an answer |
| `GET` | `/api/session/<id>` | View session details |
| `GET` | `/api/session/<id>/plan` | Get AI-generated study plan |

### Example Flow

```bash
# 1. Create a session
POST /api/session
Body: { "student_id": "student_42" }

# 2. Get next question
GET /api/next-question?session_id=<session_id>

# 3. Submit answer
POST /api/submit-answer
Body: { "session_id": "<id>", "question_id": "<qid>", "selected_answer": "5" }

# 4. Repeat steps 2-3 for 10 questions

# 5. Get study plan
GET /api/session/<session_id>/plan
```

---

## 🏗 Project Structure

```
HighScores-AI/
├── app/
│   ├── main.py                    # FastAPI entry point & lifecycle
│   ├── config.py                  # Settings from .env
│   ├── models/
│   │   └── schemas.py             # Pydantic data models
│   ├── routes/
│   │   ├── quiz.py                # Session, question, answer endpoints
│   │   └── insights.py            # AI study plan endpoint
│   ├── services/
│   │   ├── adaptive_logic.py      # IRT algorithm (core math)
│   │   └── llm_insights.py        # OpenRouter LLM integration
│   └── utils/
│       └── database.py            # Async MongoDB connection manager
├── scripts/
│   └── seed.py                    # Database seeder (20 GRE questions)
├── .env                           # Environment variables
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🤖 AI Log

### Tools Used
- **Cursor AI / Claude** — Used to accelerate architecture scaffolding, write the IRT implementation with correct mathematical formulation, and generate the 20 diverse GRE-style seed questions.

### What AI Was Great At
- Generating boilerplate FastAPI route patterns quickly.
- Structuring the Pydantic models with proper validation.
- Drafting the question bank across multiple GRE topics.

### What Required Human Guidance
- Tuning the IRT discrimination parameter (a=4.0) and learning rate (0.4) for smooth convergence — the AI's initial suggestions were too aggressive.
- Debugging the httpx/OpenAI client compatibility issue that caused a `proxies` keyword error.
- Ensuring the MongoDB schema design optimized for the adaptive query pattern (indexing on `difficulty`).

---

## 📊 Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | FastAPI (Python) |
| Database | MongoDB (Motor async driver) |
| AI/LLM | OpenRouter API (nvidia/nemotron free) |
| Algorithm | IRT 1PL Rasch Model |
| Validation | Pydantic v2 |
