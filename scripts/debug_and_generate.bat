@echo off
REM Comprehensive debugging script for data generation and API health (Windows)

setlocal enabledelayedexpansion

echo.
echo ═══════════════════════════════════════════════════════════
echo 🔍 Azure Cost Simulator - Debug ^& Data Generation
echo ═══════════════════════════════════════════════════════════
echo.

REM Step 1: Check backend running
echo 📋 Step 1: Checking backend status...
docker ps | findstr "fastapi-backend" >nul
if %ERRORLEVEL% EQU 0 (
    echo ✅ Backend container is running
) else (
    echo ❌ Backend container is NOT running - starting...
    docker-compose up -d fastapi-backend
    timeout /t 5 /nobreak >nul
)

REM Step 2: Test initial API health
echo.
echo 📋 Step 2: Testing initial API health...
for /f %%A in ('curl -s -w "%%{http_code}" http://localhost:8000/api/v1/health') do set HEALTH=%%A

if "!HEALTH:~-3!"=="200" (
    echo ✅ Backend API is responding (HTTP 200)
) else (
    echo ❌ Backend API error (HTTP !HEALTH:~-3!)
)

REM Step 3: Test database connectivity
echo.
echo 📋 Step 3: Testing database connectivity...
for /f %%A in ('curl -s -w "%%{http_code}" http://localhost:8000/api/v1/health/ready') do set DB_READY=%%A

if "!DB_READY:~-3!"=="200" (
    echo ✅ Database is connected
) else (
    echo ❌ Database connection error
)

REM Step 4: Check row counts before generation
echo.
echo 📋 Step 4: Checking database row counts ^(before^)...

REM Step 5: Generate data
echo.
echo 📋 Step 5: Generating synthetic data...
echo    ^(This may take 1-2 minutes...^)
docker exec fastapi-backend python /app/scripts/generate_data.py

if %ERRORLEVEL% EQU 0 (
    echo ✅ Data generation completed
) else (
    echo ❌ Data generation failed (exit code: %ERRORLEVEL%)
)

REM Step 6: Restart backend
echo.
echo 📋 Step 6: Restarting backend service...
docker-compose restart fastapi-backend
timeout /t 5 /nobreak >nul
echo ✅ Backend restarted

REM Step 7: Test API health after restart
echo.
echo 📋 Step 7: Testing API health after restart...
for /f %%A in ('curl -s -w "%%{http_code}" http://localhost:8000/api/v1/health') do set HEALTH_AFTER=%%A

if "!HEALTH_AFTER:~-3!"=="200" (
    echo ✅ Backend is healthy after restart
) else (
    echo ❌ Backend error after restart (HTTP !HEALTH_AFTER:~-3!)
)

REM Step 8: Test cost summary endpoint
echo.
echo 📋 Step 8: Testing /api/v1/cost/summary endpoint...
curl -s http://localhost:8000/api/v1/cost/summary >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Cost summary endpoint working
) else (
    echo ❌ Cost summary endpoint error
)

REM Step 9: Test resources endpoint
echo.
echo 📋 Step 9: Testing /api/v1/resources/top-expensive endpoint...
curl -s http://localhost:8000/api/v1/resources/top-expensive >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Resources endpoint working
) else (
    echo ❌ Resources endpoint error
)

echo.
echo ═══════════════════════════════════════════════════════════
echo ✨ Debug report complete!
echo.
echo 🌐 Frontend: http://localhost:5173
echo 📚 API Docs: http://localhost:8000/docs
echo ═══════════════════════════════════════════════════════════
echo.
pause
