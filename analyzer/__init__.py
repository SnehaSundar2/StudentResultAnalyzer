"""Student Result Analyzer.

A modular command-line tool that loads student marks, validates them,
computes grades, ranks and class statistics, and exports reports.
"""

__version__ = "1.0.0"

import logging

# Stay silent unless the application (main.py) configures logging.
logging.getLogger("analyzer").addHandler(logging.NullHandler())
