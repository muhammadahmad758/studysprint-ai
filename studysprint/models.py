"""Data models for StudySprint AI.

Every model is a plain dataclass with ``to_dict`` / ``from_dict`` helpers,
so the whole app state can be stored as one JSON file (see storage.py).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date


def parse_date(text: str) -> date:
    """Parse a YYYY-MM-DD date, raising ValueError on bad input."""
    year, month, day = (int(part) for part in text.split("-"))
    return date(year, month, day)


@dataclass
class Topic:
    """One subject/topic the user wants to study before an exam."""

    name: str
    difficulty: int  # 1 (easy) to 5 (hard)
    exam_date: str  # YYYY-MM-DD

    def __post_init__(self) -> None:
        if not 1 <= self.difficulty <= 5:
            raise ValueError("difficulty must be between 1 and 5")
        parse_date(self.exam_date)  # validates the format

    def days_left(self, today: date) -> int:
        return (parse_date(self.exam_date) - today).days

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Topic":
        return cls(name=data["name"], difficulty=int(data["difficulty"]),
                   exam_date=data["exam_date"])


@dataclass
class Card:
    """One flashcard belonging to a topic."""

    id: str
    topic: str
    question: str
    answer: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Card":
        return cls(id=data["id"], topic=data["topic"],
                   question=data["question"], answer=data["answer"])


@dataclass
class Attempt:
    """One quiz answer, recorded so per-topic accuracy can be computed."""

    topic: str
    correct: bool
    date: str  # YYYY-MM-DD

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Attempt":
        return cls(topic=data["topic"], correct=bool(data["correct"]),
                   date=data["date"])


@dataclass
class Review:
    """A spaced-repetition item: a card that becomes due on ``due_date``.

    ``stage`` is an index into repetition.INTERVALS. A correct recall moves
    the card one stage forward; a wrong answer sends it back to stage 0.
    """

    card_id: str
    topic: str
    due_date: str  # YYYY-MM-DD
    stage: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Review":
        return cls(card_id=data["card_id"], topic=data["topic"],
                   due_date=data["due_date"], stage=int(data.get("stage", 0)))


@dataclass
class State:
    """The whole app state — everything stored in the JSON data file."""

    topics: list = field(default_factory=list)
    cards: list = field(default_factory=list)
    attempts: list = field(default_factory=list)
    reviews: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "topics": [t.to_dict() for t in self.topics],
            "cards": [c.to_dict() for c in self.cards],
            "attempts": [a.to_dict() for a in self.attempts],
            "reviews": [r.to_dict() for r in self.reviews],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "State":
        return cls(
            topics=[Topic.from_dict(t) for t in data.get("topics", [])],
            cards=[Card.from_dict(c) for c in data.get("cards", [])],
            attempts=[Attempt.from_dict(a) for a in data.get("attempts", [])],
            reviews=[Review.from_dict(r) for r in data.get("reviews", [])],
        )

    def next_card_id(self) -> str:
        numbers = [int(c.id[1:]) for c in self.cards
                   if c.id.startswith("c") and c.id[1:].isdigit()]
        return f"c{max(numbers, default=0) + 1}"
