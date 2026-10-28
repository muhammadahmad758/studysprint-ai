import unittest

from studysprint.models import Attempt, State, Topic
from studysprint.report import build_report


def make_state(attempts):
    return State(topics=[Topic("Bio", 4, "2026-11-10"),
                         Topic("Math", 3, "2026-11-12")],
                 attempts=attempts)


class TestReport(unittest.TestCase):
    def test_readiness_is_zero_with_no_attempts(self):
        report = build_report(make_state([]))
        self.assertEqual(report["readiness_score"], 0)
        self.assertEqual(report["completion_pct"], 0)
        self.assertEqual(report["not_attempted"], ["Bio", "Math"])

    def test_readiness_is_100_with_perfect_attempts(self):
        attempts = [Attempt("Bio", True, "2026-10-28"),
                    Attempt("Math", True, "2026-10-28")]
        report = build_report(make_state(attempts))
        self.assertEqual(report["readiness_score"], 100)
        self.assertEqual(report["completion_pct"], 100)

    def test_readiness_stays_within_bounds(self):
        attempts = [Attempt("Bio", True, "2026-10-28"),
                    Attempt("Bio", False, "2026-10-28")]
        report = build_report(make_state(attempts))
        self.assertGreaterEqual(report["readiness_score"], 0)
        self.assertLessEqual(report["readiness_score"], 100)
        self.assertEqual(report["completion_pct"], 50)
        self.assertEqual(report["weakest_topics"], ["Bio"])

    def test_weakest_topic_is_lowest_accuracy(self):
        attempts = [Attempt("Bio", False, "2026-10-28"),
                    Attempt("Math", True, "2026-10-28")]
        report = build_report(make_state(attempts))
        self.assertEqual(report["weakest_topics"], ["Bio"])
        self.assertEqual(report["per_topic_accuracy_pct"],
                         {"Bio": 0.0, "Math": 100.0})


if __name__ == "__main__":
    unittest.main()
