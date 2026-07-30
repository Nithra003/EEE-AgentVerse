@echo off
title ElderCare AI - Launcher
color 0A
cls

cd /d "%~dp0"

echo Stopping old agents...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":850"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":851"') do taskkill /PID %%a /F >nul 2>&1
taskkill /F /IM streamlit.exe >nul 2>&1
timeout /t 3 /nobreak >nul

if not exist logs mkdir logs

echo Starting Dashboard (8500)...
start "ElderCare-Dashboard" cmd /c "cd /d %~dp0 && streamlit run dashboard.py --server.port 8500 --server.address 0.0.0.0 --server.headless true"
timeout /t 3 /nobreak >nul

echo Starting Agent 1  (8501) Medicine Reminder...
start "ElderCare-1" cmd /c "cd /d %~dp0Agent-1-Medicine-Reminder && streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true"
timeout /t 1 /nobreak >nul

echo Starting Agent 2  (8502) Emergency Detection...
start "ElderCare-2" cmd /c "cd /d %~dp0Agent-2-Emergency-Detection && streamlit run app.py --server.port 8502 --server.address 0.0.0.0 --server.headless true"
timeout /t 1 /nobreak >nul

echo Starting Agent 3  (8503) Appointment Booking...
start "ElderCare-3" cmd /c "cd /d %~dp0Agent-3-Appointment-Booking && streamlit run app.py --server.port 8503 --server.address 0.0.0.0 --server.headless true"
timeout /t 1 /nobreak >nul

echo Starting Agent 4  (8504) Prescription Explainer...
start "ElderCare-4" cmd /c "cd /d %~dp0Agent-4-Prescription-Explainer && streamlit run app.py --server.port 8504 --server.address 0.0.0.0 --server.headless true"
timeout /t 1 /nobreak >nul

echo Starting Agent 5  (8505) Health Report...
start "ElderCare-5" cmd /c "cd /d %~dp0Agent-5-Health-Report && streamlit run app.py --server.port 8505 --server.address 0.0.0.0 --server.headless true"
timeout /t 1 /nobreak >nul

echo Starting Agent 6  (8506) Family Notifier...
start "ElderCare-6" cmd /c "cd /d %~dp0Agent-6-Family-Notifier && streamlit run app.py --server.port 8506 --server.address 0.0.0.0 --server.headless true"
timeout /t 1 /nobreak >nul

echo Starting Agent 7  (8507) Diet Recommendation...
start "ElderCare-7" cmd /c "cd /d %~dp0Agent-7-Diet-Recommendation && streamlit run app.py --server.port 8507 --server.address 0.0.0.0 --server.headless true"
timeout /t 1 /nobreak >nul

echo Starting Agent 8  (8508) Exercise Coach...
start "ElderCare-8" cmd /c "cd /d %~dp0Agent-8-Exercise-Coach && streamlit run app.py --server.port 8508 --server.address 0.0.0.0 --server.headless true"
timeout /t 1 /nobreak >nul

echo Starting Agent 9  (8509) Mood Companion...
start "ElderCare-9" cmd /c "cd /d %~dp0Agent-9-Mood-Companion && streamlit run app.py --server.port 8509 --server.address 0.0.0.0 --server.headless true"
timeout /t 1 /nobreak >nul

echo Starting Agent 10 (8510) Voice Assistant...
start "ElderCare-10" cmd /c "cd /d %~dp0Agent-10-Voice-Assistant && streamlit run app.py --server.port 8510 --server.address 0.0.0.0 --server.headless true"
timeout /t 1 /nobreak >nul

echo Starting Agent 11 (8511) Medical Assistant...
start "ElderCare-11" cmd /c "cd /d %~dp0Agent-11-Medical-Assistant && streamlit run app.py --server.port 8511 --server.address 0.0.0.0 --server.headless true"
timeout /t 1 /nobreak >nul

echo.
echo Waiting 8 seconds for all agents to load...
timeout /t 8 /nobreak >nul

echo.
echo ============================================================
echo  ALL 11 AGENTS STARTED!
echo  Dashboard : http://localhost:8500
echo  Agent 1   : http://localhost:8501  Medicine Reminder
echo  Agent 2   : http://localhost:8502  Emergency Detection
echo  Agent 3   : http://localhost:8503  Appointment Booking
echo  Agent 4   : http://localhost:8504  Prescription Explainer
echo  Agent 5   : http://localhost:8505  Health Report
echo  Agent 6   : http://localhost:8506  Family Notifier
echo  Agent 7   : http://localhost:8507  Diet Recommendation
echo  Agent 8   : http://localhost:8508  Exercise Coach
echo  Agent 9   : http://localhost:8509  Mood Companion
echo  Agent 10  : http://localhost:8510  Voice Assistant
echo  Agent 11  : http://localhost:8511  Medical Assistant
echo ============================================================

start "" "http://localhost:8500"
pause
