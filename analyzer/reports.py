"""Report generation: formatted text tables and CSV export of results."""

import csv
import os
from datetime import datetime

from . import analysis
from .exceptions import DataFileError


def format_table(rows, columns):
    """Render a list of dicts as an aligned text table."""
    if not rows:
        return "  Nothing to show."
    widths = {c: max(len(c), *(len(str(r.get(c, ""))) for r in rows)) for c in columns}
    lines = ["  " + "  ".join(c.upper().ljust(widths[c]) for c in columns),
             "  " + "  ".join("-" * widths[c] for c in columns)]
    for r in rows:
        lines.append("  " + "  ".join(str(r.get(c, "")).ljust(widths[c]) for c in columns))
    return "\n".join(lines)


def result_rows(book):
    rows = []
    for r in analysis.all_results(book):
        row = {"rank": r.rank or "-", "roll_no": r.roll_no, "name": r.name}
        row.update({s: "AB" if m is None else m for s, m in r.marks.items()})
        row.update({"total": r.total, "percent": f"{r.percentage:.2f}",
                    "gpa": f"{r.gpa:.2f}", "grade": r.grade, "result": r.status})
        rows.append(row)
    return rows


def result_columns(book):
    return ["rank", "roll_no", "name", *book.subjects, "total", "percent", "gpa", "grade", "result"]


def build_text_report(book, title="Class Result Report"):
    s = analysis.class_summary(book)
    out = [
        "=" * 70,
        f"  {title}",
        f"  Generated: {datetime.now():%Y-%m-%d %H:%M}",
        "=" * 70,
        "",
        "  CLASS SUMMARY",
        f"  Students: {s['students']}   Subjects: {s['subjects']}   "
        f"Passed: {s['passed']}   Failed: {s['failed']}   Pass rate: {s['pass_percentage']}%",
        f"  Average: {s['average_percentage']}%   Median: {s['median_percentage']}%   "
        f"Highest: {s['highest_percentage']}%   Lowest: {s['lowest_percentage']}%   "
        f"Std dev: {s['std_dev']}",
        "",
        "  RESULTS (ranked)",
        format_table(result_rows(book), result_columns(book)),
        "",
        "  SUBJECT ANALYSIS",
    ]
    subj_rows = [{"subject": name, "average": st["average"], "median": st["median"],
                  "highest": st["highest"], "lowest": st["lowest"], "pass_%": st["pass_percentage"],
                  "absent": st["absent"], "topper": ", ".join(st["toppers"]) or "-"}
                 for name, st in analysis.subject_stats(book).items()]
    out.append(format_table(subj_rows, ["subject", "average", "median", "highest",
                                        "lowest", "pass_%", "absent", "topper"]))
    out += ["", f"  Hardest subject (lowest pass rate): {analysis.hardest_subject(book)}",
            "", "  GRADE DISTRIBUTION"]
    total = s["students"]
    for grade, count in analysis.grade_distribution(book).items():
        bar = "#" * round(30 * count / total) if total else ""
        out.append(f"  {grade:<3}{count:>4}  {bar}")
    failed = analysis.failed_students(book)
    out += ["", "  STUDENTS NEEDING SUPPORT"]
    if failed:
        for r in failed:
            reasons = ", ".join(f"{sub} ({'AB' if r.marks[sub] is None else r.marks[sub]})"
                                for sub in r.failed_subjects)
            out.append(f"  {r.roll_no:<10}{r.name:<22}failed in: {reasons}")
    else:
        out.append("  None - every student passed.")
    out.append("=" * 70)
    return "\n".join(out)


def save_text_report(book, path):
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(build_text_report(book) + "\n")
    except OSError as exc:
        raise DataFileError(f"Could not write report: {exc}") from exc
    return path


def export_results_csv(book, path):
    columns = result_columns(book)
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=columns)
            writer.writeheader()
            writer.writerows(result_rows(book))
    except OSError as exc:
        raise DataFileError(f"Could not export results: {exc}") from exc
    return path
