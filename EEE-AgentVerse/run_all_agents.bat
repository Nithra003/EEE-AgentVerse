@echo off
title ElderCare AI - AgentVerse Launcher
color 0A
cls

echo.
echo ============================================================
echo   ElderCare AI - AgentVerse Launcher
echo ============================================================
echo.

cd /d "%~dp0"

taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo Starting ElderCare AI Agent (Unified App)...
start "ElderCare-AI-Main" cmd /k "cd /d %~dp0 && streamlit run main_app.py --server.port 8500 --server.address 0.0.0.0 --server.headless true"

timeout /t 3 /nobreak >nul

echo Starting individual agents...
start "Agent-1"  cmd /k "cd /d %~dp0Agent-1-Medicine-Reminder && streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true"
start "Agent-2"  cmd /k "cd /d %~dp0Agent-2-Emergency-Detection && streamlit run app.py --server.port 8502 --server.address 0.0.0.0 --server.headless true"
start "Agent-3"  cmd /k "cd /d %~dp0Agent-3-Appointment-Booking && streamlit run app.py --server.port 8503 --server.address 0.0.0.0 --server.headless true"
start "Agent-4"  cmd /k "cd /d %~dp0Agent-4-Prescription-Explainer && streamlit run app.py --server.port 8504 --server.address 0.0.0.0 --server.headless true"
start "Agent-5"  cmd /k "cd /d %~dp0Agent-5-Health-Report && streamlit run app.py --server.port 8505 --server.address 0.0.0.0 --server.headless true"
start "Agent-6"  cmd /k "cd /d %~dp0Agent-6-Family-Notifier && streamlit run app.py --server.port 8506 --server.address 0.0.0.0 --server.headless true"
start "Agent-7"  cmd /k "cd /d %~dp0Agent-7-Diet-Recommendation && streamlit run app.py --server.port 8507 --server.address 0.0.0.0 --server.headless true"
start "Agent-8"  cmd /k "cd /d %~dp0Agent-8-Exercise-Coach && streamlit run app.py --server.port 8508 --server.address 0.0.0.0 --server.headless true"
start "Agent-9"  cmd /k "cd /d %~dp0Agent-9-Mood-Companion && streamlit run app.py --server.port 8509 --server.address 0.0.0.0 --server.headless true"
start "Agent-10" cmd /k "cd /d %~dp0Agent-10-Voice-Assistant && streamlit run app.py --server.port 8510 --server.address 0.0.0.0 --server.headless true"

echo.
echo ============================================================
echo   ALL AGENTS STARTED!
echo.
echo   MAIN APP (use this for demo)
echo   http://localhost:8500
echo.
echo   Individual Agents
echo   Agent 1  Medicine Reminder    : http://localhost:8501
echo   Agent 2  Emergency Detection  : http://localhost:8502
echo   Agent 3  Appointment Booking  : http://localhost:8503
echo   Agent 4  Prescription         : http://localhost:8504
echo   Agent 5  Health Report        : http://localhost:8505
echo   Agent 6  Family Notifier      : http://localhost:8506
echo   Agent 7  Diet Recommendation  : http://localhost:8507
echo   Agent 8  Exercise Coach       : http://localhost:8508
echo   Agent 9  Mood Companion       : http://localhost:8509
echo   Agent 10 Voice Assistant      : http://localhost:8510
echo.
echo   Mobile Access (same WiFi)
echo   http://172.17.15.201:8500
echo ============================================================
echo.
pause
