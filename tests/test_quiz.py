import unittest

from studysprint.models import Attempt, Card
from studysprint.quiz import accuracy_by_topic, is_correct, normalise, score


class TestQuiz(unittest.TestCase):
    def test_answer_check_is_case_insensitive_and_trims(self):
        card = Card("c1", "Bio", "Q?", "Photosynthesis")
        self.assertTrue(is_correct(card, "  photosynthesis "))
        self.assertTrue(is_correct(card, "PHOTOSYNTHESIS"))
        self.assertFalse(is_correct(card, "respiration"))

    def test_normalise_collapses_spaces(self):
        self.assertEqual(normalise("  a   b  "), "a b")

    def test_score_counts_correct_answers(self):
        cards = [Card("c1", "Bio", "Q1", "a"), Card("c2", "Bio", "Q2", "b")]
        correct, total, results = score(cards, ["A", "wrong"])
        self.assertEqual((correct, total), (1, 2))
        self.assertEqual([r[2] for r in results], [True, False])

    def test_accuracy_by_topic(self):
        attempts = [Attempt("Bio", True, "2026-10-28"),
                    Attempt("Bio", False, "2026-10-28"),
                    Attempt("Math", True, "2026-10-28")]
        self.assertEqual(accuracy_by_topic(attempts), {"Bio": 0.5, "Math": 1.0})

    def test_accuracy_empty_is_empty(self):
        self.assertEqual(accuracy_by_topic([]), {})


if __name__ == "__main__":
    unittest.main()
