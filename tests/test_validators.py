import unittest

from analyzer import validators as v
from analyzer.exceptions import ValidationError


class TestValidators(unittest.TestCase):
    def test_roll_no(self):
        self.assertEqual(v.validate_roll_no(" 21cs 001 "), "21CS001")
        for bad in ["", "A", "21-CS-001", "X" * 16]:
            with self.assertRaises(ValidationError):
                v.validate_roll_no(bad)

    def test_name(self):
        self.assertEqual(v.validate_name("  asha   kumar "), "Asha Kumar")
        for bad in ["", "R2D2", "x" * 61]:
            with self.assertRaises(ValidationError):
                v.validate_name(bad)

    def test_subject(self):
        self.assertEqual(v.validate_subject("computer science"), "Computer Science")
        with self.assertRaises(ValidationError):
            v.validate_subject("Maths!")

    def test_mark_valid_values(self):
        self.assertEqual(v.validate_mark("0"), 0)
        self.assertEqual(v.validate_mark(" 100 "), 100)
        self.assertEqual(v.validate_mark("75.0"), 75)

    def test_mark_absent_tokens(self):
        for token in ["AB", "ab", "Absent", "ABS"]:
            self.assertIsNone(v.validate_mark(token))

    def test_mark_invalid(self):
        for bad in ["-1", "101", "75.5", "abc", "", None]:
            with self.assertRaises(ValidationError):
                v.validate_mark(bad, "Maths")

    def test_positive_int(self):
        self.assertEqual(v.validate_positive_int("3", "Count"), 3)
        for bad in ["0", "x", "51"]:
            with self.assertRaises(ValidationError):
                v.validate_positive_int(bad, "Count", 50)


if __name__ == "__main__":
    unittest.main()
