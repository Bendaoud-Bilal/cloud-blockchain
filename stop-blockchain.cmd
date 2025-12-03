@echo off
echo ========================================
echo   Stopping Blockchain Network
echo ========================================
echo.

cd /d "%~dp0"

echo Stopping and removing containers...
docker-compose down

echo.
echo Blockchain network stopped.
echo.
echo To also remove volumes (blockchain data), run:
echo   docker-compose down -v
echo.
pause
