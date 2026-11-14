#!/usr/bin/env python3
"""
tests/run_e2e_tests.py
Standalone CLI Test Runner for Management Cards Chapter 02 E2E Test Suite.

Features:
- Direct PowerShell invocation: `python tests/run_e2e_tests.py`
- Discovers and executes all test tiers (Tiers 1, 2, 3, 4)
- Supports tier selection via CLI (`--tier 1`, `--tier 1 2`, `--tier all`)
- Supports pattern filter (`-k FILTER`), fail-fast (`-f`), verbose (`-v`), quiet (`-q`)
- Pretty-prints structured summary table with tier breakdowns, timings, and status
- Detailed failure/error reporting with exact stack traces
- Native exit code semantics: 0 on 100% pass, non-zero on any failure
"""

from __future__ import annotations
import sys
import os
import time
import argparse
import unittest
import importlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any, Iterator

# ---------------------------------------------------------------------------
# Path Bootstrapping
# ---------------------------------------------------------------------------
TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent

if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Enable ANSI escape sequences on Windows PowerShell/CMD
if os.name == "nt":
    os.system("")

# ---------------------------------------------------------------------------
# ANSI Terminal Colors
# ---------------------------------------------------------------------------
class Color:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    @classmethod
    def disable(cls):
        cls.GREEN = ""
        cls.RED = ""
        cls.YELLOW = ""
        cls.BLUE = ""
        cls.CYAN = ""
        cls.BOLD = ""
        cls.DIM = ""
        cls.RESET = ""


# ---------------------------------------------------------------------------
# Tier Module Mapping
# ---------------------------------------------------------------------------
TIER_DEFINITIONS = {
    1: {
        "name": "Tier 1: Feature Coverage (F1-F6)",
        "module": "test_tier1_features",
        "description": "Equivalence-class unit tests covering features F1 through F6 (>=30 tests)",
        "min_expected": 30,
    },
    2: {
        "name": "Tier 2: Boundary & Corner Cases",
        "module": "test_tier2_boundaries",
        "description": "Edge conditions, 4 vs 5 choices, 20 boxed questions, outliers (>=30 tests)",
        "min_expected": 30,
    },
    3: {
        "name": "Tier 3: Cross-Feature Combinations",
        "module": "test_tier3_combinations",
        "description": "Pairwise interactions: boxed statements + options + tokens.css (>=6 tests)",
        "min_expected": 6,
    },
    4: {
        "name": "Tier 4: Real-World Workload Scenarios",
        "module": "test_tier4_scenarios",
        "description": "Exhaustive scans across all 231 cards in Chapter 02 (>=5 tests)",
        "min_expected": 5,
    },
}


# ---------------------------------------------------------------------------
# Custom Test Result Collector
# ---------------------------------------------------------------------------
class TierTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_timings: Dict[str, float] = {}
        self._test_start: float = 0.0

    def startTest(self, test: unittest.TestCase):
        super().startTest(test)
        self._test_start = time.perf_counter()

    def addSuccess(self, test: unittest.TestCase):
        super().addSuccess(test)
        duration = time.perf_counter() - self._test_start
        self.test_timings[test.id()] = duration

    def addFailure(self, test: unittest.TestCase, err):
        super().addFailure(test, err)
        duration = time.perf_counter() - self._test_start
        self.test_timings[test.id()] = duration

    def addError(self, test: unittest.TestCase, err):
        super().addError(test, err)
        duration = time.perf_counter() - self._test_start
        self.test_timings[test.id()] = duration


# ---------------------------------------------------------------------------
# Test Suite Traversal Helper
# ---------------------------------------------------------------------------
def _iter_tests(suite_or_case: Any) -> Iterator[unittest.TestCase]:
    """Recursively yields test cases from nested TestSuite objects."""
    if isinstance(suite_or_case, unittest.TestSuite):
        for sub in suite_or_case:
            yield from _iter_tests(sub)
    elif isinstance(suite_or_case, unittest.TestCase):
        yield suite_or_case


# ---------------------------------------------------------------------------
# Tier Runner & Stats Aggregator
# ---------------------------------------------------------------------------
@dataclass
class TierExecutionSummary:
    tier_num: int
    name: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    duration: float = 0.0
    status: str = "PASS"
    failures_details: List[Tuple[Any, str]] = field(default_factory=list)
    errors_details: List[Tuple[Any, str]] = field(default_factory=list)
    import_error: Optional[str] = None


