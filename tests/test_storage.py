import os
import tempfile
import unittest

from studysprint.models import Attempt, Card, State, Topic
from studysprint.storage import load, save


class TestStorage(unittest.TestCase):
    def test_round_trip_preserves_everything(self):
        state = State(
            topics=[Topic("Bio", 4, "2026-11-10")],
            cards=[Card("c1", "Bio", "What is DNA?", "Genetic material")],
            attempts=[Attempt("Bio", True, "2026-10-28")],
            reviews=[],
        )
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "data.json")
            save(state, path)
            loaded = load(path)
        self.assertEqual(loaded, state)

    def test_missing_file_gives_empty_state(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(load(os.path.join(folder, "nope.json")), State())

    def test_save_does_not_leave_temp_files(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "data.json")
            save(State(), path)
            self.assertEqual(os.listdir(folder), ["data.json"])


if __name__ == "__main__":
    unittest.main()
