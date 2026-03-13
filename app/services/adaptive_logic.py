"""
Adaptive Testing Logic based on Item Response Theory (IRT).

Uses the 1-Parameter Logistic (Rasch) Model:
    P(correct | ability, difficulty) = 1 / (1 + exp(-a * (ability - difficulty)))

- 'ability' (theta): The student's estimated proficiency (0.0 to 1.0).
- 'difficulty' (b): The question's difficulty parameter (0.1 to 1.0).
- 'a': Discrimination parameter (fixed at 4.0 for sharper probability curves).

Question Selection Strategy:
    Select the question whose difficulty is closest to the student's current
    ability estimate. This maximizes Fisher Information, meaning each question
    provides the most diagnostic value about the student's true ability.

Ability Update Rule:
    After each response, the ability is adjusted via a simple gradient step:
        theta_new = theta_old + learning_rate * (response - P(correct))
    where response = 1 if correct, 0 if incorrect.
    The learning rate decreases as more questions are answered (1 / sqrt(n+1)),
    ensuring the estimate stabilizes over time.
"""

import math
from typing import List, Dict, Any, Optional


# --- IRT Constants ---
DISCRIMINATION = 4.0     # Controls steepness of the probability curve
BASE_LEARNING_RATE = 0.4  # Initial step size for ability updates
MIN_ABILITY = 0.05        # Floor for ability estimate
MAX_ABILITY = 0.95        # Ceiling for ability estimate


def irt_probability(ability: float, difficulty: float) -> float:
    """
    Calculate the probability of a correct response using the 1PL (Rasch) model.

    P(correct) = 1 / (1 + exp(-a * (theta - b)))

    Args:
        ability: Student's current ability estimate (theta).
        difficulty: Question difficulty parameter (b).

    Returns:
        Probability of answering correctly (0.0 to 1.0).
    """
    exponent = -DISCRIMINATION * (ability - difficulty)
    # Clamp to prevent overflow
    exponent = max(-10.0, min(10.0, exponent))
    return 1.0 / (1.0 + math.exp(exponent))


def select_next_question(
    ability: float,
    available_questions: List[Dict[str, Any]],
    answered_ids: List[str],
) -> Optional[Dict[str, Any]]:
    """
    Select the optimal next question using Maximum Fisher Information.

    The question whose difficulty is closest to the student's current ability
    provides the most information about their true level.

    Args:
        ability: The student's current estimated ability.
        available_questions: List of question dicts from the database.
        answered_ids: List of question IDs the student has already answered.

    Returns:
        The best question dict, or None if no unanswered questions remain.
    """
    # Filter out already-answered questions
    unanswered = [
        q for q in available_questions
        if str(q["_id"]) not in answered_ids
    ]

    if not unanswered:
        return None

    # Find the question with difficulty closest to ability (maximizes information)
    best_question = min(
        unanswered,
        key=lambda q: abs(q["difficulty"] - ability)
    )

    return best_question


def update_ability(
    current_ability: float,
    difficulty: float,
    is_correct: bool,
    questions_answered: int,
) -> float:
    """
    Update the student's ability estimate after answering a question.

    Uses a gradient-descent-inspired step:
        theta_new = theta_old + lr * (response - P(correct))

    The learning rate decays as: lr = BASE_LEARNING_RATE / sqrt(n + 1)
    This ensures large initial adjustments and gradual stabilization.

    Args:
        current_ability: Current ability estimate (theta).
        difficulty: The difficulty of the answered question.
        is_correct: Whether the student answered correctly.
        questions_answered: Total questions answered so far (for LR decay).

    Returns:
        Updated ability estimate, clamped within [MIN_ABILITY, MAX_ABILITY].
    """
    response = 1.0 if is_correct else 0.0
    p_correct = irt_probability(current_ability, difficulty)

    # Decaying learning rate for convergence
    learning_rate = BASE_LEARNING_RATE / math.sqrt(questions_answered + 1)

    # Gradient step: positive if surprising correct, negative if surprising incorrect
    new_ability = current_ability + learning_rate * (response - p_correct)

    # Clamp to valid range
    return max(MIN_ABILITY, min(MAX_ABILITY, new_ability))
