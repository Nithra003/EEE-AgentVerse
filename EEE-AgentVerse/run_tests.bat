@echo off
REM run_tests.bat — Run full ElderCare AI test suite with coverage report

echo ============================================================
echo  ElderCare AI — Test Suite (Target: 95%% Coverage)
echo ============================================================

cd /d "%~dp0"

echo.
echo [1/3] Installing test dependencies...
pip install -r tests\requirements-test.txt -q

echo.
echo [2/3] Running tests...
python -m pytest tests\ ^
    --tb=short ^
    -v ^
    --cov=Agent-3-Appointment-Booking ^
    --cov=Agent-1-Medicine-Reminder ^
    --cov=Agent-4-Prescription-Explainer ^
    --cov=Agent-10-Voice-Assistant ^
    --cov=Agent-11-Medical-Assistant ^
    --cov-report=term-missing ^
    --cov-report=html:coverage_html ^
    --cov-report=xml:coverage.xml ^
    --cov-fail-under=95

echo.
echo [3/3] Coverage report saved to: coverage_html\index.html
echo ============================================================
pause
