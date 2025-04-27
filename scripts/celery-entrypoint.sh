#!/bin/bash
set -e

# Install six and fix vendor package issue
pip install --no-cache-dir six==1.16.0
# Create vendor directory if it doesn't exist
mkdir -p /.venv/lib/python3.12/site-packages/kafka/vendor
# Create __init__.py in the vendor directory if it doesn't exist
touch /.venv/lib/python3.12/site-packages/kafka/vendor/__init__.py
# Create symlink to the six module
ln -sf /.venv/lib/python3.12/site-packages/six.py /.venv/lib/python3.12/site-packages/kafka/vendor/six.py

echo "Starting Celery worker..."
exec python worker.py