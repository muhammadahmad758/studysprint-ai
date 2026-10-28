# Learning Notes — StudySprint AI

Simple-English notes so I can explain this project in an interview.

## The idea in one sentence

Turn a list of topics and exam dates into a daily study plan, then use
quizzes and spaced reviews to keep weak topics coming back until they
stick.

## Module by module

- **models.py** — The data shapes, built with Python `dataclasses`
  (a short way to write a class that mainly holds data). `Topic` holds a
  name, difficulty 1–5 and exam date. `Card` is one flashcard. `Attempt`
  records one quiz answer so accuracy can be counted later. `Review`
  says when a card is next due. `State` is everything together, and
  every model can turn itself into a dictionary (`to_dict`) and back
  (`from_dict`) — that is how JSON storage works.

- **storage.py** — Loads and saves the JSON file. Writes are *atomic*:
  the new data goes to a temporary file first, then replaces the old
  file in one step. If the program crashes mid-save, the old file is
  still intact instead of half-written.

- **planner.py** — The "smart" plan. Priority = difficulty points
  (difficulty x 2) + urgency points (closer exam = more points) +
  weakness points ((1 - accuracy) x 5). A topic never quizzed counts as
  average weakness (2.5). Topics are sorted by this score, then dealt
  out one per day up to the latest exam. It is deterministic: same
  input, same plan, every time. I can explain any day's choice in one
  sentence using `explain()`.

- **quiz.py** — Answers are normalised (lowercase, trimmed, extra spaces
  collapsed) and compared exactly. So "Photosynthesis" and
  "  photosynthesis " both count as correct, but a wrong word does not.
  `accuracy_by_topic` counts correct answers per topic.

- **repetition.py** — Spaced repetition, the classic Leitner idea: a
  card reviewed correctly waits longer next time (+1, then +3, +7, +14
  days); a wrong answer sends it back to tomorrow. Reviewing just
  before you would forget is more effective than re-reading everything
  every day.

- **report.py** — Readiness = 0.6 x average accuracy + 0.4 x completion.
  Completion is the share of topics quizzed at least once. This is a
  scoring model I chose and documented — it measures practice so far,
  it is not a prediction or a guarantee about the real exam.

- **cli.py** — The command line, built with `argparse` (Python's
  built-in argument parser). Each subcommand (`add-topic`, `plan`,
  `quiz`, ...) is one function. `__main__.py` exists only so
  `python -m studysprint` works.

## Key ideas to mention in an interview

1. Separation of concerns: planning, quizzing, repetition and reporting
   are separate modules, so each can be tested alone.
2. Deterministic, explainable scoring instead of a black box.
3. Atomic file writes so user data is never corrupted by a crash.
4. Standard library only — no dependencies to install or break.
5. Tested with `unittest`: planner ordering, repetition intervals, quiz
   scoring, storage round-trip, readiness bounds.
