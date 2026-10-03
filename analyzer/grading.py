"""Grading rules: grade scale, grade points, pass mark and per-student results."""

from dataclasses import dataclass, field

PASS_MARK = 35  # minimum mark per subject

# (minimum percentage, grade letter, grade point) - checked top to bottom
GRADE_SCALE = [
    (90, "O", 10),
    (80, "A+", 9),
    (70, "A", 8),
    (60, "B+", 7),
    (50, "B", 6),
    (40, "C", 5),
    (PASS_MARK, "P", 4),
    (0, "F", 0),
]
GRADE_ORDER = [g for _, g, _ in GRADE_SCALE]


def grade_for(score):
    """Return (grade, grade_point) for a mark or percentage 0-100. None (absent) -> F."""
    if score is None:
        return "F", 0
    for minimum, grade, point in GRADE_SCALE:
        if score >= minimum:
            return grade, point
    return "F", 0


def is_pass(mark):
    return mark is not None and mark >= PASS_MARK


@dataclass
class StudentResult:
    roll_no: str
    name: str
    marks: dict
    total: int
    max_total: int
    percentage: float
    gpa: float
    grade: str
    status: str  # PASS / FAIL
    failed_subjects: list = field(default_factory=list)
    absent_subjects: list = field(default_factory=list)
    rank: int = None  # filled in by analysis.rank_students for passed students


def compute_result(student, subjects):
    """Turn a Student's raw marks into a StudentResult."""
    marks = {s: student.marks.get(s) for s in subjects}
    obtained = [m or 0 for m in marks.values()]
    total = sum(obtained)
    max_total = 100 * len(subjects)
    percentage = round(100 * total / max_total, 2) if max_total else 0.0
    points = [grade_for(m)[1] for m in marks.values()]
    gpa = round(sum(points) / len(points), 2) if points else 0.0
    failed = [s for s, m in marks.items() if not is_pass(m)]
    absent = [s for s, m in marks.items() if m is None]
    status = "PASS" if not failed else "FAIL"
    grade = grade_for(percentage)[0] if status == "PASS" else "F"
    return StudentResult(
        roll_no=student.roll_no, name=student.name, marks=marks,
        total=total, max_total=max_total, percentage=percentage, gpa=gpa,
        grade=grade, status=status, failed_subjects=failed, absent_subjects=absent,
    )
