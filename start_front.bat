@echo off
echo ========================================
echo   Starting Local Development Server
echo ========================================
echo.
echo Project will be available at:
echo http://localhost:8000/pages/
echo.
echo Press Ctrl+C to stop the server
echo.
python -m http.server 8000
pause