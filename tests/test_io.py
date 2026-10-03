"""Tests for CSV loading/saving, report export and the interactive CLI."""

import csv
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from analyzer import loader, reports
from analyzer.cli import AnalyzerCLI
from analyzer.exceptions import DataFileError
from tests.helpers import make_book


class TempDirTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = tmp.name

    def write(self, name, text):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        return path


class TestLoader(TempDirTest):
    def test_good_and_bad_rows(self):
        path = self.write("m.csv", "roll_no,name,Maths,Physics\n"
                                   "A01,Asha,90,80\n"
                                   "\n"
                                   "A02,Bad Mark,90,xyz\n"
                                   "A03,Short,90\n"
                                   "A01,Dup,50,50\n"
                                   "A04,Absent,AB,40\n")
        book, errors = loader.load_csv(path)
        self.assertEqual(sorted(book.students), ["A01", "A04"])
        self.assertEqual(len(errors), 3)
        self.assertTrue(errors[0].startswith("Line 4:"))
        self.assertIsNone(book.students["A04"].marks["Maths"])

    def test_structural_errors(self):
        with self.assertRaises(DataFileError):
            loader.load_csv(os.path.join(self.dir, "missing.csv"))
        with self.assertRaises(DataFileError):
            loader.load_csv(self.write("empty.csv", ""))
        with self.assertRaises(DataFileError):
            loader.load_csv(self.write("hdr.csv", "id,student,Maths\n1,A,50\n"))
        with self.assertRaises(DataFileError):
            loader.load_csv(self.write("nosubj.csv", "roll_no,name\n"))

    def test_non_utf8_file(self):
        path = os.path.join(self.dir, "latin.csv")
        with open(path, "wb") as fh:
            fh.write("roll_no,name,Maths\nA01,Jos\xe9,50\n".encode("latin-1"))
        with self.assertRaises(DataFileError):
            loader.load_csv(path)

    def test_save_roundtrip(self):
        book = make_book()
        path = os.path.join(self.dir, "out", "saved.csv")
        loader.save_csv(book, path)
        loaded, errors = loader.load_csv(path)
        self.assertEqual(errors, [])
        self.assertEqual(loaded.students["R005"].marks, book.students["R005"].marks)

    def test_sample_file_loads(self):
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        book, errors = loader.load_csv(os.path.join(here, "sample_data", "students.csv"))
        self.assertEqual(len(book), 12)
        self.assertEqual(len(errors), 3)


class TestReports(TempDirTest):
    def test_text_report(self):
        text = reports.build_text_report(make_book())
        for section in ["CLASS SUMMARY", "SUBJECT ANALYSIS", "GRADE DISTRIBUTION", "Karthik Raja"]:
            self.assertIn(section, text)

    def test_export_results_csv(self):
        path = reports.export_results_csv(make_book(), os.path.join(self.dir, "r.csv"))
        with open(path, newline="") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(rows[0]["roll_no"], "R001")
        self.assertEqual(rows[0]["rank"], "1")
        self.assertEqual(rows[-1]["result"], "FAIL")


def run_cli(cli, inputs):
    out = io.StringIO()
    with patch("builtins.input", side_effect=inputs), redirect_stdout(out):
        cli.run()
    return out.getvalue()


class TestCLI(unittest.TestCase):
    def test_report_card_and_stats(self):
        out = run_cli(AnalyzerCLI(make_book()), ["8", "R001", "9", "11", "0"])
        self.assertIn("REPORT CARD - Asha Kumar", out)
        self.assertIn("Hardest subject: Maths", out)
        self.assertIn("Karthik Raja", out)

    def test_errors_shown_not_raised(self):
        out = run_cli(AnalyzerCLI(), ["7", "42", "0"])
        self.assertIn("No class loaded", out)
        self.assertIn("Invalid option", out)

    def test_add_student_creates_class(self):
        cli = AnalyzerCLI()
        out = run_cli(cli, ["2", "Maths, Physics", "A01", "asha", "95", "abc",
                            "2", "A01", "asha", "95", "88", "0"])
        self.assertIn("Physics mark 'abc' is not a number", out)
        self.assertIn("Added Asha (A01)", out)
        self.assertEqual(cli.book.subjects, ["Maths", "Physics"])


if __name__ == "__main__":
    unittest.main()
