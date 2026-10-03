"""Interactive menu-driven command-line interface.

All AnalyzerError subclasses are caught here and shown as friendly
messages; unexpected errors are logged and the menu keeps running.
"""

import logging

from . import analysis, loader, reports
from .exceptions import AnalyzerError, NoDataError
from .grading import grade_for
from .models import ResultBook
from .validators import validate_positive_int, validate_subject

log = logging.getLogger("analyzer")

MENU = """
============ STUDENT RESULT ANALYZER ============
 DATA                       ANALYSIS
  1. Load marks from CSV     7. Class result table
  2. Add student             8. Student report card
  3. Update a mark           9. Subject-wise analysis
  4. Remove student         10. Top performers
  5. Search students        11. Failed students
  6. Save marks to CSV      12. Grade distribution
 EXPORT
 13. Save full text report  14. Export results to CSV
  0. Exit
================================================="""


def ask(prompt):
    return input(f"  {prompt}: ").strip()


class AnalyzerCLI:
    def __init__(self, book=None, data_path=None):
        self.book = book
        self.data_path = data_path
        self.actions = {
            "1": self.load, "2": self.add_student, "3": self.update_mark,
            "4": self.remove_student, "5": self.search, "6": self.save,
            "7": self.result_table, "8": self.report_card, "9": self.subject_analysis,
            "10": self.top_performers, "11": self.failed, "12": self.grade_distribution,
            "13": self.text_report, "14": self.export_csv,
        }

    def require_book(self):
        if self.book is None:
            raise NoDataError("No class loaded. Load a CSV (option 1) or add a student (option 2) first.")
        return self.book

    def run(self):
        while True:
            print(MENU)
            if self.book is not None:
                print(f"  Loaded: {len(self.book)} student(s), subjects: {', '.join(self.book.subjects)}")
            choice = ask("Choose an option")
            if choice == "0":
                print("  Goodbye!")
                return
            action = self.actions.get(choice)
            if action is None:
                print("  ! Invalid option, please enter a number from the menu.")
                continue
            try:
                action()
            except AnalyzerError as exc:
                log.warning("%s failed: %s", action.__name__, exc)
                print(f"  ! Error: {exc}")
            except (KeyboardInterrupt, EOFError):
                print("\n  Operation cancelled.")
            except Exception:  # safety net; full traceback goes to the log file
                log.exception("Unexpected error in %s", action.__name__)
                print("  ! An unexpected error occurred. See analyzer.log for details.")

    # ---- data
    def load(self):
        path = ask(f"CSV file path [{self.data_path or 'sample_data/students.csv'}]") \
            or self.data_path or "sample_data/students.csv"
        book, errors = loader.load_csv(path)
        self.book, self.data_path = book, path
        log.info("Loaded %s: %d students, %d rejected rows", path, len(book), len(errors))
        print(f"  Loaded {len(book)} student(s) with subjects: {', '.join(book.subjects)}")
        if errors:
            print(f"  {len(errors)} row(s) were skipped:")
            for e in errors:
                print(f"    - {e}")

    def add_student(self):
        if self.book is None:
            raw = ask("No class loaded. Enter subjects separated by commas")
            subjects = [validate_subject(s) for s in raw.split(",") if s.strip()]
            self.book = ResultBook(subjects)
        roll, name = ask("Roll number"), ask("Name")
        marks = {s: ask(f"{s} mark (0-100, AB if absent)") for s in self.book.subjects}
        student = self.book.add_student(roll, name, marks)
        log.info("Added student %s", student.roll_no)
        print(f"  Added {student.name} ({student.roll_no}). Remember to save (option 6).")

    def update_mark(self):
        book = self.require_book()
        student = book.update_mark(ask("Roll number"), ask(f"Subject [{', '.join(book.subjects)}]"),
                                   ask("New mark (0-100, AB if absent)"))
        log.info("Updated marks for %s", student.roll_no)
        print(f"  Updated {student.name}'s marks.")

    def remove_student(self):
        book = self.require_book()
        roll = ask("Roll number")
        if ask(f"Really remove {roll}? [y/N]").lower() != "y":
            print("  Cancelled.")
            return
        student = book.remove_student(roll)
        log.info("Removed student %s", student.roll_no)
        print(f"  Removed {student.name}.")

    def search(self):
        found = self.require_book().search(ask("Name or roll number contains"))
        if not found:
            print("  No matching students.")
        for s in found:
            print(f"  {s.roll_no:<10} {s.name}")

    def save(self):
        book = self.require_book()
        path = ask(f"Save to [{self.data_path or 'students.csv'}]") or self.data_path or "students.csv"
        loader.save_csv(book, path)
        self.data_path = path
        log.info("Saved marks to %s", path)
        print(f"  Saved {len(book)} student(s) to {path}.")

    # ---- analysis
    def result_table(self):
        book = self.require_book()
        print(reports.format_table(reports.result_rows(book), reports.result_columns(book)))

    def report_card(self):
        book = self.require_book()
        r = analysis.student_result(book, ask("Roll number"))
        print(f"\n  REPORT CARD - {r.name} ({r.roll_no})")
        print("  " + "-" * 40)
        for subject, mark in r.marks.items():
            shown = "AB" if mark is None else mark
            print(f"  {subject:<20}{shown!s:>5}   {grade_for(mark)[0]}")
        print("  " + "-" * 40)
        print(f"  Total: {r.total}/{r.max_total}   Percentage: {r.percentage:.2f}%   GPA: {r.gpa:.2f}")
        print(f"  Grade: {r.grade}   Result: {r.status}   Rank: {r.rank or '-'}")
        if r.failed_subjects:
            print(f"  Needs improvement in: {', '.join(r.failed_subjects)}")

    def subject_analysis(self):
        rows = [{"subject": s, "average": st["average"], "median": st["median"],
                 "highest": st["highest"], "lowest": st["lowest"], "std_dev": st["std_dev"],
                 "pass_%": st["pass_percentage"], "absent": st["absent"],
                 "topper": ", ".join(st["toppers"]) or "-"}
                for s, st in analysis.subject_stats(self.require_book()).items()]
        print(reports.format_table(rows, list(rows[0])))
        print(f"\n  Hardest subject: {analysis.hardest_subject(self.book)}")

    def top_performers(self):
        n = validate_positive_int(ask("How many? [3]") or 3, "Count", 50)
        for r in analysis.top_students(self.require_book(), n):
            print(f"  #{r.rank:<3} {r.name:<22} {r.percentage:6.2f}%  GPA {r.gpa:.2f}  {r.grade}")

    def failed(self):
        failed = analysis.failed_students(self.require_book())
        if not failed:
            print("  Every student passed!")
        for r in failed:
            print(f"  {r.roll_no:<10} {r.name:<22} failed: {', '.join(r.failed_subjects)}")

    def grade_distribution(self):
        dist = analysis.grade_distribution(self.require_book())
        total = sum(dist.values())
        for grade, count in dist.items():
            print(f"  {grade:<3}{count:>4}  {'#' * round(30 * count / total)}")

    # ---- export
    def text_report(self):
        path = ask("Report file [reports/result_report.txt]") or "reports/result_report.txt"
        reports.save_text_report(self.require_book(), path)
        print(f"  Report written to {path}")

    def export_csv(self):
        path = ask("CSV file [reports/results.csv]") or "reports/results.csv"
        reports.export_results_csv(self.require_book(), path)
        print(f"  Results exported to {path}")
