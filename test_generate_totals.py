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

    @unittest.skip("future functionality")
    def test_flatten(self):
        test_data = {"Memos of a Master Marksman": 2,
                     "Memoirs of a Hunter": 4}
        expected_results = {"Kenaf Cloth": 36,
                            "Lentesco Wood": 24,
                            "Pius Wood": 8,
                            "Dragon Fang": 8}

        self.gi.needed_items = test_data
        self.gi._aggregate(self.gi.needed_items, recursive=True)

        self.assertEqual(self.gi.materials, expected_results)

    def test_basic_aggregate(self):
        test_data = [{"obj": "Memos of a Master Marksman", "num": 2},
                     {"obj": "Memoirs of a Hunter", "num": 4}]
        expected_results = {"Halgitian Paper": 12,
                            "Genius's Quill": 8,
                            "Memoirs of a Hunter": 2}

        self.gi.needed_items = test_data
        self.gi._aggregate(self.gi.needed_items)

        self.assertEqual(self.gi.materials, expected_results)

    def test_recursive_aggregate(self):
        test_data = [{"obj": "Memos of a Master Marksman", "num": 2},
                     {"obj": "Memoirs of a Hunter", "num": 4}]
        expected_results = {"Kenaf Cloth": 54,
                            "Lentesco Wood": 36,
                            "Pius Wood": 10,
                            "Dragon Fang": 10}

        self.gi.needed_items = test_data
        self.gi._aggregate(self.gi.needed_items, recursive=True)

        self.assertEqual(self.gi.materials, expected_results)

    def test_obtained(self):
        test_data = [{"obj": "Memos of a Master Marksman", "num": 2},
                     {"obj": "Memoirs of a Hunter", "num": 4}]
        obtained_data = {"Halgitian Paper": 3,
                         "Genius's Quill": 5}
        expected_results = {"Halgitian Paper": 9,
                            "Genius's Quill": 3,
                            "Memoirs of a Hunter": 2}

        self.gi.needed_items = test_data
        self.gi.obtained_items = obtained_data
        self.gi._aggregate(self.gi.needed_items)

        self.assertEqual(self.gi.materials, expected_results)

    def test_obtained_mixed(self):
        test_data = [{"obj": "Memos of a Master Marksman", "num": 2},
                     {"obj": "Memoirs of a Hunter", "num": 4}]
        obtained_data = {"Halgitian Paper": 22,
                         "Genius's Quill": 7}
        expected_results = {"Genius's Quill": 1,
                            "Memoirs of a Hunter": 2}

        self.gi.needed_items = test_data
        self.gi.obtained_items = obtained_data
        self.gi._aggregate(self.gi.needed_items)

        self.assertEqual(self.gi.materials, expected_results)

    def test_obtained_recursive(self):
        test_data = [{"obj": "Memos of a Master Marksman", "num": 2},
                     {"obj": "Memoirs of a Hunter", "num": 4}]
        obtained_data = {"Halgitian Paper": 3,
                         "Genius's Quill": 5}
        expected_results = {"Kenaf Cloth": 45,
                            "Lentesco Wood": 30,
                            "Pius Wood": 5,
                            "Dragon Fang": 5}

        self.gi.needed_items = test_data
        self.gi.obtained_items = obtained_data
        self.gi._aggregate(self.gi.needed_items, recursive=True)

        self.assertEqual(self.gi.materials, expected_results)

    def test_obtained_recursive_mixed(self):
        test_data = [{"obj": "Memos of a Master Marksman", "num": 2},
                     {"obj": "Memoirs of a Hunter", "num": 4}]
        obtained_data = {"Halgitian Paper": 17,
                         "Genius's Quill": 12}
        expected_results = {"Kenaf Cloth": 3,
                            "Lentesco Wood": 2}

        self.gi.needed_items = test_data
        self.gi.obtained_items = obtained_data
        self.gi._aggregate(self.gi.needed_items, recursive=True)

        self.assertEqual(self.gi.materials, expected_results)

if __name__ == "__main__":
    unittest.main()
