"""Smart daily plan: a deterministic, explainable priority score.

Priority = difficulty points + urgency points + weakness points

- Difficulty points: difficulty x 2  (a difficulty-5 topic scores 10).
- Urgency points: from days left until the exam —
  overdue 10, <=3 days 8, <=7 days 5, <=14 days 3, otherwise 1.
- Weakness points: (1 - past quiz accuracy) x 5 for topics already quizzed,
  or 2.5 for a topic never quizzed (unknown, so treated as middling).

Nothing here is machine learning and nothing is random: the same topics,
quiz history and date always produce the same plan, and every score can
be explained in one sentence (see ``explain``).
"""

from __future__ import annotations

from datetime import date, timedelta

from .models import Topic, parse_date


def urgency_points(days_left: int) -> int:
    if days_left <= 0:
        return 10
    if days_left <= 3:
        return 8
    if days_left <= 7:
        return 5
    if days_left <= 14:
        return 3
    return 1


def priority(topic: Topic, accuracy: float | None, today: date) -> float:
    """Priority score for one topic. ``accuracy`` is None if never quizzed."""
    difficulty_points = topic.difficulty * 2
    urgency = urgency_points(topic.days_left(today))
    weakness = 2.5 if accuracy is None else (1.0 - accuracy) * 5
    return difficulty_points + urgency + weakness


def explain(topic: Topic, accuracy: float | None, today: date) -> str:
    """One plain-English sentence explaining a topic's priority score."""
    days = topic.days_left(today)
    if accuracy is None:
        weak = "not quizzed yet, so weakness is counted as average"
    else:
        weak = f"past quiz accuracy {accuracy:.0%}"
    return (f"{topic.name}: difficulty {topic.difficulty}/5, exam in "
            f"{days} day(s), {weak} -> priority {priority(topic, accuracy, today):.1f}")


def ranked_topics(topics: list, accuracy_by_topic: dict, today: date) -> list:
    """Topics sorted highest priority first (ties broken by topic name)."""
    return sorted(
        topics,
        key=lambda t: (-priority(t, accuracy_by_topic.get(t.name), today), t.name),
    )


def daily_plan(topics: list, accuracy_by_topic: dict, today: date) -> list:
    """One study session per day from ``today`` to the latest exam date.

    Sessions cycle through topics in priority order, so the hardest,
    most urgent, weakest topic is always studied first and every topic
    keeps coming back until its exam. Suggested minutes scale with
    difficulty: difficulty x 15 minutes.
    """
    if not topics:
        return []
    ranked = ranked_topics(topics, accuracy_by_topic, today)
    last_exam = max(parse_date(t.exam_date) for t in topics)
    total_days = max(1, (last_exam - today).days + 1)
    plan = []
    for offset in range(total_days):
        topic = ranked[offset % len(ranked)]
        plan.append({
            "date": (today + timedelta(days=offset)).isoformat(),
            "topic": topic.name,
            "priority": round(priority(topic, accuracy_by_topic.get(topic.name), today), 1),
            "minutes": topic.difficulty * 15,
            "reason": explain(topic, accuracy_by_topic.get(topic.name), today),
        })
    return plan
