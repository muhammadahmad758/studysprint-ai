import unittest
from datetime import date

from studysprint.models import Review
from studysprint.repetition import INTERVALS, due_today, new_review, next_review

TODAY = date(2026, 10, 28)


class TestRepetition(unittest.TestCase):
    def test_intervals_are_1_3_7_14(self):
        self.assertEqual(INTERVALS, [1, 3, 7, 14])

    def test_correct_answer_advances_stage_and_gap(self):
        review = Review("c1", "Bio", "2026-10-28", stage=0)
        updated = next_review(review, True, TODAY)
        self.assertEqual(updated.stage, 1)
        self.assertEqual(updated.due_date, "2026-10-31")  # +3 days

    def test_wrong_answer_resets_to_tomorrow(self):
        review = Review("c1", "Bio", "2026-10-28", stage=2)
        updated = next_review(review, False, TODAY)
        self.assertEqual(updated.stage, 0)
        self.assertEqual(updated.due_date, "2026-10-29")  # +1 day

    def test_stage_caps_at_last_interval(self):
        review = Review("c1", "Bio", "2026-10-28", stage=3)
        updated = next_review(review, True, TODAY)
        self.assertEqual(updated.stage, 3)
        self.assertEqual(updated.due_date, "2026-11-11")  # +14 days

    def test_new_review_due_tomorrow(self):
        self.assertEqual(new_review("c1", "Bio", TODAY).due_date, "2026-10-29")

    def test_due_today_includes_overdue_and_excludes_future(self):
        reviews = [Review("c1", "Bio", "2026-10-27", 0),
                   Review("c2", "Bio", "2026-10-28", 0),
                   Review("c3", "Bio", "2026-10-29", 0)]
        self.assertEqual([r.card_id for r in due_today(reviews, TODAY)],
                         ["c1", "c2"])


if __name__ == "__main__":
    unittest.main()
