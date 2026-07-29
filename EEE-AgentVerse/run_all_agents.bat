@echo off
title ElderCare AI - AgentVerse Launcher
color 0A
cls

echo.
echo ============================================================
echo   ElderCare AI - AgentVerse Launcher
echo   IP: 172.16.161.187
echo ============================================================
echo.

cd /d "%~dp0"

taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM streamlit.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo Starting all agents...

start "Dashboard"  cmd /k "cd /d %~dp0 && streamlit run dashboard.py --server.port 8500 --server.address 0.0.0.0 --server.headless true"
start "Agent-1"    cmd /k "cd /d %~dp0Agent-1-Medicine-Reminder && streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true"
start "Agent-2"    cmd /k "cd /d %~dp0Agent-2-Emergency-Detection && streamlit run app.py --server.port 8502 --server.address 0.0.0.0 --server.headless true"
start "Agent-3"    cmd /k "cd /d %~dp0Agent-3-Appointment-Booking && streamlit run app.py --server.port 8503 --server.address 0.0.0.0 --server.headless true"
start "Agent-4"    cmd /k "cd /d %~dp0Agent-4-Prescription-Explainer && streamlit run app.py --server.port 8504 --server.address 0.0.0.0 --server.headless true"
start "Agent-5"    cmd /k "cd /d %~dp0Agent-5-Health-Report && streamlit run app.py --server.port 8505 --server.address 0.0.0.0 --server.headless true"
start "Agent-6"    cmd /k "cd /d %~dp0Agent-6-Family-Notifier && streamlit run app.py --server.port 8506 --server.address 0.0.0.0 --server.headless true"
start "Agent-7"    cmd /k "cd /d %~dp0Agent-7-Diet-Recommendation && streamlit run app.py --server.port 8507 --server.address 0.0.0.0 --server.headless true"
start "Agent-8"    cmd /k "cd /d %~dp0Agent-8-Exercise-Coach && streamlit run app.py --server.port 8508 --server.address 0.0.0.0 --server.headless true"
start "Agent-9"    cmd /k "cd /d %~dp0Agent-9-Mood-Companion && streamlit run app.py --server.port 8509 --server.address 0.0.0.0 --server.headless true"
start "Agent-10"   cmd /k "cd /d %~dp0Agent-10-Voice-Assistant && streamlit run app.py --server.port 8510 --server.address 0.0.0.0 --server.headless true"

echo.
echo ============================================================
echo   ALL AGENTS STARTED!
echo.
echo   Dashboard  : http://172.16.161.187:8500
echo   Agent 1    : http://172.16.161.187:8501
echo   Agent 2    : http://172.16.161.187:8502
echo   Agent 3    : http://172.16.161.187:8503
echo   Agent 4    : http://172.16.161.187:8504
echo   Agent 5    : http://172.16.161.187:8505
echo   Agent 6    : http://172.16.161.187:8506
echo   Agent 7    : http://172.16.161.187:8507
echo   Agent 8    : http://172.16.161.187:8508
echo   Agent 9    : http://172.16.161.187:8509
echo   Agent 10   : http://172.16.161.187:8510
echo.
echo   Mobile: Open http://172.16.161.187:8500
echo ============================================================
echo.
pause
