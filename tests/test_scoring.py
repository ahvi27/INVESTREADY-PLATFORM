import unittest

from investready.scoring import calculate_score, category_for, normalize


class ScoringTests(unittest.TestCase):
    def test_normalize_caps_at_100(self):
        self.assertEqual(normalize(200, 100), 100)

    def test_normalize_rejects_negative(self):
        with self.assertRaises(ValueError):
            normalize(-1, 100)

    def test_category_boundaries(self):
        self.assertEqual(category_for(80), "Strategic Priority")
        self.assertEqual(category_for(60), "Strong Opportunity")
        self.assertEqual(category_for(40), "Requires Development")
        self.assertEqual(category_for(39.9), "Low Priority")

    def test_perfect_investor_scores_100(self):
        result = calculate_score(100, 1000, 100, 10, 10, 10, 10)
        self.assertEqual(result.total, 100)
        self.assertEqual(result.category, "Strategic Priority")

    def test_weighted_score(self):
        result = calculate_score(50, 500, 50, 5, 5, 5, 5)
        self.assertEqual(result.total, 50)
