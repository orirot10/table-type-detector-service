#!/usr/bin/env bash

set -euo pipefail

echo "📦 Activating virtual environment (if exists)..."
if [ -d "venv" ]; then
    source venv/bin/activate || true
fi

echo "🔍 Running style checks (flake8 if installed)..."
if command -v flake8 >/dev/null 2>&1; then
    flake8 app tests || {
        echo "❌ flake8 failed"
        exit 1
    }
else
    echo "⚠ flake8 not installed — skipping style check"
fi

echo "🧪 Running pytest..."
pytest --maxfail=1 --disable-warnings -q

status=$?

if [ $status -eq 0 ]; then
    echo "✨ All tests passed successfully!"
else
    echo "❌ Some tests failed"
fi

exit $status
