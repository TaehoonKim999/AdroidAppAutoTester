@echo off
REM ========================================
REM Android App Auto Tester - Windows Setup
REM ========================================

echo.
echo ========================================
echo   Android App Auto Tester Setup
echo   for Windows 10/11
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Check ADB installation
adb version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] ADB (Android Debug Bridge) not found in PATH
    echo Please install Android SDK Platform Tools from:
    echo https://developer.android.com/studio/releases/platform-tools
    echo.
    echo Press any key to continue anyway...
    pause >nul
) else (
    echo [OK] ADB is installed
    adb version
    echo.
)

REM Create virtual environment
echo [INFO] Creating virtual environment...
python -m venv .venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created
echo.

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [WARNING] Failed to upgrade pip, continuing...
)
echo.

REM Install Python packages
echo [INFO] Installing Python packages from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python packages
    pause
    exit /b 1
)
echo [OK] Python packages installed successfully
echo.

REM Initialize uiautomator2 (requires connected device)
echo.
echo ========================================
echo   uiautomator2 Initialization
echo ========================================
echo.
echo [INFO] Checking for connected Android devices...

adb devices | findstr "device" >nul
if %errorlevel% neq 0 (
    echo [WARNING] No Android device found
    echo Please connect your Android device with USB debugging enabled
    echo.
    echo Press any key to skip uiautomator2 initialization...
    echo You can run this command later after connecting your device:
    echo   python -m uiautomator2 init
    pause >nul
) else (
    echo [OK] Android device found
    echo.
    echo [INFO] Initializing uiautomator2...
    echo This may take a few minutes...
    echo.
    python -m uiautomator2 init
    if %errorlevel% neq 0 (
        echo [WARNING] uiautomator2 initialization failed
        echo You can run this command later:
        echo   python -m uiautomator2 init
    ) else (
        echo [OK] uiautomator2 initialized successfully
    )
)

REM Create sample config files
echo.
echo [INFO] Creating sample configuration files...

if not exist "config\apps.json.sample" (
    echo {"apps": [{"name": "Sample App", "package": "com.example.app", "activity": ".MainActivity", "test_duration": 120, "test_actions": ["scroll", "click_buttons"]}]}> config\apps.json.sample
    echo [OK] config\apps.json.sample created
)

if not exist "config\settings.json.sample" (
    echo {"screenshot_on_error": true, "screenshot_interval": 30, "collect_logcat": true, "logcat_filter": ["E", "W", "F"], "report_format": "markdown", "max_test_retries": 3, "delay_between_apps": 5}> config\settings.json.sample
    echo [OK] config\settings.json.sample created
)

REM Summary
echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo To run the application:
echo.
echo   1. Activate virtual environment:
echo      .venv\Scripts\activate.bat
echo.
echo   2. Run GUI version:
echo      python main_gui.py
echo.
echo   3. Run CLI version:
echo      python main.py
echo.
echo Configuration files:
echo   - Copy config\apps.json.sample to config\apps.json and customize
echo   - Copy config\settings.json.sample to config\settings.json and customize
echo.
echo Press any key to exit...
pause >nul