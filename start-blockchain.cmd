@echo off
echo ========================================
echo   Blockchain Network Startup Script
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Building Docker images...
docker-compose build
if %errorlevel% neq 0 (
    echo ERROR: Failed to build images. Is Docker Desktop running?
    pause
    exit /b 1
)

echo.
echo [2/4] Starting containers...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start containers.
    pause
    exit /b 1
)

echo.
echo [3/4] Waiting for containers to initialize...
timeout /t 5 /nobreak > nul

echo.
echo [4/4] Registering nodes with each other...

REM Register node2 and node3 with node1
curl -s -X POST -d "nodes=http://node2:5000,http://node3:5000" http://localhost:5001/nodes/register > nul
echo   - Node 1: registered node2, node3

REM Register node1 and node3 with node2
curl -s -X POST -d "nodes=http://node1:5000,http://node3:5000" http://localhost:5002/nodes/register > nul
echo   - Node 2: registered node1, node3

REM Register node1 and node2 with node3
curl -s -X POST -d "nodes=http://node1:5000,http://node2:5000" http://localhost:5003/nodes/register > nul
echo   - Node 3: registered node1, node2

echo.
echo ========================================
echo   Blockchain Network is Ready!
echo ========================================
echo.
echo Access Points:
echo   Wallet Client: http://localhost:8081
echo   Node 1:        http://localhost:5001
echo   Node 2:        http://localhost:5002
echo   Node 3:        http://localhost:5003
echo.
echo Quick Commands:
echo   View containers:  docker ps
echo   View logs:        docker-compose logs -f
echo   Stop network:     docker-compose down
echo.
pause
