@echo off
title ElderCare AI - AgentVerse Launcher
color 0A

echo.
echo ============================================================
echo   ElderCare AI - AgentVerse Launcher
echo   Starting all 10 agents + Dashboard
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/11] Starting Dashboard (port 8500)...
start "Dashboard" cmd /k "streamlit run dashboard.py --server.port 8500 --server.address 0.0.0.0 --server.headless true"
timeout /t 3 /nobreak >nul

echo [2/11] Starting Agent-1 Medicine Reminder (port 8501)...
start "Agent-1 Medicine Reminder" cmd /k "cd /d "%~dp0Agent-1-Medicine-Reminder" && streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true"
timeout /t 2 /nobreak >nul

echo [3/11] Starting Agent-2 Emergency Detection (port 8502)...
start "Agent-2 Emergency Detection" cmd /k "cd Agent-2-Emergency-Detection && streamlit run app.py --server.port 8502 --server.address 0.0.0.0 --server.headless true"
timeout /t 2 /nobreak >nul

echo [4/11] Starting Agent-3 Appointment Booking (port 8503)...
start "Agent-3 Appointment Booking" cmd /k "cd Agent-3-Appointment-Booking && streamlit run app.py --server.port 8503 --server.address 0.0.0.0 --server.headless true"
timeout /t 2 /nobreak >nul

echo [5/11] Starting Agent-4 Prescription Explainer (port 8504)...
start "Agent-4 Prescription Explainer" cmd /k "cd Agent-4-Prescription-Explainer && streamlit run app.py --server.port 8504 --server.address 0.0.0.0 --server.headless true"
timeout /t 2 /nobreak >nul

echo [6/11] Starting Agent-5 Health Report (port 8505)...
start "Agent-5 Health Report" cmd /k "cd Agent-5-Health-Report && streamlit run app.py --server.port 8505 --server.address 0.0.0.0 --server.headless true"
timeout /t 2 /nobreak >nul

echo [7/11] Starting Agent-6 Family Notifier (port 8506)...
start "Agent-6 Family Notifier" cmd /k "cd Agent-6-Family-Notifier && streamlit run app.py --server.port 8506 --server.address 0.0.0.0 --server.headless true"
timeout /t 2 /nobreak >nul

echo [8/11] Starting Agent-7 Diet Recommendation (port 8507)...
start "Agent-7 Diet Recommendation" cmd /k "cd Agent-7-Diet-Recommendation && streamlit run app.py --server.port 8507 --server.address 0.0.0.0 --server.headless true"
timeout /t 2 /nobreak >nul

echo [9/11] Starting Agent-8 Exercise Coach (port 8508)...
start "Agent-8 Exercise Coach" cmd /k "cd Agent-8-Exercise-Coach && streamlit run app.py --server.port 8508 --server.address 0.0.0.0 --server.headless true"
timeout /t 2 /nobreak >nul

echo [10/11] Starting Agent-9 Mood Companion (port 8509)...
start "Agent-9 Mood Companion" cmd /k "cd Agent-9-Mood-Companion && streamlit run app.py --server.port 8509 --server.address 0.0.0.0 --server.headless true"
timeout /t 2 /nobreak >nul

echo [11/11] Starting Agent-10 Voice Assistant (port 8510)...
start "Agent-10 Voice Assistant" cmd /k "cd Agent-10-Voice-Assistant && streamlit run app.py --server.port 8510 --server.address 0.0.0.0 --server.headless true"
timeout /t 2 /nobreak >nul

echo.
echo ============================================================
echo   All agents started successfully!
echo.
echo   Dashboard  : http://localhost:8500
echo   Agent 1    : http://localhost:8501
echo   Agent 2    : http://localhost:8502
echo   Agent 3    : http://localhost:8503
echo   Agent 4    : http://localhost:8504
echo   Agent 5    : http://localhost:8505
echo   Agent 6    : http://localhost:8506
echo   Agent 7    : http://localhost:8507
echo   Agent 8    : http://localhost:8508
echo   Agent 9    : http://localhost:8509
echo   Agent 10   : http://localhost:8510
echo.
echo   For mobile: replace localhost with your PC IP address
echo   Run ipconfig to find your IP address
echo ============================================================
echo.
pause
