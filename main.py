"""Entry point for the Student Result Analyzer.

Usage:
    python main.py                                  # interactive menu
    python main.py --file sample_data/students.csv  # load a file, then menu
    python main.py --file data.csv --report out.txt # print + save report, no menu
"""

import argparse
import logging
import sys

from analyzer import loader, reports
from analyzer.cli import AnalyzerCLI
from analyzer.exceptions import AnalyzerError


def main(argv=None):
    parser = argparse.ArgumentParser(description="Student Result Analyzer")
    parser.add_argument("--file", help="CSV file of student marks to load at start-up")
    parser.add_argument("--report", metavar="PATH",
                        help="generate a text report to PATH and exit (requires --file)")
    parser.add_argument("--csv", metavar="PATH", help="also export ranked results CSV (with --report)")
    args = parser.parse_args(argv)

    logging.basicConfig(filename="analyzer.log", level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")

    if args.report and not args.file:
        parser.error("--report requires --file")

    book = None
    if args.file:
        try:
            book, errors = loader.load_csv(args.file)
        except AnalyzerError as exc:
            print(f"Could not load {args.file}: {exc}")
            return 1
        print(f"Loaded {len(book)} student(s) from {args.file}.")
        for e in errors:
            print(f"  skipped - {e}")

    if args.report:
        try:
            print(reports.build_text_report(book))
            reports.save_text_report(book, args.report)
            print(f"\nReport saved to {args.report}")
            if args.csv:
                reports.export_results_csv(book, args.csv)
                print(f"Results CSV saved to {args.csv}")
        except AnalyzerError as exc:
            print(f"Report failed: {exc}")
            return 1
        return 0

    try:
        AnalyzerCLI(book, args.file).run()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
