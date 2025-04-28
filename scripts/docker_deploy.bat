@echo off
setlocal enabledelayedexpansion

echo [92m===== Portfolio Optimizer Docker Deployment Tool =====[0m
echo.

:menu
echo [96mSelect an option:[0m
echo [96m1.[0m Build and start containers
echo [96m2.[0m Start containers (detached mode)
echo [96m3.[0m Stop containers
echo [96m4.[0m View logs
echo [96m5.[0m Rebuild containers
echo [96m6.[0m Set environment variables
echo [96m7.[0m Exit
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" (
    echo [92mBuilding and starting containers...[0m
    docker-compose up --build
    goto menu
)

if "%choice%"=="2" (
    echo [92mStarting containers in detached mode...[0m
    for /f "tokens=1,2 delims==" %%a in (..\..env) do (
        if "%%a"=="PORT" set PORT=%%b
    )
    if not defined PORT set PORT=5000
    docker-compose up -d
    echo [92mContainers started! Access the application at http://localhost:%PORT%[0m
    goto menu
)

if "%choice%"=="3" (
    echo [92mStopping containers...[0m
    docker-compose down
    goto menu
)

if "%choice%"=="4" (
    echo [92mViewing logs (press Ctrl+C to exit)...[0m
    docker-compose logs -f
    goto menu
)

if "%choice%"=="5" (
    echo [92mRebuilding containers...[0m
    docker-compose build --no-cache
    echo [92mRebuild complete![0m
    goto menu
)

if "%choice%"=="6" (
    echo [96mSet environment variables for deployment:[0m
    set /p secret_key="Enter SECRET_KEY (leave empty for default): "
    set /p flask_env="Enter FLASK_ENV (production/development, default: production): "
    set /p port="Enter PORT (default: 5000): "
    set /p host="Enter HOST (default: 0.0.0.0): "
    
    if "!secret_key!"=="" (
        set secret_key=default-dev-key-replace-in-production
    )
    
    if "!flask_env!"=="" (
        set flask_env=production
    )
    
    if "!port!"=="" (
        for /f "tokens=1,2 delims==" %%a in (..\..env) do (
            if "%%a"=="PORT" set port=%%b
        )
        if "!port!"=="" set port=5000
    )
    
    if "!host!"=="" (
        for /f "tokens=1,2 delims==" %%a in (..\..env) do (
            if "%%a"=="HOST" set host=%%b
        )
        if "!host!"=="" set host=0.0.0.0
    )
    
    echo [92mStarting containers with custom environment...[0m
    set SECRET_KEY=!secret_key!
    set FLASK_ENV=!flask_env!
    set PORT=!port!
    set HOST=!host!
    
    docker-compose up -d
    echo [92mContainers started with custom environment! Access the application at http://localhost:!port![0m
    goto menu
)

if "%choice%"=="7" (
    echo [92mExiting...[0m
    exit /b 0
)

echo [91mInvalid choice. Please try again.[0m
goto menu
