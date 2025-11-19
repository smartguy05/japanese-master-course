#!/bin/bash
set -e

# =============================================================================
# Nihongo Sensei - Test All Script
# =============================================================================
# This script runs all backend and frontend tests with coverage
# Usage: ./scripts/test_all.sh [--verbose]
# =============================================================================

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

VERBOSE=false
if [[ "$1" == "--verbose" ]] || [[ "$1" == "-v" ]]; then
    VERBOSE=true
fi

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          Nihongo Sensei - Test Suite Runner                  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# =============================================================================
# Backend Tests
# =============================================================================

echo "🐍 Running Backend Tests..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$PROJECT_ROOT/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
else
    source venv/bin/activate
fi

# Run backend tests with coverage
if [ "$VERBOSE" = true ]; then
    pytest tests/ \
        --cov=app \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --cov-report=json:coverage.json \
        -v
else
    pytest tests/ \
        --cov=app \
        --cov-report=term-missing \
        --cov-report=html:htmlcov \
        --cov-report=json:coverage.json
fi

BACKEND_EXIT_CODE=$?

# Extract coverage percentage
BACKEND_COVERAGE=$(python -c "import json; print(json.load(open('coverage.json'))['totals']['percent_covered'])" 2>/dev/null || echo "0")

echo ""
if [ $BACKEND_EXIT_CODE -eq 0 ]; then
    echo "✅ Backend tests passed! Coverage: ${BACKEND_COVERAGE}%"
else
    echo "❌ Backend tests failed!"
fi

echo ""
echo "📊 Backend coverage report: backend/htmlcov/index.html"
echo ""

# Deactivate virtual environment
deactivate

# =============================================================================
# Frontend Tests
# =============================================================================

echo "⚛️  Running Frontend Tests..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$PROJECT_ROOT/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "⚠️  node_modules not found. Installing dependencies..."
    npm install
fi

# Run frontend tests with coverage
if [ "$VERBOSE" = true ]; then
    npm test -- --coverage --watchAll=false --verbose
else
    npm test -- --coverage --watchAll=false
fi

FRONTEND_EXIT_CODE=$?

# Extract coverage percentage
FRONTEND_COVERAGE=$(node -e "
const coverage = require('./coverage/coverage-summary.json');
const total = coverage.total;
console.log(total.lines.pct);
" 2>/dev/null || echo "0")

echo ""
if [ $FRONTEND_EXIT_CODE -eq 0 ]; then
    echo "✅ Frontend tests passed! Coverage: ${FRONTEND_COVERAGE}%"
else
    echo "❌ Frontend tests failed!"
fi

echo ""
echo "📊 Frontend coverage report: frontend/coverage/index.html"
echo ""

# =============================================================================
# Test Summary
# =============================================================================

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                   Test Summary                                ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Backend summary
if [ $BACKEND_EXIT_CODE -eq 0 ]; then
    echo "🐍 Backend:  ✅ PASSED  (Coverage: ${BACKEND_COVERAGE}%)"
else
    echo "🐍 Backend:  ❌ FAILED  (Coverage: ${BACKEND_COVERAGE}%)"
fi

# Check backend coverage threshold
BACKEND_THRESHOLD=85
if (( $(echo "$BACKEND_COVERAGE >= $BACKEND_THRESHOLD" | bc -l) )); then
    echo "             ✅ Coverage above threshold (${BACKEND_THRESHOLD}%)"
else
    echo "             ⚠️  Coverage below threshold (${BACKEND_THRESHOLD}%)"
fi

echo ""

# Frontend summary
if [ $FRONTEND_EXIT_CODE -eq 0 ]; then
    echo "⚛️  Frontend: ✅ PASSED  (Coverage: ${FRONTEND_COVERAGE}%)"
else
    echo "⚛️  Frontend: ❌ FAILED  (Coverage: ${FRONTEND_COVERAGE}%)"
fi

# Check frontend coverage threshold
FRONTEND_THRESHOLD=85
if (( $(echo "$FRONTEND_COVERAGE >= $FRONTEND_THRESHOLD" | bc -l) )); then
    echo "             ✅ Coverage above threshold (${FRONTEND_THRESHOLD}%)"
else
    echo "             ⚠️  Coverage below threshold (${FRONTEND_THRESHOLD}%)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Exit with error if any tests failed
if [ $BACKEND_EXIT_CODE -ne 0 ] || [ $FRONTEND_EXIT_CODE -ne 0 ]; then
    echo "❌ Some tests failed. Please fix before committing."
    echo ""
    exit 1
else
    echo "✅ All tests passed successfully!"
    echo ""

    # Check if both meet coverage threshold
    if (( $(echo "$BACKEND_COVERAGE >= $BACKEND_THRESHOLD" | bc -l) )) && \
       (( $(echo "$FRONTEND_COVERAGE >= $FRONTEND_THRESHOLD" | bc -l) )); then
        echo "🎉 All tests passed and coverage thresholds met!"
    else
        echo "⚠️  Tests passed but coverage below threshold in some areas"
        exit 1
    fi
fi

echo ""
echo "Test run completed at: $(date)"
