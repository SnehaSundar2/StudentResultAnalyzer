import unittest

from analyzer.exceptions import DuplicateStudentError, StudentNotFoundError, ValidationError
from analyzer.grading import compute_result, grade_for
from analyzer.models import ResultBook
from tests.helpers import SUBJECTS, make_book


class TestResultBook(unittest.TestCase):
    def setUp(self):
        self.book = make_book()

    def test_subjects_validated(self):
        with self.assertRaises(ValidationError):
            ResultBook([])
        with self.assertRaises(ValidationError):
            ResultBook(["Maths", "maths"])

    def test_add_student_matches_subjects_case_insensitively(self):
        s = self.book.add_student("r010", "new student", {"maths": 50, "PHYSICS": 60, "English": 70})
        self.assertEqual(s.roll_no, "R010")
        self.assertEqual(s.marks, {"Maths": 50, "Physics": 60, "English": 70})

    def test_missing_or_unknown_subject(self):
        with self.assertRaises(ValidationError):
            self.book.add_student("R010", "X", {"Maths": 50, "Physics": 60})
        with self.assertRaises(ValidationError):
            self.book.add_student("R010", "X", {"Maths": 50, "Physics": 60, "English": 1, "Art": 5})

    def test_invalid_mark_not_added(self):
        with self.assertRaises(ValidationError):
            self.book.add_student("R010", "X", {"Maths": 150, "Physics": 60, "English": 70})
        self.assertNotIn("R010", self.book.students)

    def test_duplicate_and_missing(self):
        with self.assertRaises(DuplicateStudentError):
            self.book.add_student("r001", "X", {"Maths": 1, "Physics": 1, "English": 1})
        with self.assertRaises(StudentNotFoundError):
            self.book.get_student("R999")

    def test_update_and_remove(self):
        self.book.update_mark("R004", "maths", "65")
        self.assertEqual(self.book.get_student("R004").marks["Maths"], 65)
        with self.assertRaises(ValidationError):
            self.book.update_mark("R004", "Art", 50)
        self.book.remove_student("R004")
        self.assertEqual(len(self.book), 4)

    def test_search(self):
        self.assertEqual([s.roll_no for s in self.book.search("sharma")], ["R003"])
        self.assertEqual(len(self.book.search("r00")), 5)


class TestGrading(unittest.TestCase):
    def test_grade_boundaries(self):
        cases = {100: "O", 90: "O", 89.99: "A+", 80: "A+", 70: "A", 60: "B+",
                 50: "B", 40: "C", 35: "P", 34.99: "F", 0: "F", None: "F"}
        for score, grade in cases.items():
            self.assertEqual(grade_for(score)[0], grade, score)

    def test_compute_pass(self):
        r = compute_result(make_book().get_student("R001"), SUBJECTS)
        self.assertEqual((r.total, r.max_total), (270, 300))
        self.assertEqual(r.percentage, 90.0)
        self.assertEqual(r.gpa, 9.67)  # O, O, A+ -> (10 + 10 + 9) / 3
        self.assertEqual((r.grade, r.status), ("O", "PASS"))

    def test_compute_fail_and_absent(self):
        book = make_book()
        fail = compute_result(book.get_student("R004"), SUBJECTS)
        self.assertEqual((fail.status, fail.grade, fail.failed_subjects), ("FAIL", "F", ["Maths"]))
        absent = compute_result(book.get_student("R005"), SUBJECTS)
        self.assertEqual(absent.total, 90)
        self.assertEqual(absent.absent_subjects, ["Physics"])
        self.assertEqual(absent.status, "FAIL")


if __name__ == "__main__":
    unittest.main()
