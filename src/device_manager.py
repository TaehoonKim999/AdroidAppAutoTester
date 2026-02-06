"""
Device Manager Module

Handles Android device connection and management through ADB.
Provides methods to control apps, take screenshots, and get device information.
"""

import os
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict

try:
    import uiautomator2 as u2
except ImportError:
    u2 = None

from .platform_utils import get_platform_utils


@dataclass
class DeviceInfo:
    """
    Information about a connected Android device.
    
    Attributes:
        serial: Device serial number
        model: Device model name
        android_version: Android version string
        sdk_version: Android SDK version number
    """
    serial: str
    model: str
    android_version: str
    sdk_version: int
    
    def to_dict(self) -> dict:
        """Convert DeviceInfo to dictionary."""
        return {
            "serial": self.serial,
            "model": self.model,
            "android_version": self.android_version,
            "sdk_version": self.sdk_version
        }
    
    def __str__(self) -> str:
        """Return string representation of device info."""
        return f"{self.model} (Android {self.android_version}, SDK {self.sdk_version})"


class DeviceManager:
    """
    Manager for Android device connection and control.
    
    Handles ADB connection, app lifecycle management, screenshots,
    and device information retrieval.
    
    Attributes:
        platform_utils: PlatformUtils instance
        device: uiautomator2 device instance (if connected)
        device_info: DeviceInfo object (if connected)
        serial: Device serial number
    """
    
    MAX_CONNECT_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    def __init__(self, serial: Optional[str] = None):
        """
        Initialize DeviceManager.
        
        Args:
            serial: Optional device serial number. If None, uses first connected device.
        """
        if u2 is None:
            raise ImportError(
                "uiautomator2 is not installed. "
                "Please install it with: pip install uiautomator2"
            )
        
        self.platform_utils = get_platform_utils()
        self.device: Optional[u2.Device] = None
        self.device_info: Optional[DeviceInfo] = None
        self.serial = serial
        self._connected = False
        self._app_name_cache: Dict[str, str] = {}  # Cache for app names
    
    def list_devices(self) -> List[DeviceInfo]:
        """
        Get list of connected Android devices.
        
        Returns:
            List of DeviceInfo objects for all connected devices
        """
        serials = self.platform_utils.get_connected_devices()
        devices = []
        
        for serial in serials:
            # Get device info for each serial
            device_info = self._get_device_info_for_serial(serial)
            if device_info:
                devices.append(device_info)
        
        return devices
    
    def _get_device_info_for_serial(self, serial: str) -> Optional[DeviceInfo]:
        """
        Get device information for a specific serial number.
        
        Args:
            serial: Device serial number
        
        Returns:
            DeviceInfo object or None if failed
        """
        adb_cmd = self.platform_utils.get_adb_command()
        
        # Get device model
        _, model_out, _ = self.platform_utils.run_command([
            adb_cmd, "-s", serial, "shell", "getprop", "ro.product.model"
        ])
        model = model_out.strip() or "Unknown"
        
        # Get Android version
        _, version_out, _ = self.platform_utils.run_command([
            adb_cmd, "-s", serial, "shell", "getprop", "ro.build.version.release"
        ])
        android_version = version_out.strip() or "Unknown"
        
        # Get SDK version
        _, sdk_out, _ = self.platform_utils.run_command([
            adb_cmd, "-s", serial, "shell", "getprop", "ro.build.version.sdk"
        ])
        try:
            sdk_version = int(sdk_out.strip())
        except (ValueError, AttributeError):
            sdk_version = 0
        
        return DeviceInfo(
            serial=serial,
            model=model,
            android_version=android_version,
            sdk_version=sdk_version
        )
    
    def connect(self) -> bool:
        """
        Connect to Android device via ADB.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        # Check ADB availability
        if not self.platform_utils.check_adb_available():
            print("[ERROR] ADB is not available. Please install Android SDK Platform Tools.")
            return False
        
        # Get connected devices
        devices = self.platform_utils.get_connected_devices()
        if not devices:
            print("[ERROR] No Android devices found. Please connect a device with USB debugging enabled.")
            return False
        
        # Determine which device to connect to
        if self.serial is None:
            # Use first device
            self.serial = devices[0]
        elif self.serial not in devices:
            print(f"[ERROR] Device with serial {self.serial} not found.")
            print(f"Available devices: {devices}")
            return False
        
        # Try to connect with retries
        for attempt in range(1, self.MAX_CONNECT_RETRIES + 1):
            print(f"[INFO] Connecting to device {self.serial} (attempt {attempt}/{self.MAX_CONNECT_RETRIES})...")
            
            try:
                self.device = u2.connect(self.serial)
                self._connected = True
                
                # Get device info
                self.device_info = self._get_device_info()
                print(f"[OK] Connected to {self.device_info}")
                
                return True
                
            except Exception as e:
                print(f"[WARNING] Connection attempt {attempt} failed: {e}")
                if attempt < self.MAX_CONNECT_RETRIES:
                    time.sleep(self.RETRY_DELAY)
                else:
                    print(f"[ERROR] Failed to connect after {self.MAX_CONNECT_RETRIES} attempts.")
                    return False
        
        return False
    
    def disconnect(self) -> None:
        """
        Disconnect from device.
        
        Clears device connection and resets state.
        """
        if self.device is not None:
            print(f"[INFO] Disconnecting from device {self.serial}...")
            self.device = None
            self._connected = False
            self.device_info = None
            print("[OK] Disconnected")
    
    def is_connected(self) -> bool:
        """
        Check if device is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self._connected and self.device is not None
    
    def get_device_info(self) -> Optional[DeviceInfo]:
        """
        Get device information.
        
        Returns:
            DeviceInfo object if connected, None otherwise
        """
        if not self.is_connected():
            return None
        return self.device_info
    
    def _get_device_info(self) -> DeviceInfo:
        """
        Retrieve device information from ADB.
        
        Returns:
            DeviceInfo object
        """
        adb_cmd = self.platform_utils.get_adb_command()
        
        # Get device model
        _, model_out, _ = self.platform_utils.run_command([
            adb_cmd, "-s", self.serial, "shell", "getprop", "ro.product.model"
        ])
        model = model_out.strip() or "Unknown"
        
        # Get Android version
        _, version_out, _ = self.platform_utils.run_command([
            adb_cmd, "-s", self.serial, "shell", "getprop", "ro.build.version.release"
        ])
        android_version = version_out.strip() or "Unknown"
        
        # Get SDK version
        _, sdk_out, _ = self.platform_utils.run_command([
            adb_cmd, "-s", self.serial, "shell", "getprop", "ro.build.version.sdk"
        ])
        try:
            sdk_version = int(sdk_out.strip())
        except (ValueError, AttributeError):
            sdk_version = 0
        
        return DeviceInfo(
            serial=self.serial,
            model=model,
            android_version=android_version,
            sdk_version=sdk_version
        )
    
    def get_installed_apps(self, third_party_only: bool = True, use_aapt: bool = True) -> List[dict]:
        """
        Get list of installed applications on device.
        
        Args:
            third_party_only: If True, only return third-party apps (not system apps)
            use_aapt: If True, use aapt to get actual app names (slower but more accurate)
        
        Returns:
            List of dicts with app info: package name and app name
        """
        if not self.serial:
            return []
        
        adb_cmd = self.platform_utils.get_adb_command()
        
        # Get package list
        cmd = ["shell", "pm", "list", "packages"]
        if third_party_only:
            cmd.append("-3")
        
        code, output, _ = self.platform_utils.run_command(
            [adb_cmd, "-s", self.serial] + cmd,
            timeout=30
        )
        
        if code != 0:
            return []
        
        # Parse package list
        packages = []
        for line in output.split('\n'):
            if line.strip().startswith('package:'):
                package_name = line.replace('package:', '').strip()
                
                # Get app name
                if use_aapt:
                    app_name = self._get_app_name_aapt(package_name)
                else:
                    app_name = self._extract_app_name(package_name)
                
                packages.append({
                    "package": package_name,
                    "name": app_name
                })
        
        # Sort by app name
        packages.sort(key=lambda x: x['name'].lower())
        return packages
    
    def _get_app_name_aapt(self, package: str) -> str:
        """
        Get actual app name using aapt tool.
        
        Args:
            package: Package name (e.g., "com.nextstory.somomi")
        
        Returns:
            Actual app display name (e.g., "소모미")
        """
        # Check cache first
        if package in self._app_name_cache:
            return self._app_name_cache[package]
        
        # Check if aapt is available
        if not self._check_aapt_available():
            # Fallback to package name extraction
            return self._extract_app_name(package)
        
        adb_cmd = self.platform_utils.get_adb_command()
        
        try:
            # Get APK path
            code, output, _ = self.platform_utils.run_command(
                [adb_cmd, "-s", self.serial, "shell", "pm", "path", package],
                timeout=10
            )
            
            if code != 0:
                return self._extract_app_name(package)
            
            # Parse APK path (get base.apk)
            apk_path = None
            for line in output.split('\n'):
                if line.strip().startswith('package:') and 'base.apk' in line:
                    apk_path = line.replace('package:', '').strip()
                    break
            
            if not apk_path:
                return self._extract_app_name(package)
            
            # Pull APK to host temporarily
            with tempfile.TemporaryDirectory() as tmpdir:
                local_apk = os.path.join(tmpdir, 'app.apk')
                
                code, _, _ = self.platform_utils.run_command(
                    [adb_cmd, "-s", self.serial, "pull", apk_path, local_apk],
                    timeout=30
                )
                
                if code != 0:
                    return self._extract_app_name(package)
                
                # Use aapt to get label
                code, output, _ = self.platform_utils.run_command(
                    ["aapt", "dump", "badging", local_apk],
                    timeout=30
                )
                
                if code == 0:
                    for line in output.split('\n'):
                        if 'application-label:' in line:
                            # Parse label (format: application-label:'App Name')
                            if "'" in line:
                                label = line.split("'")[1]
                                # Cache the result
                                self._app_name_cache[package] = label
                                return label
        
        except Exception as e:
            print(f"[WARNING] Failed to get app name for {package}: {e}")
        
        # Fallback to package name extraction
        return self._extract_app_name(package)
    
    def _check_aapt_available(self) -> bool:
        """
        Check if aapt tool is available on host system.
        
        Returns:
            bool: True if aapt is available, False otherwise
        """
        try:
            code, _, _ = self.platform_utils.run_command(
                ["which", "aapt"],
                timeout=5
            )
            return code == 0
        except Exception:
            return False
    
    def _extract_app_name(self, package: str) -> str:
        """
        Extract app name from package name (fallback method).
        
        Args:
            package: Package name (e.g., "com.example.app")
        
        Returns:
            App name extracted from package name
        """
        # Get last segment of package name
        parts = package.split('.')
        if parts:
            app_name = parts[-1]
            
            # Convert to title case (e.g., "youtube" -> "Youtube", "eungman_calendar" -> "Eungman Calendar")
            # Replace underscores with spaces and capitalize
            app_name = app_name.replace('_', ' ')
            app_name = app_name.title()
            
            return app_name
        
        return package
    
    def _find_launcher_activity(self, package: str) -> Optional[str]:
        """
        Find the launcher activity for a package.
        
        Args:
            package: Package name (e.g., "com.example.app")
        
        Returns:
            Full activity string (e.g., "com.example.app/.MainActivity") or None
        """
        adb_cmd = self.platform_utils.get_adb_command()
        
        try:
            # Use dumpsys package to find launcher activity
            code, output, _ = self.platform_utils.run_command(
                [adb_cmd, "-s", self.serial, "shell", "dumpsys", "package", package],
                timeout=15
            )
            
            if code != 0:
                return None
            
            # Parse output for launchable activity
            in_activities = False
            for line in output.split('\n'):
                # Check if we're in the activities section
                if 'Activity Resolver Table:' in line and 'android.intent.action.MAIN' in line:
                    in_activities = True
                    continue
                
                if in_activities:
                    # Look for activity lines
                    if line.strip().startswith(package):
                        # Extract activity name
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            activity = parts[1]
                            # Clean up the activity name
                            if activity.startswith(package):
                                return f"{package}/{activity[len(package):]}"
                            return activity
            
            # Alternative method: use dumpsys package for android.intent.action.MAIN
            code, output, _ = self.platform_utils.run_command(
                [adb_cmd, "-s", self.serial, "shell", "cmd", "package", "resolve-activity", "--brief", package + "/android.intent.action.MAIN"],
                timeout=10
            )
            
            if code == 0:
                activity = output.strip()
                if activity and '/' in activity:
                    return activity
            
            return None
            
        except Exception as e:
            print(f"[WARNING] Failed to find launcher activity for {package}: {e}")
            return None
    
    def start_app(self, package: str, activity: str) -> bool:
        """
        Start an application.
        
        Args:
            package: Android package name (e.g., "com.example.app")
            activity: Activity name (e.g., ".MainActivity"). If empty or None, finds launcher activity automatically.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            print("[ERROR] Device not connected")
            return False
        
        adb_cmd = self.platform_utils.get_adb_command()
        
        # If activity is empty or None, find launcher activity automatically
        if not activity or activity.strip() == "" or activity == ".MainActivity":
            print(f"[INFO] Finding launcher activity for {package}...")
            launcher_activity = self._find_launcher_activity(package)
            if launcher_activity:
                full_activity = launcher_activity
                print(f"[INFO] Using launcher activity: {full_activity}")
            else:
                # Fallback to package name only (Android will try to launch main activity)
                full_activity = package
                print(f"[INFO] Using package name only: {full_activity}")
        else:
            full_activity = f"{package}/{activity}"
        
        try:
            print(f"[INFO] Starting app: {full_activity}")
            code, _, err = self.platform_utils.run_command([
                adb_cmd, "-s", self.serial,
                "shell", "am", "start", "-n", full_activity
            ], timeout=10)
            
            if code == 0:
                # Wait for app to start
                time.sleep(2)
                print(f"[OK] App started: {full_activity}")
                return True
            else:
                print(f"[ERROR] Failed to start app: {err}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Exception starting app: {e}")
            return False
    
    def stop_app(self, package: str) -> bool:
        """
        Stop an application (force stop).
        
        Args:
            package: Android package name
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            print("[ERROR] Device not connected")
            return False
        
        adb_cmd = self.platform_utils.get_adb_command()
        
        try:
            print(f"[INFO] Stopping app: {package}")
            code, _, err = self.platform_utils.run_command([
                adb_cmd, "-s", self.serial,
                "shell", "am", "force-stop", package
            ], timeout=10)
            
            if code == 0:
                print(f"[OK] App stopped: {package}")
                return True
            else:
                print(f"[ERROR] Failed to stop app: {err}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Exception stopping app: {e}")
            return False
    
    def is_app_running(self, package: str) -> bool:
        """
        Check if an app is currently running.
        
        Args:
            package: Android package name
        
        Returns:
            bool: True if running, False otherwise
        """
        if not self.is_connected():
            return False
        
        adb_cmd = self.platform_utils.get_adb_command()
        
        try:
            # Get current foreground activity
            code, output, _ = self.platform_utils.run_command([
                adb_cmd, "-s", self.serial,
                "shell", "dumpsys", "window", "windows"
            ], timeout=5)
            
            if code == 0:
                # Check if package is in output
                return package in output
                
        except Exception as e:
            print(f"[WARNING] Error checking app status: {e}")
        
        return False
    
    def get_current_activity(self) -> Optional[str]:
        """
        Get the current foreground activity.
        
        Returns:
            Current activity string (e.g., "com.example.app/.MainActivity")
            or None if unable to retrieve
        """
        if not self.is_connected():
            return None
        
        adb_cmd = self.platform_utils.get_adb_command()
        
        try:
            code, output, _ = self.platform_utils.run_command([
                adb_cmd, "-s", self.serial,
                "shell", "dumpsys", "window", "windows"
            ], timeout=5)
            
            if code == 0:
                # Parse output to find current activity
                for line in output.split('\n'):
                    if 'mCurrentFocus' in line or 'mFocusedApp' in line:
                        # Extract activity from line
                        if 'Window{' in line:
                            # Format: Window{... u0 com.example.app/com.example.app.MainActivity}
                            parts = line.split()
                            for part in parts:
                                if '/' in part and '.' in part:
                                    activity = part.strip()
                                    # Clean up
                                    if activity.startswith('{'):
                                        activity = activity[1:]
                                    if activity.endswith('}'):
                                        activity = activity[:-1]
                                    return activity
                return None
                
        except Exception as e:
            print(f"[WARNING] Error getting current activity: {e}")
        
        return None
    
    def take_screenshot(self, filename: str) -> Optional[Path]:
        """
        Take a screenshot and save it.
        
        Args:
            filename: Filename to save (without path)
        
        Returns:
            Path to saved screenshot, or None if failed
        """
        if not self.is_connected():
            print("[ERROR] Device not connected")
            return None
        
        try:
            # Get screenshots directory
            screenshots_dir = self.platform_utils.get_path("screenshots")
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            
            # Full file path
            screenshot_path = screenshots_dir / filename
            
            print(f"[INFO] Taking screenshot: {filename}")
            
            # Use uiautomator2 to take screenshot
            if self.device:
                self.device.screenshot(str(screenshot_path))
                print(f"[OK] Screenshot saved: {screenshot_path}")
                return screenshot_path
            else:
                # Fallback to ADB
                adb_cmd = self.platform_utils.get_adb_command()
                code, _, _ = self.platform_utils.run_command([
                    adb_cmd, "-s", self.serial,
                    "shell", "screencap", "-p", "/sdcard/screenshot_temp.png"
                ], timeout=10)
                
                if code == 0:
                    # Pull file
                    code, _, _ = self.platform_utils.run_command([
                        adb_cmd, "-s", self.serial,
                        "pull", "/sdcard/screenshot_temp.png", str(screenshot_path)
                    ], timeout=10)
                    
                    if code == 0:
                        # Clean up device
                        self.platform_utils.run_command([
                            adb_cmd, "-s", self.serial,
                            "shell", "rm", "/sdcard/screenshot_temp.png"
                        ])
                        print(f"[OK] Screenshot saved: {screenshot_path}")
                        return screenshot_path
            
            return None
            
        except Exception as e:
            print(f"[ERROR] Failed to take screenshot: {e}")
            return None


# Global instance for convenience
_device_manager: Optional[DeviceManager] = None


def get_device_manager(serial: Optional[str] = None) -> DeviceManager:
    """
    Get the global DeviceManager instance.
    
    Args:
        serial: Optional device serial number
    
    Returns:
        DeviceManager: The global instance
    """
    global _device_manager
    if _device_manager is None:
        _device_manager = DeviceManager(serial)
    return _device_manager