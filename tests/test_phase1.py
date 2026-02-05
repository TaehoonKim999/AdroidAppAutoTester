"""
Unit Tests for Phase 1: Platform Utils and Config Manager

Tests:
- PlatformUtils class
- ConfigManager class
- AppConfig dataclass
- GlobalSettings dataclass
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.platform_utils import PlatformUtils
from src.config_manager import ConfigManager, AppConfig, GlobalSettings


class TestPlatformUtils:
    """Test cases for PlatformUtils class."""
    
    def __init__(self):
        self.utils = PlatformUtils()
    
    def test_system_detection(self):
        """Test that OS is correctly detected."""
        assert self.utils.system in ["Windows", "Linux"], \
            f"Unknown system: {self.utils.system}"
        
        if self.utils.system == "Windows":
            assert self.utils.is_windows is True
            assert self.utils.is_linux is False
        else:
            assert self.utils.is_windows is False
            assert self.utils.is_linux is True
        
        print("✓ OS detection test passed")
    
    def test_project_root(self):
        """Test that project root path is correctly identified."""
        assert self.utils.project_root.exists(), \
            f"Project root does not exist: {self.utils.project_root}"
        
        # Check that it contains expected directories
        expected_dirs = ["src", "config", "docs"]
        for dir_name in expected_dirs:
            assert (self.utils.project_root / dir_name).exists(), \
                f"Expected directory not found: {dir_name}"
        
        print("✓ Project root test passed")
    
    def test_adb_command(self):
        """Test that ADB command is returned correctly."""
        adb_cmd = self.utils.get_adb_command()
        
        if self.utils.is_windows:
            assert adb_cmd == "adb.exe", \
                f"Expected 'adb.exe' on Windows, got: {adb_cmd}"
        else:
            assert adb_cmd == "adb", \
                f"Expected 'adb' on Linux, got: {adb_cmd}"
        
        print("✓ ADB command test passed")
    
    def test_get_path(self):
        """Test that project directory paths are correctly returned."""
        test_paths = ["config", "screenshots", "reports", "logs", "templates"]
        
        for path_name in test_paths:
            path = self.utils.get_path(path_name)
            assert isinstance(path, Path), \
                f"get_path should return Path, got: {type(path)}"
            assert path.is_absolute(), \
                f"Path should be absolute: {path}"
        
        # Test invalid path name
        try:
            self.utils.get_path("invalid_path")
            assert False, "Should raise ValueError for invalid path name"
        except ValueError as e:
            assert "Unknown path name" in str(e)
        
        print("✓ get_path test passed")
    
    def test_run_command(self):
        """Test that system commands can be executed."""
        # Test simple command
        if self.utils.is_linux:
            code, out, err = self.utils.run_command(["echo", "test"])
        else:
            code, out, err = self.utils.run_command(["cmd", "/c", "echo", "test"])
        
        assert code == 0, f"Command failed with code: {code}"
        assert "test" in out, f"Expected 'test' in output, got: {out}"
        
        print("✓ run_command test passed")
    
    def test_get_connected_devices(self):
        """Test that connected devices can be listed."""
        devices = self.utils.get_connected_devices()
        assert isinstance(devices, list), \
            f"get_connected_devices should return list, got: {type(devices)}"
        
        # Don't assert devices exist (user may not have any connected)
        print(f"✓ get_connected_devices test passed (found {len(devices)} device(s))")


class TestAppConfig:
    """Test cases for AppConfig dataclass."""
    
    def test_creation(self):
        """Test AppConfig creation with valid data."""
        app = AppConfig(
            name="Test App",
            package="com.example.test",
            activity=".MainActivity",
            test_duration=120,
            test_actions=["scroll", "click_buttons"]
        )
        
        assert app.name == "Test App"
        assert app.package == "com.example.test"
        assert app.activity == ".MainActivity"
        assert app.test_duration == 120
        assert "scroll" in app.test_actions
        
        print("✓ AppConfig creation test passed")
    
    def test_defaults(self):
        """Test AppConfig default values."""
        app = AppConfig(
            name="Test App",
            package="com.example.test",
            activity=".MainActivity"
        )
        
        assert app.test_duration == 120  # Default value
        assert "scroll" in app.test_actions  # Default value
        
        print("✓ AppConfig defaults test passed")
    
    def test_to_dict(self):
        """Test AppConfig to_dict conversion."""
        app = AppConfig(
            name="Test App",
            package="com.example.test",
            activity=".MainActivity",
            test_duration=120,
            test_actions=["scroll"]
        )
        
        data = app.to_dict()
        assert isinstance(data, dict)
        assert data["name"] == "Test App"
        assert data["package"] == "com.example.test"
        
        print("✓ AppConfig to_dict test passed")
    
    def test_from_dict(self):
        """Test AppConfig from_dict conversion."""
        data = {
            "name": "Test App",
            "package": "com.example.test",
            "activity": ".MainActivity",
            "test_duration": 90,
            "test_actions": ["scroll", "click_buttons"]
        }
        
        app = AppConfig.from_dict(data)
        assert app.name == "Test App"
        assert app.test_duration == 90
        
        print("✓ AppConfig from_dict test passed")
    
    def test_validation(self):
        """Test AppConfig validation."""
        # Valid config
        valid_app = AppConfig(
            name="Test",
            package="com.example.test",
            activity=".MainActivity"
        )
        assert valid_app.validate() is True
        
        # Invalid config (missing name)
        invalid_app1 = AppConfig(
            name="",
            package="com.example.test",
            activity=".MainActivity"
        )
        assert invalid_app1.validate() is False
        
        # Invalid config (negative duration)
        invalid_app2 = AppConfig(
            name="Test",
            package="com.example.test",
            activity=".MainActivity",
            test_duration=-1
        )
        assert invalid_app2.validate() is False
        
        print("✓ AppConfig validation test passed")


class TestGlobalSettings:
    """Test cases for GlobalSettings dataclass."""
    
    def test_creation(self):
        """Test GlobalSettings creation with valid data."""
        settings = GlobalSettings(
            screenshot_on_error=True,
            screenshot_interval=30,
            collect_logcat=True,
            logcat_filter=["E", "W", "F"],
            report_format="markdown",
            max_test_retries=3,
            delay_between_apps=5
        )
        
        assert settings.screenshot_on_error is True
        assert settings.screenshot_interval == 30
        assert settings.collect_logcat is True
        assert "E" in settings.logcat_filter
        
        print("✓ GlobalSettings creation test passed")
    
    def test_defaults(self):
        """Test GlobalSettings default values."""
        settings = GlobalSettings()
        
        assert settings.screenshot_on_error is True
        assert settings.screenshot_interval == 30
        assert settings.collect_logcat is True
        assert "E" in settings.logcat_filter
        assert settings.report_format == "markdown"
        assert settings.max_test_retries == 3
        
        print("✓ GlobalSettings defaults test passed")
    
    def test_to_dict(self):
        """Test GlobalSettings to_dict conversion."""
        settings = GlobalSettings(
            screenshot_on_error=True,
            screenshot_interval=60
        )
        
        data = settings.to_dict()
        assert isinstance(data, dict)
        assert data["screenshot_on_error"] is True
        assert data["screenshot_interval"] == 60
        
        print("✓ GlobalSettings to_dict test passed")
    
    def test_from_dict(self):
        """Test GlobalSettings from_dict conversion."""
        data = {
            "screenshot_on_error": False,
            "screenshot_interval": 60,
            "collect_logcat": False,
            "logcat_filter": ["E"],
            "report_format": "markdown",
            "max_test_retries": 5,
            "delay_between_apps": 10
        }
        
        settings = GlobalSettings.from_dict(data)
        assert settings.screenshot_on_error is False
        assert settings.screenshot_interval == 60
        assert settings.max_test_retries == 5
        
        print("✓ GlobalSettings from_dict test passed")
    
    def test_validation(self):
        """Test GlobalSettings validation."""
        # Valid config
        valid_settings = GlobalSettings()
        assert valid_settings.validate() is True
        
        # Invalid config (negative interval)
        invalid_settings1 = GlobalSettings(screenshot_interval=-1)
        assert invalid_settings1.validate() is False
        
        # Invalid config (wrong format)
        invalid_settings2 = GlobalSettings(report_format="html")
        assert invalid_settings2.validate() is False
        
        print("✓ GlobalSettings validation test passed")


class TestConfigManager:
    """Test cases for ConfigManager class."""
    
    def __init__(self):
        self.config_dir = Path(__file__).parent.parent / "config"
        self.test_apps_file = self.config_dir / "test_apps.json"
        self.test_settings_file = self.config_dir / "test_settings.json"
    
    def test_load_apps_from_sample(self):
        """Test loading apps from sample file."""
        sample_file = self.config_dir / "apps.json.sample"
        
        if not sample_file.exists():
            print("⚠ Skipping test: apps.json.sample not found")
            return
        
        # Create temporary config manager with sample file
        manager = ConfigManager(apps_file="apps.json.sample")
        apps = manager.load_apps()
        
        assert isinstance(apps, list)
        assert len(apps) > 0
        
        for app in apps:
            assert isinstance(app, AppConfig)
            assert app.validate() is True
        
        print(f"✓ ConfigManager load_apps test passed (loaded {len(apps)} apps)")
    
    def test_load_settings_from_sample(self):
        """Test loading settings from sample file."""
        sample_file = self.config_dir / "settings.json.sample"
        
        if not sample_file.exists():
            print("⚠ Skipping test: settings.json.sample not found")
            return
        
        # Create temporary config manager with sample file
        manager = ConfigManager(settings_file="settings.json.sample")
        settings = manager.load_settings()
        
        assert isinstance(settings, GlobalSettings)
        assert settings.validate() is True
        
        print("✓ ConfigManager load_settings test passed")
    
    def test_save_and_load_apps(self):
        """Test saving and loading apps."""
        # Create test apps
        test_apps = [
            AppConfig(
                name="Test App 1",
                package="com.example.test1",
                activity=".MainActivity"
            ),
            AppConfig(
                name="Test App 2",
                package="com.example.test2",
                activity=".MainActivity"
            )
        ]
        
        # Save to test file
        manager = ConfigManager(apps_file="test_apps.json")
        manager.save_apps(test_apps)
        
        # Load back
        loaded_apps = manager.load_apps()
        
        assert len(loaded_apps) == 2
        assert loaded_apps[0].name == "Test App 1"
        assert loaded_apps[1].package == "com.example.test2"
        
        # Clean up
        if self.test_apps_file.exists():
            self.test_apps_file.unlink()
        
        print("✓ ConfigManager save/load apps test passed")
    
    def test_save_and_load_settings(self):
        """Test saving and loading settings."""
        # Create test settings
        test_settings = GlobalSettings(
            screenshot_on_error=False,
            screenshot_interval=60,
            max_test_retries=5
        )
        
        # Save to test file
        manager = ConfigManager(settings_file="test_settings.json")
        manager.save_settings(test_settings)
        
        # Load back
        loaded_settings = manager.load_settings()
        
        assert loaded_settings.screenshot_on_error is False
        assert loaded_settings.screenshot_interval == 60
        assert loaded_settings.max_test_retries == 5
        
        # Clean up
        if self.test_settings_file.exists():
            self.test_settings_file.unlink()
        
        print("✓ ConfigManager save/load settings test passed")


def run_all_tests():
    """Run all Phase 1 unit tests."""
    print("\n" + "="*60)
    print("  Phase 1: Platform Utils and Config Manager Tests")
    print("="*60 + "\n")
    
    # Test PlatformUtils
    print("Testing PlatformUtils...")
    test_platform = TestPlatformUtils()
    test_platform.test_system_detection()
    test_platform.test_project_root()
    test_platform.test_adb_command()
    test_platform.test_get_path()
    test_platform.test_run_command()
    test_platform.test_get_connected_devices()
    print()
    
    # Test AppConfig
    print("Testing AppConfig...")
    test_app_config = TestAppConfig()
    test_app_config.test_creation()
    test_app_config.test_defaults()
    test_app_config.test_to_dict()
    test_app_config.test_from_dict()
    test_app_config.test_validation()
    print()
    
    # Test GlobalSettings
    print("Testing GlobalSettings...")
    test_global_settings = TestGlobalSettings()
    test_global_settings.test_creation()
    test_global_settings.test_defaults()
    test_global_settings.test_to_dict()
    test_global_settings.test_from_dict()
    test_global_settings.test_validation()
    print()
    
    # Test ConfigManager
    print("Testing ConfigManager...")
    test_config_manager = TestConfigManager()
    test_config_manager.test_load_apps_from_sample()
    test_config_manager.test_load_settings_from_sample()
    test_config_manager.test_save_and_load_apps()
    test_config_manager.test_save_and_load_settings()
    print()
    
    print("="*60)
    print("  All Phase 1 Tests Passed! ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()