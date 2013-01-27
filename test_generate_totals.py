import unittest

import generate_totals

class TestGenerateItems(unittest.TestCase):
    def setUp(self):
        self.gi = generate_totals.GenerateItems(None, None)
        self.gi.items_db = {
            "Memos of a Master Marksman": {"ic": [
                {"num": 1, "obj": "Memoirs of a Hunter"},
                {"num": 2, "obj": "Genius's Quill"}]},
            "Memoirs of a Hunter": {"ic": [
                {"num": 3, "obj": "Halgitian Paper"},
                {"num": 1, "obj": "Genius's Quill"}]},
            "Halgitian Paper": {"ic": [
                {"num": 3, "obj": "Kenaf Cloth"},
                {"num": 2, "obj": "Lentesco Wood"}]},
            "Genius's Quill": {"ic": [
                {"num": 1, "obj": "Pius Wood"},
                {"num": 1, "obj": "Dragon Fang"}]}
        }

    def test_basic_aggregate(self):
        test_data = [{"obj": "Memos of a Master Marksman", "num": 2},
                     {"obj": "Memoirs of a Hunter", "num": 4}]
        expected_results = {"Halgitian Paper": 12,
                            "Genius's Quill": 8,
                            "Memoirs of a Hunter": 2}

        self.gi.needed_items = test_data
        self.gi._aggregate(self.gi._itericdeps())

        self.assertEqual(self.gi.materials, expected_results)

    def test_recursive_aggregate(self):
        test_data = [{"obj": "Memos of a Master Marksman", "num": 2},
                     {"obj": "Memoirs of a Hunter", "num": 4}]
        expected_results = {"Kenaf Cloth": 54,
                            "Lentesco Wood": 36,
                            "Pius Wood": 10,
                            "Dragon Fang": 10}

        self.gi.needed_items = test_data
        self.gi._aggregate(self.gi._itericdeps(), recursive=True)

        self.assertEqual(self.gi.materials, expected_results)

if __name__ == "__main__":
    unittest.main()
