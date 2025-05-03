#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Run pytest with coverage
# --cov=app: Measure coverage for the 'app' directory
# --cov-report=: Don't generate reports directly from pytest, we'll do it manually
# -v: Verbose output
pytest --cov=app --cov-report= -v

# Combine parallel coverage data files (if any)
echo "Combining coverage data..."
coverage combine

# Generate reports from the combined data
echo "Generating coverage reports..."
coverage report --show-missing
coverage html

echo "Test run completed."
