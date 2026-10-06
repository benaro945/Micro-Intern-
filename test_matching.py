import unittest
from matching import calculate_match, skill_score, budget_score

class MatchingTests(unittest.TestCase):
    def test_skill_score(self):
        self.assertEqual(skill_score("Python, Git", "Python, SQL"), 50.0)

    def test_budget_score(self):
        self.assertEqual(budget_score(20, 20), 100.0)
        self.assertEqual(budget_score(10, 20), 50.0)

    def test_full_match(self):
        student = {
            "skills": "Python, Git",
            "minimum_budget": 20,
            "availability": "Saturday",
            "experience": "Intermediate",
            "rating": 5,
        }
        task = {
            "required_skills": "Python, Git",
            "budget": 25,
            "schedule": "Saturday",
            "experience": "Intermediate",
        }
        result = calculate_match(student, task)
        self.assertEqual(result["total"], 100.0)

if __name__ == "__main__":
    unittest.main()
