"""Flashcards and quizzes.

Answers are compared case-insensitively after trimming whitespace and
collapsing repeated spaces, so "  Photosynthesis " matches
"photosynthesis". Scoring is exact-match on that normalised form —
this is a simple, honest check, not fuzzy grading.
"""

from __future__ import annotations

import re

from .models import Card


def normalise(answer: str) -> str:
    return re.sub(r"\s+", " ", answer.strip().lower())


def is_correct(card: Card, given: str) -> bool:
    return normalise(given) == normalise(card.answer)


def score(cards: list, answers: list) -> tuple:
    """Score parallel lists of cards and given answers.

    Returns (correct_count, total, per_card_results) where each result is
    (card, given_answer, was_correct).
    """
    results = [(card, given, is_correct(card, given))
               for card, given in zip(cards, answers)]
    correct = sum(1 for _, _, ok in results if ok)
    return correct, len(results), results


def accuracy_by_topic(attempts: list) -> dict:
    """Per-topic accuracy (0.0-1.0) for topics with at least one attempt."""
    totals: dict = {}
    correct: dict = {}
    for attempt in attempts:
        totals[attempt.topic] = totals.get(attempt.topic, 0) + 1
        if attempt.correct:
            correct[attempt.topic] = correct.get(attempt.topic, 0) + 1
    return {topic: correct.get(topic, 0) / total
            for topic, total in totals.items()}
