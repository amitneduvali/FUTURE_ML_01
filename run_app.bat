@echo off
echo Starting Sales Forecasting Full-Stack Application...
echo.

echo Step 1: Installing backend dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing backend dependencies
    pause
    exit /b 1
)

echo.
echo Step 2: Starting Flask backend server...
start "Flask Backend" cmd /k "python app.py"

echo.
echo Step 3: Starting frontend server...
cd ../frontend
start "Frontend Server" cmd /k "python -m http.server 3000"

echo.
echo Servers starting...
echo - Backend API: http://localhost:5000
echo - Frontend Dashboard: http://localhost:3000
echo.
echo Press any key to close this window...
pause > nul