"""CSV import and export of raw marks.

Expected CSV layout (any number of subject columns):

    roll_no,name,Maths,Physics,Chemistry
    21CS001,Asha Kumar,88,76,AB

Bad rows are skipped and reported with their line number instead of
stopping the whole import; structural problems (missing file, missing
header columns) raise DataFileError.
"""

import csv
import os

from .exceptions import AnalyzerError, DataFileError, ValidationError
from .models import ResultBook

REQUIRED_COLUMNS = ["roll_no", "name"]


def load_csv(path):
    """Return (ResultBook, errors) where errors is a list of 'Line N: message' strings."""
    if not os.path.exists(path):
        raise DataFileError(f"File not found: {path}")
    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            if header is None:
                raise DataFileError("The file is empty.")
            header = [h.strip() for h in header]
            if [h.lower() for h in header[:2]] != REQUIRED_COLUMNS:
                raise DataFileError("The first two columns must be 'roll_no' and 'name'.")
            subjects = header[2:]
            try:
                book = ResultBook(subjects)
            except ValidationError as exc:
                raise DataFileError(f"Invalid header: {exc}") from exc

            errors = []
            for row in reader:
                line = reader.line_num
                if not any(cell.strip() for cell in row):
                    continue  # ignore blank lines
                if len(row) != len(header):
                    errors.append(f"Line {line}: expected {len(header)} columns, found {len(row)}.")
                    continue
                roll_no, name, *marks = row
                try:
                    book.add_student(roll_no, name, dict(zip(subjects, marks)))
                except AnalyzerError as exc:
                    errors.append(f"Line {line}: {exc}")
    except UnicodeDecodeError:
        raise DataFileError("File is not valid UTF-8 text. Save it as CSV (UTF-8).") from None
    except OSError as exc:
        raise DataFileError(f"Could not read file: {exc}") from exc
    return book, errors


def save_csv(book, path):
    """Save raw marks back to CSV in the same format load_csv reads."""
    try:
        folder = os.path.dirname(os.path.abspath(path))
        os.makedirs(folder, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(REQUIRED_COLUMNS + book.subjects)
            for s in book.students.values():
                marks = ["AB" if s.marks[sub] is None else s.marks[sub] for sub in book.subjects]
                writer.writerow([s.roll_no, s.name, *marks])
    except OSError as exc:
        raise DataFileError(f"Could not save file: {exc}") from exc
