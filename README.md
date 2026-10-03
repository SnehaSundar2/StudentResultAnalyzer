# Student Result Analyzer

A menu-driven Python application that turns a class's raw marks into results: totals,
percentages, grades, GPA, pass/fail, ranks, subject-wise statistics and printable reports.

Built as a virtual internship project to demonstrate **Python modules, input validation,
data processing and error handling**. It uses only the Python standard library, so there is
nothing to install.

---

## 1. Features

| Area | What it does |
|---|---|
| **Data entry** | Load marks from CSV, add students, update marks, remove students, search, save back to CSV |
| **Results** | Total, percentage, grade, GPA and PASS/FAIL for every student |
| **Ranking** | Passed students ranked by total, then GPA; equal scores share a rank (1, 2, 2, 4) |
| **Class analysis** | Pass rate, average, median, highest, lowest, standard deviation |
| **Subject analysis** | Average, median, highest, lowest, std dev, pass %, absentees and topper per subject; hardest subject |
| **Insights** | Top performers, students needing support (with failed subjects), grade distribution chart |
| **Reports** | Full text report and ranked results CSV |
| **Bad-data handling** | Invalid CSV rows are skipped and reported with line numbers; the rest still load |
| **Logging** | Every action and error recorded in `analyzer.log` |

### Grading rules

| Percentage / mark | Grade | Grade point |
|---|---|---|
| 90 – 100 | O | 10 |
| 80 – 89 | A+ | 9 |
| 70 – 79 | A | 8 |
| 60 – 69 | B+ | 7 |
| 50 – 59 | B | 6 |
| 40 – 49 | C | 5 |
| 35 – 39 | P | 4 |
| below 35 / absent | F | 0 |

- **Pass mark:** 35 in **every** subject. Failing or being absent in any subject means FAIL.
- **Percentage** = total ÷ (100 × number of subjects) × 100.
- **GPA** = average of the subject grade points.
- **Overall grade** comes from the percentage, and is F for any student who failed.
- Absent (`AB`) counts as 0 in the total but is excluded from subject averages.

---

## 2. Project structure

```
StudentResultAnalyzer/
├── main.py                  # Entry point: options, logging, report-only mode
├── analyzer/                # The application package
│   ├── __init__.py
│   ├── exceptions.py        # Custom exception hierarchy
│   ├── validators.py        # Input validation functions
│   ├── models.py            # Student + ResultBook (validated class data)
│   ├── grading.py           # Grade scale, pass mark, per-student result
│   ├── loader.py            # CSV import (row-level error reporting) and save
│   ├── analysis.py          # Ranks, class/subject statistics, insights
│   ├── reports.py           # Text report, tables, results CSV export
│   └── cli.py               # Interactive menu
├── sample_data/
│   └── students.csv         # 12 valid students + 3 deliberately bad rows
├── tests/                   # 35 automated tests
└── docs/
    └── PROJECT_REPORT.md    # Internship submission report
```

---

## 3. How to run

Requires **Python 3.8 or newer**.

```bash
cd StudentResultAnalyzer
python main.py --file sample_data/students.csv
```

One-shot report without the menu:

```bash
python main.py --file sample_data/students.csv --report reports/result_report.txt --csv reports/results.csv
```

| Option | Purpose |
|---|---|
| `--file PATH` | Load a marks CSV at start-up |
| `--report PATH` | Print and save the full text report, then exit (needs `--file`) |
| `--csv PATH` | With `--report`, also export the ranked results as CSV |

### CSV format

```
roll_no,name,Maths,Physics,Chemistry,English,Computer Science
21CS001,Asha Kumar,95,88,91,84,98
21CS008,Vikram Singh,33,40,28,45,AB
```

The first two columns must be `roll_no` and `name`. Every column after that is a subject
(1–12 subjects). Marks are whole numbers 0–100, or `AB` for absent. Files saved from Excel as
"CSV UTF-8" work directly.

