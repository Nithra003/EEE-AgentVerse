@echo off
echo Stopping all ElderCare AI agents...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":850[0-9] "') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":851[0-9] "') do taskkill /PID %%a /F >nul 2>&1
echo Done. All agents stopped.
pause
