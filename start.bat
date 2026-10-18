@echo off
setlocal

echo ===================================================
echo Source-to-Runtime Security Assessor (SIH 2026)
echo ===================================================

echo.
echo [1/2] Starting Backend (FastAPI)...
cd backend
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing requirements...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)
start "Security Assessor Backend" cmd /c "uvicorn main:app --host 0.0.0.0 --port 8000"
cd ..

echo.
echo [2/2] Starting Frontend (Vite+React)...
cd frontend
if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install
)
start "Security Assessor Frontend" cmd /c "npm run dev"
cd ..

echo.
echo ===================================================
echo Services Started!
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:5173
echo.
echo Close the newly opened command windows to stop the services.
echo ===================================================
pause