def run_tier(
    tier_num: int,
    verbose: bool = False,
    failfast: bool = False,
    pattern: Optional[str] = None,
    stream=sys.stdout
) -> TierExecutionSummary:
    """Executes a single test tier and returns structured metrics."""
    tier_info = TIER_DEFINITIONS[tier_num]
    summary = TierExecutionSummary(tier_num=tier_num, name=tier_info["name"])

    module_name = tier_info["module"]
    t0 = time.perf_counter()

    try:
        module = importlib.import_module(module_name)
    except Exception as e:
        summary.duration = time.perf_counter() - t0
        summary.status = "FAIL"
        summary.import_error = f"Failed to import {module_name}: {str(e)}"
        summary.total = 1
        summary.failed = 1
        summary.errors_details.append((module_name, summary.import_error))
        return summary

    loader = unittest.defaultTestLoader
    raw_suite = loader.loadTestsFromModule(module)

    if pattern:
        suite = unittest.TestSuite()
        for test in _iter_tests(raw_suite):
            if pattern.lower() in test.id().lower():
                suite.addTest(test)
    else:
        suite = raw_suite

    summary.total = suite.countTestCases()
    if summary.total == 0:
        summary.duration = time.perf_counter() - t0
        summary.status = "EMPTY"
        return summary

    verbosity_level = 2 if verbose else 1
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=verbosity_level,
        failfast=failfast,
        resultclass=TierTestResult
    )

    result: TierTestResult = runner.run(suite)
    summary.duration = time.perf_counter() - t0
    summary.failed = len(result.failures)
    summary.errors = len(result.errors)
    summary.skipped = len(result.skipped)
    executed = result.testsRun
    summary.passed = max(0, executed - summary.failed - summary.errors - summary.skipped)
    summary.failures_details = list(result.failures)
    summary.errors_details = list(result.errors)

    if summary.failed > 0 or summary.errors > 0:
        summary.status = "FAIL"
    else:
        summary.status = "PASS"

    return summary


# ---------------------------------------------------------------------------
# Summary Table Formatter
# ---------------------------------------------------------------------------
def print_summary_table(summaries: List[TierExecutionSummary]) -> None:
    """Prints a structured, formatted summary table to stdout."""
    col_tier = 40
    col_total = 8
    col_pass = 8
    col_fail = 8
    col_skip = 8
    col_dur = 11
    col_stat = 10

    line_width = (
        col_tier + col_total + col_pass + col_fail + col_skip + col_dur + col_stat + 6
    )

    print()
    print("=" * line_width)
    title = "MANAGEMENT CARDS E2E TEST EXECUTION REPORT"
    print(f"{Color.BOLD}{title.center(line_width)}{Color.RESET}")
    print("=" * line_width)
    header = (
        f"{'Tier':<{col_tier}} "
        f"{'Total':>{col_total}} "
        f"{'Passed':>{col_pass}} "
        f"{'Failed':>{col_fail}} "
        f"{'Skipped':>{col_skip}} "
        f"{'Duration':>{col_dur}} "
        f"{'Status':>{col_stat}}"
    )
    print(header)
    print("-" * line_width)

    grand_total = 0
    grand_passed = 0
    grand_failed = 0
    grand_skipped = 0
    grand_duration = 0.0

    for s in summaries:
        grand_total += s.total
        grand_passed += s.passed
        grand_failed += s.failed + s.errors
        grand_skipped += s.skipped
        grand_duration += s.duration

        dur_str = f"{s.duration:.2f}s"
        if s.status == "PASS":
            status_badge = f"{Color.GREEN}{Color.BOLD}{'PASS':>{col_stat}}{Color.RESET}"
        elif s.status == "EMPTY":
            status_badge = f"{Color.YELLOW}{'NO TESTS':>{col_stat}}{Color.RESET}"
        else:
            status_badge = f"{Color.RED}{Color.BOLD}{'FAIL':>{col_stat}}{Color.RESET}"

        row = (
            f"{s.name:<{col_tier}} "
            f"{s.total:>{col_total}} "
            f"{s.passed:>{col_pass}} "
            f"{(s.failed + s.errors):>{col_fail}} "
            f"{s.skipped:>{col_skip}} "
            f"{dur_str:>{col_dur}} "
            f"{status_badge}"
        )
        print(row)

    print("-" * line_width)
    tot_dur_str = f"{grand_duration:.2f}s"
    if grand_total == 0:
        overall_status = f"{Color.YELLOW}{Color.BOLD}{'NO TESTS':>{col_stat}}{Color.RESET}"
    elif grand_failed == 0:
        overall_status = f"{Color.GREEN}{Color.BOLD}{'ALL PASS':>{col_stat}}{Color.RESET}"
    else:
        overall_status = f"{Color.RED}{Color.BOLD}{'FAILURE':>{col_stat}}{Color.RESET}"

    total_row = (
        f"{Color.BOLD}{'TOTAL':<{col_tier}}{Color.RESET} "
        f"{Color.BOLD}{grand_total:>{col_total}}{Color.RESET} "
        f"{Color.BOLD}{grand_passed:>{col_pass}}{Color.RESET} "
        f"{Color.BOLD}{grand_failed:>{col_fail}}{Color.RESET} "
        f"{Color.BOLD}{grand_skipped:>{col_skip}}{Color.RESET} "
        f"{Color.BOLD}{tot_dur_str:>{col_dur}}{Color.RESET} "
        f"{overall_status}"
    )
    print(total_row)
    print("=" * line_width)
    print()


