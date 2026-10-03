"""Input validation helpers.

Each function returns a cleaned value or raises ValidationError with a
message that can be shown directly to the user.
"""

import re

from .exceptions import ValidationError

ROLL_PATTERN = re.compile(r"^[A-Z0-9]{2,15}$")
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'-]*$")
SUBJECT_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9 &.-]*$")
ABSENT_TOKENS = {"AB", "ABS", "ABSENT"}

MIN_MARK = 0
MAX_MARK = 100


def validate_non_empty(value, field):
    if value is None or not str(value).strip():
        raise ValidationError(f"{field} cannot be empty.")
    return " ".join(str(value).split())


def validate_roll_no(value):
    value = validate_non_empty(value, "Roll number").upper().replace(" ", "")
    if not ROLL_PATTERN.match(value):
        raise ValidationError("Roll number must be 2-15 letters/digits (e.g. 21CS001).")
    return value


def validate_name(value):
    value = validate_non_empty(value, "Name")
    if len(value) > 60:
        raise ValidationError("Name must be at most 60 characters.")
    if not NAME_PATTERN.match(value):
        raise ValidationError("Name may contain only letters, spaces, dots, apostrophes and hyphens.")
    return value.title()


def validate_subject(value):
    value = validate_non_empty(value, "Subject")
    if len(value) > 30:
        raise ValidationError("Subject name must be at most 30 characters.")
    if not SUBJECT_PATTERN.match(value):
        raise ValidationError(f"Subject name '{value}' contains invalid characters.")
    return value.title()


def validate_mark(value, subject="Mark"):
    """Return an int 0-100, or None for an absent student ('AB')."""
    text = validate_non_empty(value, f"{subject} mark").upper()
    if text in ABSENT_TOKENS:
        return None
    try:
        number = float(text)
    except ValueError:
        raise ValidationError(f"{subject} mark '{value}' is not a number (use AB for absent).") from None
    if not number.is_integer():
        raise ValidationError(f"{subject} mark must be a whole number, got {value}.")
    number = int(number)
    if not MIN_MARK <= number <= MAX_MARK:
        raise ValidationError(f"{subject} mark must be between {MIN_MARK} and {MAX_MARK}, got {number}.")
    return number


def validate_positive_int(value, field, maximum=None):
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be a whole number.") from None
    if number < 1:
        raise ValidationError(f"{field} must be at least 1.")
    if maximum is not None and number > maximum:
        raise ValidationError(f"{field} must be at most {maximum}.")
    return number
