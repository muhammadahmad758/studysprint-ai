import unittest
from datetime import date

from studysprint.models import Topic
from studysprint.planner import daily_plan, priority, ranked_topics

TODAY = date(2026, 10, 28)


class TestPlanner(unittest.TestCase):
    def test_harder_closer_weaker_topic_ranks_first(self):
        hard = Topic("Hard", 5, "2026-10-30")
        easy = Topic("Easy", 1, "2026-12-30")
        ranked = ranked_topics([easy, hard], {"Hard": 0.0, "Easy": 1.0}, TODAY)
        self.assertEqual(ranked[0].name, "Hard")

    def test_priority_is_deterministic(self):
        topic = Topic("Math", 4, "2026-11-05")
        self.assertEqual(priority(topic, 0.5, TODAY),
                         priority(topic, 0.5, TODAY))

    def test_weakness_beats_difficulty_when_exam_is_far(self):
        weak = Topic("Weak", 2, "2026-12-30")
        strong = Topic("Strong", 4, "2026-12-30")
        self.assertGreater(priority(weak, 0.0, TODAY),
                           priority(strong, 1.0, TODAY))

    def test_plan_starts_today_ends_on_latest_exam(self):
        topics = [Topic("A", 3, "2026-10-30")]
        plan = daily_plan(topics, {}, TODAY)
        self.assertEqual(plan[0]["date"], "2026-10-28")
        self.assertEqual(plan[-1]["date"], "2026-10-30")
        self.assertTrue(all(p["topic"] == "A" for p in plan))

    def test_empty_topics_give_empty_plan(self):
        self.assertEqual(daily_plan([], {}, TODAY), [])


if __name__ == "__main__":
    unittest.main()