---

## 4. Workflow

```
   ┌──────────────────────┐
   │  marks CSV / manual  │
   │        entry         │
   └──────────┬───────────┘
              ▼
   ┌──────────────────────┐   bad row → skipped, reported as
   │ loader.py / cli.py   │   "Line 14: Maths mark must be between 0 and 100"
   │  read the raw input  │──────────────────────────────────────┐
   └──────────┬───────────┘                                      │
              ▼                                                  │
   ┌──────────────────────┐   ValidationError / DuplicateStudent │
   │ validators.py checks │   → friendly "! Error: ..." message  │
   │ roll no, name, marks │──────────────────────────────────────┤
   └──────────┬───────────┘                                      │
              ▼                                                  │
   ┌──────────────────────┐                                      │
   │ models.ResultBook    │  only clean data is stored           │
   └──────────┬───────────┘                                      │
              ▼                                                  ▼
   ┌──────────────────────┐                          ┌───────────────────┐
   │ grading.py           │ total, %, GPA, grade,    │ analyzer.log      │
   │ analysis.py          │ pass/fail, ranks, stats  │ (warnings/errors) │
   └──────────┬───────────┘                          └───────────────────┘
              ▼
   ┌──────────────────────┐
   │ reports.py / cli.py  │ screen tables, report card,
   │                      │ text report, results CSV
   └──────────────────────┘
```

### Typical session

1. **Load** the class marks (option 1). Any rejected rows are listed with the reason.
2. Fix mistakes: **update a mark** (option 3), **add** a late entry (option 2) or **remove** a
   student (option 4), then **save** (option 6).
3. View the **class result table** (option 7) and individual **report cards** (option 8).
4. Use **subject analysis** (option 9), **top performers** (option 10), **failed students**
   (option 11) and the **grade distribution** (option 12).
5. **Export** the full text report (option 13) and ranked results CSV (option 14).

---

## 5. Key concepts demonstrated

**Python modules.** Each module has one job. `grading.py` holds the rules, `analysis.py` does
the calculations, `loader.py` handles files and `cli.py` handles the user. Changing the grade
scale means editing one list in `grading.py`.

**Input validation.** Roll numbers, names, subject names and marks are cleaned (spaces, case)
and checked. Marks must be whole numbers 0–100 or `AB`. Each student must have a mark for every
subject and no unknown subjects. Roll numbers and subject names must be unique.

**Data processing.** The `statistics` module provides mean, median and standard deviation;
`collections.Counter` gives the grade distribution. Competition-style ranking handles ties, and
absent students are excluded from subject averages.

**Error handling**
- A custom exception hierarchy: `AnalyzerError` → `ValidationError`, `DuplicateStudentError`,
  `StudentNotFoundError`, `DataFileError`, `NoDataError`.
- **Row-level recovery:** one bad row doesn't stop the import; each problem is reported with
  its line number.
- **File-level errors** (missing file, empty file, wrong header, non-UTF-8 encoding,
  permission problems) become clear `DataFileError` messages.
- The CLI catches every `AnalyzerError` and shows it. Unexpected exceptions are logged with a
  full traceback while the menu keeps running. Ctrl+C cancels the current action.

---

## 6. Testing

```bash
cd StudentResultAnalyzer
python -m unittest discover -s tests -t . -v
```

Result: **35 tests, all passing.**

| Test file | Tests | Covers |
|---|---|---|
| `test_validators.py` | 7 | Roll no, name, subject, marks (range, decimals, absent tokens) |
| `test_models_grading.py` | 10 | Adding/updating/removing students, duplicates, grade boundaries, pass/fail/absent results |
| `test_analysis.py` | 8 | Ranking with ties and GPA tie-break, class and subject stats, distribution, empty data |
| `test_io.py` | 10 | CSV good/bad rows, missing/empty/wrong-header/non-UTF-8 files, save round-trip, reports, CLI sessions |
