@echo off
REM Script to generate data and properly reload backend (Windows)
REM This fixes "Failed to fetch" errors after data generation

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║  Azure Cost Simulator - Data Generation & Backend Reload  ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Step 1: Check if backend is running
echo 📋 Step 1: Checking backend status...
docker ps | findstr "fastapi-backend" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ⚠️  Backend not running. Starting...
    docker-compose up -d fastapi-backend
    timeout /t 5 /nobreak >nul
)
echo ✅ Backend is running

REM Step 2: Generate synthetic data
echo.
echo 📊 Step 2: Generating synthetic cost data...
echo    (This will take 1-2 minutes...)
docker exec fastapi-backend python /app/scripts/generate_data.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ Data generation failed!
    echo.
    echo 🔧 Troubleshooting tips:
    echo    - Check backend logs: docker logs fastapi-backend
    echo    - Check database: docker logs postgres-db
    echo    - Restart containers: docker-compose restart
    pause
    exit /b 1
)

echo ✅ Data generated successfully!

REM Step 3: Restart backend to refresh connection pools
echo.
echo 🔄 Step 3: Restarting backend service...
docker-compose restart fastapi-backend

REM Wait for backend to be ready
echo ⏳ Waiting for backend to start (this takes 10-15 seconds)...
timeout /t 3 /nobreak >nul

REM Step 4: Wait for backend health check (with retries)
echo 🧪 Step 4: Verifying backend health...
setlocal enabledelayedexpansion
set RETRY_COUNT=0
set MAX_RETRIES=10

:health_check_retry
if !RETRY_COUNT! GEQ !MAX_RETRIES! (
    echo ❌ Backend failed to become healthy after %MAX_RETRIES% retries
    echo.
    echo 🔧 Manual troubleshooting:
    echo    - Check backend logs: docker logs fastapi-backend
    echo    - Check database logs: docker logs postgres-db
    echo    - Full restart: docker-compose down && docker-compose up -d
    pause
    exit /b 1
)

REM Test health endpoint with quiet error handling
curl -s -f http://localhost:8000/api/v1/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Backend is healthy (HTTP 200)
    goto health_check_complete
)

echo ⏳ Backend still initializing... (attempt !RETRY_COUNT!/%MAX_RETRIES%)
set /a RETRY_COUNT=!RETRY_COUNT!+1
timeout /t 2 /nobreak >nul
goto health_check_retry

:health_check_complete
echo.

REM Step 5: Test API endpoints
echo 📋 Step 5: Testing key API endpoints...

curl -s -f http://localhost:8000/api/v1/cost/summary >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Cost endpoint working
) else (
    echo ⚠️  Cost endpoint not responding
)

curl -s -f http://localhost:8000/api/v1/resources/top-expensive >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Resources endpoint working
) else (
    echo ⚠️  Resources endpoint not responding
)

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                    ✨ All set! Ready to go                ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 🌐 Frontend:    http://localhost:5173
echo 📚 API Docs:    http://localhost:8000/docs
echo 📊 API Health:  http://localhost:8000/api/v1/health
echo.
echo ⚡ Next steps:
echo    1. Open your browser to http://localhost:5173
echo    2. Refresh the page to see the generated data
echo    3. Check the Dashboard, Cost Trends, and Resources pages
echo.
pause
