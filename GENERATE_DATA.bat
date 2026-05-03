@echo off
REM QUICK START - Generate data and reload backend in one command
REM This is the easiest way to generate data without "Failed to fetch" errors

REM Make sure we're in the project root
if not exist docker-compose.yml (
    echo ❌ Error: docker-compose.yml not found
    echo Please run this script from the project root directory
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║     Azure Cost Simulator - Generate Data (One Click)     ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM Generate and reload in one command
echo Starting data generation and backend reload...
echo.

docker exec fastapi-backend python /app/scripts/generate_data.py && ^
docker-compose restart fastapi-backend && ^
timeout /t 5 /nobreak >nul && ^
echo. && ^
echo ✅ Success! Data generated and backend restarted. && ^
echo. && ^
echo 🌐 Frontend: http://localhost:5173 && ^
echo 📚 API Docs: http://localhost:8000/docs && ^
echo. && ^
echo 👉 Refresh your browser now to see the generated data.

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Error occurred. Run the detailed script for debugging:
    echo    .\scripts\debug_and_generate.bat
    pause
)
