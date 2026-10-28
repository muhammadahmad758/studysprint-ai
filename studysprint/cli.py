"""Command-line interface for StudySprint AI.

Run:  python -m studysprint <command> [options]

Global option: --data PATH  (default: studysprint_data.json in the
current folder). Every command accepts it before the subcommand, e.g.
``python -m studysprint --data my.json plan``.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date

from . import repetition
from .models import Attempt, Card, Topic, parse_date
from .planner import daily_plan, explain, ranked_topics
from .quiz import accuracy_by_topic, is_correct
from .report import build_report
from .storage import DEFAULT_DATA_FILE, load, save


def _today(text: str | None) -> date:
    return parse_date(text) if text else date.today()


def cmd_add_topic(args, state) -> None:
    if any(t.name == args.name for t in state.topics):
        print(f"Topic '{args.name}' already exists.")
        return
    state.topics.append(Topic(args.name, args.difficulty, args.exam))
    print(f"Added topic '{args.name}' (difficulty {args.difficulty}/5, "
          f"exam {args.exam}).")


def cmd_list_topics(args, state) -> None:
    if not state.topics:
        print("No topics yet. Add one with: add-topic --name ... --difficulty ... --exam YYYY-MM-DD")
        return
    accuracy = accuracy_by_topic(state.attempts)
    for topic in ranked_topics(state.topics, accuracy, _today(args.date)):
        acc = accuracy.get(topic.name)
        acc_text = f"{acc:.0%} accuracy" if acc is not None else "not quizzed yet"
        print(f"- {topic.name} | difficulty {topic.difficulty}/5 | "
              f"exam {topic.exam} | {acc_text}")
        print(f"  {explain(topic, acc, _today(args.date))}")


def cmd_add_card(args, state) -> None:
    if not any(t.name == args.topic for t in state.topics):
        print(f"Unknown topic '{args.topic}'. Add it first with add-topic.")
        return
    card = Card(state.next_card_id(), args.topic, args.question, args.answer)
    state.cards.append(card)
    print(f"Added card {card.id} to '{args.topic}': {args.question}")


def cmd_list_cards(args, state) -> None:
    cards = [c for c in state.cards if args.topic is None or c.topic == args.topic]
    if not cards:
        print("No cards yet.")
        return
    for card in cards:
        print(f"{card.id} [{card.topic}] Q: {card.question} | A: {card.answer}")


def cmd_plan(args, state) -> None:
    today = _today(args.date)
    plan = daily_plan(state.topics, accuracy_by_topic(state.attempts), today)
    if not plan:
        print("No topics yet. Add one first.")
        return
    for session in plan:
        print(f"{session['date']} | {session['topic']} "
              f"({session['minutes']} min, priority {session['priority']})")
        print(f"  {session['reason']}")


def cmd_quiz(args, state) -> None:
    cards = [c for c in state.cards if c.topic == args.topic]
    if not cards:
        print(f"No cards for topic '{args.topic}'. Add some with add-card.")
        return
    today = _today(args.date)
    scripted = args.answers.split("|") if args.answers is not None else None
    correct_count = 0
    for index, card in enumerate(cards):
        if scripted is not None:
            given = scripted[index] if index < len(scripted) else ""
            print(f"Q: {card.question}\nA (scripted): {given}")
        else:
            given = input(f"Q: {card.question}\nYour answer: ")
        ok = is_correct(card, given)
        correct_count += ok
        print("Correct!" if ok else f"Not quite. Answer: {card.answer}")
        state.attempts.append(Attempt(args.topic, ok, today.isoformat()))
        existing = next((r for r in state.reviews if r.card_id == card.id), None)
        updated = (repetition.next_review(existing, ok, today) if existing
                   else repetition.new_review(card.id, args.topic, today))
        if existing:
            state.reviews.remove(existing)
        state.reviews.append(updated)
    print(f"Score: {correct_count}/{len(cards)} for '{args.topic}'.")


def cmd_review(args, state) -> None:
    today = _today(args.date)
    due = repetition.due_today(state.reviews, today)
    if not due:
        print(f"Nothing due for review on {today.isoformat()}.")
        return
    cards = {c.id: c for c in state.cards}
    for item in due:
        card = cards.get(item.card_id)
        question = card.question if card else "(card removed)"
        print(f"- {item.topic}: {question} (due {item.due_date}, stage {item.stage})")


def cmd_report(args, state) -> None:
    report = build_report(state)
    print(f"Topics: {report['total_topics']} "
          f"({report['topics_attempted']} attempted, "
          f"completion {report['completion_pct']}%)")
    print(f"Average accuracy: {report['avg_accuracy_pct']}%")
    for name, pct in report["per_topic_accuracy_pct"].items():
        print(f"  {name}: {pct}%")
    if report["weakest_topics"]:
        print("Weakest topics: " + ", ".join(report["weakest_topics"]))
    if report["not_attempted"]:
        print("Not yet attempted: " + ", ".join(report["not_attempted"]))
    print(f"Readiness score: {report['readiness_score']}/100")
    print(f"Formula: {report['formula']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="studysprint",
        description="StudySprint AI — a command-line study coach.")
    parser.add_argument("--data", default=DEFAULT_DATA_FILE,
                        help="JSON data file (default: %(default)s)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add-topic", help="Add a topic with difficulty and exam date.")
    p.add_argument("--name", required=True)
    p.add_argument("--difficulty", type=int, required=True, choices=range(1, 6))
    p.add_argument("--exam", required=True, help="Exam date YYYY-MM-DD")
    p.set_defaults(func=cmd_add_topic)

    p = sub.add_parser("list-topics", help="List topics in priority order.")
    p.add_argument("--date", help="Pretend today is YYYY-MM-DD (for testing)")
    p.set_defaults(func=cmd_list_topics)

    p = sub.add_parser("add-card", help="Add a flashcard to a topic.")
    p.add_argument("--topic", required=True)
    p.add_argument("--question", required=True)
    p.add_argument("--answer", required=True)
    p.set_defaults(func=cmd_add_card)

    p = sub.add_parser("list-cards", help="List flashcards, optionally for one topic.")
    p.add_argument("--topic")
    p.set_defaults(func=cmd_list_cards)

    p = sub.add_parser("plan", help="Show the day-by-day study plan.")
    p.add_argument("--date", help="Start date YYYY-MM-DD (default: today)")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("quiz", help="Quiz yourself on a topic's cards.")
    p.add_argument("--topic", required=True)
    p.add_argument("--answers",
                   help="Pipe-separated scripted answers, e.g. 'a|b' (for tests/scripts)")
    p.add_argument("--date", help="Quiz date YYYY-MM-DD (default: today)")
    p.set_defaults(func=cmd_quiz)

    p = sub.add_parser("review", help="List reviews due today.")
    p.add_argument("--date", help="Check date YYYY-MM-DD (default: today)")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser("report", help="Show completion, accuracy and readiness.")
    p.set_defaults(func=cmd_report)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        state = load(args.data)
        args.func(args, state)
        save(state, args.data)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
