"""Data model and the ResultBook that holds a class's marks.

ResultBook validates every change, so the data it holds is always clean.
"""

from dataclasses import dataclass, field

from . import validators as v
from .exceptions import DuplicateStudentError, StudentNotFoundError, ValidationError

MAX_SUBJECTS = 12


@dataclass
class Student:
    roll_no: str
    name: str
    marks: dict = field(default_factory=dict)  # subject -> int, or None if absent


class ResultBook:
    def __init__(self, subjects):
        cleaned = [v.validate_subject(s) for s in subjects]
        if not cleaned:
            raise ValidationError("At least one subject is required.")
        if len(cleaned) > MAX_SUBJECTS:
            raise ValidationError(f"At most {MAX_SUBJECTS} subjects are supported.")
        duplicates = {s for s in cleaned if cleaned.count(s) > 1}
        if duplicates:
            raise ValidationError(f"Duplicate subject(s): {', '.join(sorted(duplicates))}.")
        self.subjects = cleaned
        self.students = {}

    def __len__(self):
        return len(self.students)

    def _clean_marks(self, marks):
        """marks: dict subject->raw value. Subject names are matched case-insensitively."""
        lookup = {s.lower(): s for s in self.subjects}
        cleaned = {}
        for raw_subject, raw_mark in marks.items():
            subject = lookup.get(str(raw_subject).strip().lower())
            if subject is None:
                raise ValidationError(f"Unknown subject '{raw_subject}'.")
            cleaned[subject] = v.validate_mark(raw_mark, subject)
        missing = [s for s in self.subjects if s not in cleaned]
        if missing:
            raise ValidationError(f"Missing mark(s) for: {', '.join(missing)}.")
        return cleaned

    def add_student(self, roll_no, name, marks):
        student = Student(v.validate_roll_no(roll_no), v.validate_name(name), self._clean_marks(marks))
        if student.roll_no in self.students:
            raise DuplicateStudentError(f"Roll number {student.roll_no} already exists.")
        self.students[student.roll_no] = student
        return student

    def get_student(self, roll_no):
        roll_no = v.validate_roll_no(roll_no)
        try:
            return self.students[roll_no]
        except KeyError:
            raise StudentNotFoundError(f"No student with roll number {roll_no}.") from None

    def update_mark(self, roll_no, subject, mark):
        student = self.get_student(roll_no)
        lookup = {s.lower(): s for s in self.subjects}
        key = lookup.get(str(subject).strip().lower())
        if key is None:
            raise ValidationError(f"Unknown subject '{subject}'. Subjects: {', '.join(self.subjects)}.")
        student.marks[key] = v.validate_mark(mark, key)
        return student

    def remove_student(self, roll_no):
        student = self.get_student(roll_no)
        del self.students[student.roll_no]
        return student

    def search(self, text):
        text = (text or "").strip().lower()
        return [s for s in self.students.values()
                if text in s.name.lower() or text in s.roll_no.lower()]
