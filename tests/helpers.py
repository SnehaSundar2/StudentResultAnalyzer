"""Shared fixtures for the test suite."""

from analyzer.models import ResultBook

SUBJECTS = ["Maths", "Physics", "English"]


def make_book():
    """Small class covering pass, fail, absent and a tie."""
    book = ResultBook(SUBJECTS)
    book.add_student("R001", "Asha Kumar", {"Maths": 95, "Physics": 90, "English": 85})   # 270
    book.add_student("R002", "Rahul Verma", {"Maths": 70, "Physics": 60, "English": 80})  # 210
    book.add_student("R003", "Priya Sharma", {"Maths": 80, "Physics": 60, "English": 70}) # 210 tie
    book.add_student("R004", "Karthik Raja", {"Maths": 30, "Physics": 50, "English": 60}) # fail
    book.add_student("R005", "Vikram Singh", {"Maths": 40, "Physics": "AB", "English": 50})  # absent
    return book
