"""Custom exception hierarchy.

Every deliberate error derives from AnalyzerError so the CLI can catch a
single base class and show a friendly message instead of a traceback.
"""


class AnalyzerError(Exception):
    """Base class for all analyzer errors."""


class ValidationError(AnalyzerError):
    """Raised when a value fails validation."""


class DuplicateStudentError(AnalyzerError):
    """Raised when a roll number already exists."""


class StudentNotFoundError(AnalyzerError):
    """Raised when a roll number does not exist."""


class DataFileError(AnalyzerError):
    """Raised when a data file is missing, unreadable or badly structured."""


class NoDataError(AnalyzerError):
    """Raised when an analysis is requested but there are no students."""
