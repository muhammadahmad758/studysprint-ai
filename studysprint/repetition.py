"""Spaced repetition: reviews at +1, +3, +7, +14 days.

A card starts at stage 0. Each correct recall moves it one stage
forward (so the next gap grows: 1, then 3, then 7, then 14 days, and it
stays at 14 days after that). A wrong answer resets it to stage 0,
so a weak card comes back tomorrow. This is the classic Leitner-style
schedule, implemented with plain dates — no learning algorithm.
"""

from __future__ import annotations

from datetime import date, timedelta

from .models import Review, parse_date

INTERVALS = [1, 3, 7, 14]


def next_review(review: Review, correct: bool, today: date) -> Review:
    """Return the updated review after answering on ``today``."""
    if correct:
        stage = min(review.stage + 1, len(INTERVALS) - 1)
    else:
        stage = 0
    gap = INTERVALS[stage]
    return Review(card_id=review.card_id, topic=review.topic,
                  due_date=(today + timedelta(days=gap)).isoformat(),
                  stage=stage)


def new_review(card_id: str, topic: str, today: date) -> Review:
    """First review for a newly quizzed card: due tomorrow (stage 0 gap)."""
    return Review(card_id=card_id, topic=topic,
                  due_date=(today + timedelta(days=INTERVALS[0])).isoformat(),
                  stage=0)


def due_today(reviews: list, today: date) -> list:
    """Reviews whose due date is today or earlier, oldest first."""
    due = [r for r in reviews if parse_date(r.due_date) <= today]
    return sorted(due, key=lambda r: (r.due_date, r.topic))
