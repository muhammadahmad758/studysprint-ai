"""Readiness report — a transparent scoring model, not "AI magic".

Readiness score (0-100) = 60% x average quiz accuracy
                        + 40% x completion

- Average quiz accuracy: mean of per-topic accuracy, over topics that
  have been quizzed at least once. 0 if nothing has been quizzed yet.
- Completion: share of topics that have been quizzed at least once.
- Weakest topics: quizzed topics sorted by accuracy, lowest first;
  never-quizzed topics are listed separately as "not yet attempted".

Because both inputs are percentages, the score is always between 0
and 100. A score of 100 means every topic has been quizzed and every
answer was correct — it measures practice so far, not a guarantee
about the real exam.
"""

from __future__ import annotations

from .quiz import accuracy_by_topic


def build_report(state) -> dict:
    accuracy = accuracy_by_topic(state.attempts)
    topic_names = [t.name for t in state.topics]
    attempted = [name for name in topic_names if name in accuracy]
    completion = (len(attempted) / len(topic_names) * 100) if topic_names else 0.0
    avg_accuracy = (sum(accuracy[n] for n in attempted) / len(attempted)
                    if attempted else 0.0)
    readiness = round(0.6 * avg_accuracy * 100 + 0.4 * completion, 1)
    # "Weakest" means genuinely weak: below 100% accuracy, lowest first.
    # A topic at 100% is not weak, even if it is the only attempted topic.
    weakest = sorted((n for n in attempted if accuracy[n] < 1.0),
                     key=lambda n: (accuracy[n], n))
    return {
        "total_topics": len(topic_names),
        "topics_attempted": len(attempted),
        "completion_pct": round(completion, 1),
        "avg_accuracy_pct": round(avg_accuracy * 100, 1),
        "per_topic_accuracy_pct": {n: round(accuracy[n] * 100, 1)
                                   for n in sorted(accuracy)},
        "weakest_topics": weakest,
        "not_attempted": [n for n in topic_names if n not in accuracy],
        "readiness_score": readiness,
        "formula": ("readiness = 0.6 x average accuracy (%) "
                    "+ 0.4 x completion (%)"),
    }