def print_failure_diagnostics(summaries: List[TierExecutionSummary]) -> None:
    """Prints detailed tracebacks for any failed or errored tests."""
    has_issues = any((s.failed > 0 or s.errors > 0 or s.import_error) for s in summaries)
    if not has_issues:
        return

    print(f"\n{Color.RED}{Color.BOLD}{'=' * 30} FAILURES & ERRORS {'=' * 30}{Color.RESET}\n")

    for s in summaries:
        if s.import_error:
            print(f"{Color.RED}[MODULE LOAD ERROR - {s.name}]{Color.RESET}")
            print(f"  {s.import_error}\n")
            continue

        for test_case, tb in s.failures_details:
            print(f"{Color.RED}[FAIL]{Color.RESET} {Color.BOLD}{test_case}{Color.RESET}")
            for line in tb.strip().splitlines():
                print(f"    {line}")
            print("-" * 70)

        for test_case, tb in s.errors_details:
            print(f"{Color.RED}[ERROR]{Color.RESET} {Color.BOLD}{test_case}{Color.RESET}")
            for line in tb.strip().splitlines():
                print(f"    {line}")
            print("-" * 70)


# ---------------------------------------------------------------------------
# CLI Argument Parsing & Main Entry Point
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Management Cards Chapter 02 E2E Test Suite Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--tier", "-t",
        nargs="*",
        default=["all"],
        help="Test tier(s) to execute: 1, 2, 3, 4, or all (e.g. --tier 1, --tier 1 2). Default: all.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose test execution output showing each test method name.",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Quiet execution (suppresses individual test dots, prints only final summary).",
    )
    parser.add_argument(
        "-f", "--failfast",
        action="store_true",
        help="Stop on first test failure within any tier.",
    )
    parser.add_argument(
        "-k", "--filter",
        type=str,
        default=None,
        help="Pattern filter matching test names/IDs (substring match).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors in console output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.no_color or not sys.stdout.isatty():
        Color.disable()

    # Normalize tier arguments
    raw_tiers = []
    for item in args.tier:
        for part in item.replace(",", " ").split():
            raw_tiers.append(part.lower())

    if "all" in raw_tiers:
        selected_tiers = [1, 2, 3, 4]
    else:
        try:
            selected_tiers = sorted(list(set(int(t) for t in raw_tiers)))
        except ValueError:
            print(f"{Color.RED}Error: Invalid tier selection '{args.tier}'. Choose from 1, 2, 3, 4, or all.{Color.RESET}")
            return 2

    # Validation
    for t in selected_tiers:
        if t not in TIER_DEFINITIONS:
            print(f"{Color.RED}Error: Tier {t} is invalid. Choose from 1, 2, 3, 4.{Color.RESET}")
            return 2

    devnull = open(os.devnull, "w") if args.quiet else None
    stream = devnull if args.quiet else sys.stdout

    summaries: List[TierExecutionSummary] = []
    total_failures = 0

    print(f"\n{Color.CYAN}{Color.BOLD}>>> Launching E2E Test Suite for Chapter 02 (Tiers: {selected_tiers}) <<<{Color.RESET}\n")

    for t in selected_tiers:
        print(f"{Color.BOLD}Running {TIER_DEFINITIONS[t]['name']}...{Color.RESET}")
        summary = run_tier(
            tier_num=t,
            verbose=args.verbose,
            failfast=args.failfast,
            pattern=args.filter,
            stream=stream,
        )
        summaries.append(summary)
        total_failures += (summary.failed + summary.errors)

        if args.failfast and total_failures > 0:
            print(f"\n{Color.RED}Fail-fast triggered in Tier {t}. Halting remaining tiers.{Color.RESET}")
            break

    if devnull:
        devnull.close()

    # Formatted Reporting
    print_summary_table(summaries)
    print_failure_diagnostics(summaries)

    # Exit code determination
    total_tests = sum(s.total for s in summaries)
    if total_failures > 0:
        print(f"{Color.RED}{Color.BOLD}❌ TEST SUITE FAILED ({total_failures} failure(s)/error(s)){Color.RESET}\n")
        return 1
    elif total_tests == 0:
        print(f"{Color.YELLOW}{Color.BOLD}⚠️  NO TESTS WERE EXECUTED.{Color.RESET}\n")
        return 0
    else:
        print(f"{Color.GREEN}{Color.BOLD}✅ ALL TESTS PASSED SUCCESSFULLY!{Color.RESET}\n")
        return 0


if __name__ == "__main__":
    sys.exit(main())
