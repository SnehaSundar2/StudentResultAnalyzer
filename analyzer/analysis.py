"""Data processing: results, ranks, class and subject statistics."""

import statistics
from collections import Counter

from .exceptions import NoDataError
from .grading import GRADE_ORDER, compute_result, is_pass


def _require_data(book):
    if not book.students:
        raise NoDataError("No student records loaded yet.")


def all_results(book):
    """Results for every student, ranked. Ties share a rank (1, 2, 2, 4)."""
    _require_data(book)
    results = [compute_result(s, book.subjects) for s in book.students.values()]
    rank_students(results)
    return sorted(results, key=lambda r: (r.rank is None, r.rank or 0, -r.total, r.roll_no))


def rank_students(results):
    """Rank passed students by total (then GPA). Failed students get no rank."""
    passed = sorted((r for r in results if r.status == "PASS"),
                    key=lambda r: (-r.total, -r.gpa))
    previous, rank = None, 0
    for position, r in enumerate(passed, 1):
        key = (r.total, r.gpa)
        if key != previous:
            rank, previous = position, key
        r.rank = rank
    return results


def student_result(book, roll_no):
    student = book.get_student(roll_no)
    return next(r for r in all_results(book) if r.roll_no == student.roll_no)


def _stats(values):
    if not values:
        return {"average": 0.0, "median": 0.0, "highest": 0, "lowest": 0, "std_dev": 0.0}
    return {
        "average": round(statistics.mean(values), 2),
        "median": round(float(statistics.median(values)), 2),
        "highest": max(values),
        "lowest": min(values),
        "std_dev": round(statistics.pstdev(values), 2),
    }


def class_summary(book):
    results = all_results(book)
    passed = [r for r in results if r.status == "PASS"]
    st = _stats([r.percentage for r in results])
    return {
        "students": len(results),
        "subjects": len(book.subjects),
        "passed": len(passed),
        "failed": len(results) - len(passed),
        "pass_percentage": round(100 * len(passed) / len(results), 2),
        "average_percentage": st["average"],
        "median_percentage": st["median"],
        "highest_percentage": st["highest"],
        "lowest_percentage": st["lowest"],
        "std_dev": st["std_dev"],
    }


def subject_stats(book):
    """Per-subject statistics. Absent students are excluded from averages."""
    _require_data(book)
    stats = {}
    for subject in book.subjects:
        marks = [s.marks[subject] for s in book.students.values()]
        present = [m for m in marks if m is not None]
        passed = sum(1 for m in marks if is_pass(m))
        top = max(present, default=None)
        toppers = [s.name for s in book.students.values() if top is not None and s.marks[subject] == top]
        stats[subject] = {
            **_stats(present),
            "appeared": len(present),
            "absent": len(marks) - len(present),
            "passed": passed,
            "pass_percentage": round(100 * passed / len(marks), 2),
            "toppers": toppers,
        }
    return stats


def grade_distribution(book):
    counts = Counter(r.grade for r in all_results(book))
    return {g: counts.get(g, 0) for g in GRADE_ORDER}


def top_students(book, n=3):
    return [r for r in all_results(book) if r.rank is not None][:n]


def failed_students(book):
    return [r for r in all_results(book) if r.status == "FAIL"]


def hardest_subject(book):
    """Subject with the lowest pass percentage (ties broken by lower average)."""
    stats = subject_stats(book)
    return min(stats, key=lambda s: (stats[s]["pass_percentage"], stats[s]["average"]))
