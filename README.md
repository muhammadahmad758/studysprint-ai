# StudySprint AI

A command-line study coach. Add topics with exam dates, get a day-by-day
study plan, quiz yourself with flashcards, review on a spaced schedule,
and check your readiness score.

No external packages, no API keys, no internet. Data lives in one local
JSON file. The "AI" here is honest: a transparent priority formula and a
spaced-repetition schedule — not a language model.

## Features

- Topics with difficulty (1–5) and exam dates
- Smart daily plan from a deterministic, explainable priority score
- Flashcards and quizzes (case-insensitive answer checking)
- Spaced repetition: reviews at +1, +3, +7, +14 days
- Readiness report: completion, per-topic accuracy, readiness 0–100

## Run

```bash
python -m studysprint add-topic --name "Biology" --difficulty 4 --exam 2026-11-10
python -m studysprint add-card --topic "Biology" --question "What is DNA?" --answer "Genetic material"
python -m studysprint plan
python -m studysprint quiz --topic "Biology"
python -m studysprint review
python -m studysprint report
```

Use `--data myfile.json` before the command to use a different data file.

## Example session

```bash
$ python -m studysprint --data demo.json add-topic --name "Biology" --difficulty 4 --exam 2026-11-10
Added topic 'Biology' (difficulty 4/5, exam 2026-11-10).
$ python -m studysprint --data demo.json add-card --topic "Biology" --question "What is DNA?" --answer "Genetic material"
Added card c1 to 'Biology': What is DNA?
$ python -m studysprint --data demo.json plan --date 2026-10-28
2026-10-28 | Biology (60 min, priority 13.5)
  Biology: difficulty 4/5, exam in 13 day(s), not quizzed yet, so weakness is counted as average -> priority 13.5
  ... (one session per day up to the exam)
$ python -m studysprint --data demo.json quiz --topic "Biology" --answers "Genetic material"
Correct!
Score: 1/1 for 'Biology'.
$ python -m studysprint --data demo.json report
Topics: 1 (1 attempted, completion 100.0%)
Average accuracy: 100.0%
  Biology: 100.0%
Readiness score: 100.0/100
Formula: readiness = 0.6 x average accuracy (%) + 0.4 x completion (%)
```

Try the demo data: copy `examples/sample_data.json` to a data file and
run the commands above with `--data` pointing at the copy.

## Structure

```
studysprint/
  models.py      data types (Topic, Card, Attempt, Review, State)
  storage.py     JSON load/save with atomic writes
  planner.py     priority score and day-by-day plan
  quiz.py        answer checking and per-topic accuracy
  repetition.py  spaced-repetition schedule (+1/+3/+7/+14 days)
  report.py      readiness score and weakest topics
  cli.py         argparse commands
tests/           unittest suite (run: python -m unittest discover -s tests -v)
examples/        sample_data.json — demo topics and cards
```

## Tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT — see `LICENSE`.
