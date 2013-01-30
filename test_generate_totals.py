import unittest

import generate_totals

class AggregationTestCase(unittest.TestCase):
    def setUp(self):
        self.recursive = False
        self.flatten = False
        self.gi = generate_totals.GenerateItems(None, None)
        self.gi.needed_items = [{"obj": "Memos of a Master Marksman", "num": 2},
                                {"obj": "Memoirs of a Hunter", "num": 4}]
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
                {"num": 1, "obj": "Dragon Fang"}]},
            "Kenaf Cloth": {"ic": [
                {"num": 2, "obj": "Fresh Herb"}]}}

    def _run_aggregate(self):
        if self.flatten:
            self.gi._flattenneededitems()
        self.gi._aggregate(self.gi.needed_items, recursive=self.recursive)

class TestBasic(AggregationTestCase):
    def test_basic(self):
        expected_results = {"Halgitian Paper": 12,
                            "Genius's Quill": 8,
                            "Memoirs of a Hunter": 2}

        self._run_aggregate()

        self.assertEqual(self.gi.materials, expected_results)

    def test_obtained(self):
        obtained_data = {"Halgitian Paper": 3,
                         "Genius's Quill": 5}
        expected_results = {"Halgitian Paper": 9,
                            "Genius's Quill": 3,
                            "Memoirs of a Hunter": 2}

        self.gi.obtained_items = obtained_data
        self._run_aggregate()

        self.assertEqual(self.gi.materials, expected_results)

    def test_obtained_mixed(self):
        obtained_data = {"Halgitian Paper": 22,
                         "Genius's Quill": 7}
        expected_results = {"Genius's Quill": 1,
                            "Memoirs of a Hunter": 2}

        self.gi.obtained_items = obtained_data
        self._run_aggregate()

        self.assertEqual(self.gi.materials, expected_results)

class TestRecursive(AggregationTestCase):
    def setUp(self):
        AggregationTestCase.setUp(self)
        self.recursive = True

    def test_recursive(self):
        expected_results = {"Fresh Herb": 108,
                            "Lentesco Wood": 36,
                            "Pius Wood": 10,
                            "Dragon Fang": 10}

        self._run_aggregate()

        self.assertEqual(self.gi.materials, expected_results)

    def test_obtained(self):
        obtained_data = {"Halgitian Paper": 3,
                         "Genius's Quill": 5}
        expected_results = {"Fresh Herb": 90,
                            "Lentesco Wood": 30,
                            "Pius Wood": 5,
                            "Dragon Fang": 5}

        self.gi.obtained_items = obtained_data
        self._run_aggregate()

        self.assertEqual(self.gi.materials, expected_results)

    def test_obtained_mixed(self):
        obtained_data = {"Halgitian Paper": 17,
                         "Genius's Quill": 12}
        expected_results = {"Fresh Herb": 6,
                            "Lentesco Wood": 2}

        self.gi.obtained_items = obtained_data
        self._run_aggregate()

        self.assertEqual(self.gi.materials, expected_results)

class TestFlattened(AggregationTestCase):
    def setUp(self):
        AggregationTestCase.setUp(self)
        self.flatten = True

    def test_flatten(self):
        expected_results = {"Halgitian Paper": 6,
                            "Genius's Quill": 6,
                            "Memoirs of a Hunter": 2}

        self._run_aggregate()

        self.assertEqual(self.gi.materials, expected_results)

class TestRecursiveFlattened(AggregationTestCase):
    def setUp(self):
        AggregationTestCase.setUp(self)
        self.recursive = True
        self.flatten = True

    def test_flatten(self):
        expected_results = {"Fresh Herb": 72,
                            "Lentesco Wood": 24,
                            "Pius Wood": 8,
                            "Dragon Fang": 8}

        self._run_aggregate()

        self.assertEqual(self.gi.materials, expected_results)

    def test_mixed(self):
        self.gi.needed_items = [{"obj": "Memos of a Master Marksman", "num": 2},
                                {"obj": "Memoirs of a Hunter", "num": 4},
                                {"obj": "Kenaf Cloth", "num": 2}]
        expected_results = {"Fresh Herb": 72,
                            "Lentesco Wood": 24,
                            "Pius Wood": 8,
                            "Dragon Fang": 8}

        self._run_aggregate()

        self.assertEqual(self.gi.materials, expected_results)

if __name__ == "__main__":
    unittest.main()
