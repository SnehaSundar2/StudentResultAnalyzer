# Project Report: Student Result Analyzer

**Program:** Virtual Internship – Python Development
**Project:** Student Result Analyzer
**Submitted by:** _[Your Name]_
**Date:** _[Submission Date]_

---

## 1. Introduction

After every exam, teachers spend hours with spreadsheets working out totals, percentages,
grades and ranks, and finding which students and subjects need attention. Manual calculation
is slow, and mistakes such as a typo in a mark, a duplicated roll number or a missed absentee are
easy to make. This project automates that work with a Python command-line tool that validates
the marks, computes results and produces analysis reports.

## 2. Objectives

1. Build a working result analyzer from clearly separated Python modules.
2. Validate every input so incorrect marks never reach the results.
3. Process marks into results, ranks and class- and subject-level statistics.
4. Handle errors in data files and user input gracefully, without crashing.
5. Document the workflow and verify the behaviour with automated tests.

## 3. Tools and technologies

| Item | Used |
|---|---|
| Language | Python 3 (tested on 3.13) |
| Libraries | Standard library only: `csv`, `statistics`, `collections`, `dataclasses`, `re`, `logging`, `argparse`, `unittest` |
| Input/Output | CSV files (Excel-compatible), text reports |
| Testing | `unittest`, `unittest.mock` |

## 4. System design

### 4.1 Modules

| Module | Responsibility |
|---|---|
| `main.py` | Starts the app; handles command-line options and report-only mode |
| `cli.py` | Menu, prompts, on-screen tables, report card |
| `validators.py` | Validates and cleans roll numbers, names, subjects and marks |
| `models.py` | `Student` and `ResultBook`, which only ever holds validated data |
| `grading.py` | Grade scale, pass mark, computing a student's result |
| `loader.py` | Reads and writes CSV; reports bad rows by line number |
| `analysis.py` | Ranking, class summary, subject statistics, insights |
| `reports.py` | Text report and results CSV |
| `exceptions.py` | Custom error types |

Data flows **CSV/keyboard → validators → ResultBook → grading/analysis → reports**.

### 4.2 Business rules

- Pass mark is 35 in every subject; absent counts as fail.
- Percentage = total / (100 × subjects) × 100. GPA = mean of subject grade points.
- Grades: O ≥ 90, A+ ≥ 80, A ≥ 70, B+ ≥ 60, B ≥ 50, C ≥ 40, P ≥ 35, otherwise F.
- Only passed students are ranked. Order is by total, then GPA, and equal scores share a rank.
- Subject averages exclude absentees. Subject pass rates count absentees as not passed.

## 5. Implementation highlights

**Validation.** `validate_mark` accepts `75`, `75.0` and `AB`/`Absent`, and rejects `75.5`,
`-1`, `101` and text. `ResultBook.add_student` rejects a student with a missing or unknown
subject, or a duplicate roll number, so the stored data is always complete and consistent.

**Error handling.** The CSV loader separates *file* problems (missing, empty, wrong header,
wrong encoding), which stop the import with a clear `DataFileError`, from *row* problems,
which skip just that row and report it:

```
Loaded 12 student(s) from sample_data/students.csv.
  skipped - Line 14: Maths mark must be between 0 and 100, got 105.
  skipped - Line 15: expected 7 columns, found 5.
  skipped - Line 16: Roll number 21CS001 already exists.
```

In the menu, every `AnalyzerError` is shown as `! Error: ...`, and unexpected errors are
written to `analyzer.log` while the program continues.

**Data processing.** Uses `statistics.mean`, `median` and `pstdev` for class and subject
statistics, and `Counter` for the grade distribution. Ranking with ties is implemented by
hand, and the report identifies the hardest subject and the students needing support.

## 6. Testing

35 automated tests were written and **all pass**.

| # | Test case | Expected | Result |
|---|---|---|---|
| 1 | Mark `101` / `-1` / `75.5` / `abc` | ValidationError | Pass |
| 2 | Mark `AB`, `absent` | Stored as absent | Pass |
| 3 | Student missing one subject's mark | ValidationError, not added | Pass |
| 4 | Duplicate roll number | DuplicateStudentError | Pass |
| 5 | Percentage 89.99 / 90 | A+ / O | Pass |
| 6 | 30 in one subject, high in others | FAIL, grade F, unranked | Pass |
| 7 | Two students with identical totals and GPA | Same rank, next rank skipped | Pass |
| 8 | Same total, different GPA | Higher GPA ranked first | Pass |
| 9 | CSV with bad rows mixed in | Good rows loaded, bad rows listed with line numbers | Pass |
| 10 | Missing / empty / wrong-header / non-UTF-8 file | DataFileError with clear message | Pass |
| 11 | Save then reload CSV | Identical data, including absentees | Pass |
| 12 | Analysis with no students | NoDataError | Pass |
| 13 | Invalid menu option, action before loading | Error message, menu continues | Pass |

## 7. Sample output (from `sample_data/students.csv`)

```
  CLASS SUMMARY
  Students: 12   Subjects: 5   Passed: 10   Failed: 2   Pass rate: 83.33%
  Average: 70.07%   Median: 71.5%   Highest: 91.2%   Lowest: 29.2%   Std dev: 18.04

  Hardest subject (lowest pass rate): Chemistry

  STUDENTS NEEDING SUPPORT
  21CS004   Karthik Raja          failed in: Chemistry (30)
  21CS008   Vikram Singh          failed in: Maths (33), Chemistry (28), Computer Science (AB)
```

## 8. Challenges and solutions

| Challenge | Solution |
|---|---|
| One bad row could stop the whole class import | Validate row by row; collect errors with line numbers |
| Fair ranking when students tie | Competition ranking on (total, GPA) |
| Absentees distorting subject averages | Store absent as `None`: excluded from averages, counted as fail |
| Excel CSVs with a hidden BOM character | Open files with the `utf-8-sig` encoding |
| Keeping the grade policy easy to change | Grade scale and pass mark defined once in `grading.py` |

## 9. Future enhancements

- Charts (matplotlib) for grade distribution and subject averages
- Excel (.xlsx) import/export
- Weighted subjects / credits for a credit-based GPA
- Comparing results across multiple exams to track progress
- A web interface (Flask) for teachers

## 10. Conclusion

The Student Result Analyzer meets all project objectives. It is organised into focused Python
modules, validates every mark and record, turns raw marks into meaningful results and
statistics, and recovers gracefully from bad data. The workflow is documented and the
behaviour is verified by 35 passing automated tests.

## 11. How to run

```bash
cd StudentResultAnalyzer
python main.py --file sample_data/students.csv
python -m unittest discover -s tests -t . -v
```
