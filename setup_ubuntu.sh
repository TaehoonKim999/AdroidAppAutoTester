#!/bin/bash
# ========================================
# Android App Auto Tester - Ubuntu Setup
# ========================================

set -e  # Exit on error

echo ""
echo "========================================"
echo "  Android App Auto Tester Setup"
echo "  for Ubuntu 20.04/22.04"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed"
    echo "Please install Python 3.8 or higher:"
    echo "  sudo apt update"
    echo "  sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

echo "[OK] Python3 is installed"
python3 --version
echo ""

# Check ADB installation
if ! command -v adb &> /dev/null; then
    echo "[WARNING] ADB (Android Debug Bridge) not found"
    echo "Please install Android SDK Platform Tools:"
    echo "  wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip"
    echo "  unzip platform-tools-latest-linux.zip"
    echo "  sudo mv platform-tools/adb /usr/local/bin/"
    echo "  sudo chmod +x /usr/local/bin/adb"
    echo ""
    echo "Or install via apt (older version):"
    echo "  sudo apt update"
    echo "  sudo apt install android-tools-adb"
    echo ""
    read -p "Press Enter to continue anyway..." -r
else
    echo "[OK] ADB is installed"
    adb version
    echo ""
fi

# Check for required system packages
echo "[INFO] Checking for required system packages..."
REQUIRED_PACKAGES=("python3-venv" "python3-pip")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! dpkg -l | grep -q "^ii  $package"; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    echo "[WARNING] Missing packages: ${MISSING_PACKAGES[*]}"
    echo "Installing missing packages..."
    sudo apt update
    sudo apt install -y "${MISSING_PACKAGES[@]}"
fi

# Create virtual environment
echo "[INFO] Creating virtual environment..."
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to create virtual environment"
    exit 1
fi
echo "[OK] Virtual environment created"
echo ""

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to activate virtual environment"
    exit 1
fi
echo "[OK] Virtual environment activated"
echo ""

# Upgrade pip
echo "[INFO] Upgrading pip..."
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo "[WARNING] Failed to upgrade pip, continuing..."
fi
echo ""

# Install Python packages
echo "[INFO] Installing Python packages from requirements.txt..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install Python packages"
    exit 1
fi
echo "[OK] Python packages installed successfully"
echo ""

# Initialize uiautomator2 (requires connected device)
echo ""
echo "========================================"
echo "  uiautomator2 Initialization"
echo "========================================"
echo ""
echo "[INFO] Checking for connected Android devices..."

if ! adb devices | grep -q "device$"; then
    echo "[WARNING] No Android device found"
    echo "Please connect your Android device with USB debugging enabled"
    echo ""
    echo "Note: If you see 'no permissions' error, you may need to set up USB permissions:"
    echo "  1. Get device vendor ID: lsusb"
    echo "  2. Add udev rule: sudo nano /etc/udev/rules.d/51-android.rules"
    echo "  3. Add line: SUBSYSTEM==\"usb\", ATTR{idVendor}==\"XXXX\", MODE=\"0666\""
    echo "  4. Reload rules: sudo udevadm control --reload-rules && sudo udevadm trigger"
    echo "  5. Reconnect the device"
    echo ""
    read -p "Press Enter to skip uiautomator2 initialization..." -r
    echo ""
    echo "You can run this command later after connecting your device:"
    echo "  python3 -m uiautomator2 init"
else
    echo "[OK] Android device found"
    echo ""
    echo "[INFO] Initializing uiautomator2..."
    echo "This may take a few minutes..."
    echo ""
    python3 -m uiautomator2 init
    if [ $? -ne 0 ]; then
        echo "[WARNING] uiautomator2 initialization failed"
        echo "You can run this command later:"
        echo "  python3 -m uiautomator2 init"
    else
        echo "[OK] uiautomator2 initialized successfully"
    fi
fi

# Create sample config files
echo ""
echo "[INFO] Creating sample configuration files..."

if [ ! -f "config/apps.json.sample" ]; then
    echo '{"apps": [{"name": "Sample App", "package": "com.example.app", "activity": ".MainActivity", "test_duration": 120, "test_actions": ["scroll", "click_buttons"]}]}' > config/apps.json.sample
    echo "[OK] config/apps.json.sample created"
fi

if [ ! -f "config/settings.json.sample" ]; then
    echo '{"screenshot_on_error": true, "screenshot_interval": 30, "collect_logcat": true, "logcat_filter": ["E", "W", "F"], "report_format": "markdown", "max_test_retries": 3, "delay_between_apps": 5}' > config/settings.json.sample
    echo "[OK] config/settings.json.sample created"
fi

# Make setup script executable
chmod +x setup_ubuntu.sh

# Summary
echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "To run the application:"
echo ""
echo "  1. Activate virtual environment:"
echo "     source .venv/bin/activate"
echo ""
echo "  2. Run GUI version:"
echo "     python3 main_gui.py"
echo ""
echo "  3. Run CLI version:"
echo "     python3 main.py"
echo ""
echo "Configuration files:"
echo "  - Copy config/apps.json.sample to config/apps.json and customize"
echo "  - Copy config/settings.json.sample to config/settings.json and customize"
echo ""
echo "Note: Don't forget to keep the virtual environment activated when running the app!"
echo ""