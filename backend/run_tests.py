#!/usr/bin/env python3
"""
Test runner script for the Canada Immigration OS backend.
"""
import os
import subprocess
import sys
from pathlib import Path


def run_tests(coverage=True, verbose=True, specific_test=None):
    """Run the test suite with optional coverage reporting."""

    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(
            [
                "--cov=src",
                "--cov-report=html:htmlcov",
                "--cov-report=term-missing",
                "--cov-fail-under=80",
            ]
        )

    if specific_test:
        cmd.append(specific_test)
    else:
        cmd.append("tests/")

    print(f"Running command: {' '.join(cmd)}")
    print("=" * 60)

    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("✅ All tests passed!")

        if coverage:
            print("\n📊 Coverage report generated in htmlcov/index.html")

        return True

    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False


def run_specific_test_categories():
    """Run specific categories of tests."""
    categories = {
        "unit": "tests/unit",
        "integration": "tests/integration",
        "e2e": "tests/e2e",
        "legacy-services": "legacy/tests/test_services.py",
        "legacy-models": "legacy/tests/test_models_simple.py",
    }

    print("Available test categories:")
    print("  unit: Run pytest over tests/unit (fast feedback)")
    print("  integration: Run pytest over tests/integration (API/service coverage)")
    print("  e2e: Run pytest over tests/e2e (requires RUN_E2E=true + running services)")
    print("  legacy-services: Original services regression tests (now archived)")
    print("  legacy-models: Original model regression tests (now archived)")

    choice = input("\nEnter category name (or 'all' for all tests): ").strip().lower()

    if choice == "all":
        return run_tests()
    elif choice in categories:
        return run_tests(specific_test=categories[choice])
    else:
        print(f"Invalid choice: {choice}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--no-coverage":
            success = run_tests(coverage=False)
        elif sys.argv[1] == "--interactive":
            success = run_specific_test_categories()
        elif sys.argv[1].startswith("tests/"):
            success = run_tests(specific_test=sys.argv[1])
        else:
            print("Usage:")
            print("  python run_tests.py                    # Run all tests with coverage")
            print("  python run_tests.py --no-coverage      # Run all tests without coverage")
            print("  python run_tests.py --interactive      # Interactive test selection")
            print("  python run_tests.py tests/test_auth.py # Run specific test file")
            sys.exit(1)
    else:
        success = run_tests()

    sys.exit(0 if success else 1)
