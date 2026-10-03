import unittest

from analyzer import analysis
from analyzer.exceptions import NoDataError
from analyzer.models import ResultBook
from tests.helpers import make_book


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.book = make_book()

    def test_ranking_with_ties_and_unranked_failures(self):
        ranks = {r.roll_no: r.rank for r in analysis.all_results(self.book)}
        self.assertEqual(ranks["R001"], 1)
        self.assertEqual(ranks["R002"], ranks["R003"])  # same total and GPA -> shared rank
        self.assertEqual(ranks["R002"], 2)
        self.assertIsNone(ranks["R004"])
        self.assertIsNone(ranks["R005"])

    def test_tie_broken_by_gpa(self):
        book = ResultBook(["A", "B"])
        book.add_student("X01", "Even Split", {"A": 75, "B": 75})    # 150, GPA (8 + 8) / 2 = 8.0
        book.add_student("X02", "Strong Subject", {"A": 90, "B": 60})  # 150, GPA (10 + 7) / 2 = 8.5
        book.add_student("X03", "Same As Even", {"A": 76, "B": 74})  # 150, GPA (8 + 8) / 2 = 8.0
        ranks = {r.roll_no: r.rank for r in analysis.all_results(book)}
        self.assertEqual(ranks, {"X02": 1, "X01": 2, "X03": 2})

    def test_class_summary(self):
        s = analysis.class_summary(self.book)
        self.assertEqual((s["students"], s["passed"], s["failed"]), (5, 3, 2))
        self.assertEqual(s["pass_percentage"], 60.0)
        self.assertEqual(s["highest_percentage"], 90.0)
        self.assertEqual(s["lowest_percentage"], 30.0)

    def test_subject_stats_excludes_absent_from_average(self):
        stats = analysis.subject_stats(self.book)
        phy = stats["Physics"]
        self.assertEqual(phy["appeared"], 4)
        self.assertEqual(phy["absent"], 1)
        self.assertEqual(phy["average"], 65.0)  # (90+60+60+50)/4
        self.assertEqual(phy["pass_percentage"], 80.0)  # absent counts as not passed
        self.assertEqual(stats["Maths"]["toppers"], ["Asha Kumar"])

    def test_grade_distribution_sums_to_students(self):
        dist = analysis.grade_distribution(self.book)
        self.assertEqual(sum(dist.values()), 5)
        self.assertEqual(dist["F"], 2)

    def test_top_failed_hardest(self):
        self.assertEqual([r.roll_no for r in analysis.top_students(self.book, 1)], ["R001"])
        self.assertEqual({r.roll_no for r in analysis.failed_students(self.book)}, {"R004", "R005"})
        self.assertEqual(analysis.hardest_subject(self.book), "Maths")

    def test_student_result(self):
        self.assertEqual(analysis.student_result(self.book, "r001").rank, 1)

    def test_no_data(self):
        with self.assertRaises(NoDataError):
            analysis.class_summary(ResultBook(["Maths"]))


if __name__ == "__main__":
    unittest.main()
