"""
Configuration Manager Module

Handles loading and management of configuration files.
Manages app-specific configurations and global settings.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from .platform_utils import get_platform_utils


@dataclass
class AppConfig:
    """
    Configuration for a single application to test.
    
    Attributes:
        name: Display name of the application
        package: Android package name (e.g., "com.example.app")
        activity: Main activity name (e.g., ".MainActivity")
        test_duration: Test duration in seconds
        test_actions: List of test actions to perform
    """
    name: str
    package: str
    activity: str
    test_duration: int = 120
    test_actions: List[str] = field(default_factory=lambda: ["scroll", "click_buttons"])
    
    def to_dict(self) -> dict:
        """Convert AppConfig to dictionary."""
        return {
            "name": self.name,
            "package": self.package,
            "activity": self.activity,
            "test_duration": self.test_duration,
            "test_actions": self.test_actions
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AppConfig':
        """Create AppConfig from dictionary."""
        return cls(
            name=data["name"],
            package=data["package"],
            activity=data["activity"],
            test_duration=data.get("test_duration", 120),
            test_actions=data.get("test_actions", ["scroll", "click_buttons"])
        )
    
    def validate(self) -> bool:
        """
        Validate the configuration.
        
        Returns:
            bool: True if valid, False otherwise
        """
        if not self.name or not isinstance(self.name, str):
            return False
        if not self.package or not isinstance(self.package, str):
            return False
        if not self.activity or not isinstance(self.activity, str):
            return False
        if not isinstance(self.test_duration, int) or self.test_duration <= 0:
            return False
        if not isinstance(self.test_actions, list) or len(self.test_actions) == 0:
            return False
        return True


@dataclass
class GlobalSettings:
    """
    Global settings for the tester.
    
    Attributes:
        screenshot_on_error: Take screenshot when error occurs
        screenshot_interval: Interval for periodic screenshots (seconds, 0=disabled)
        collect_logcat: Whether to collect logcat logs
        logcat_filter: Log levels to collect (E=Error, W=Warning, F=Fatal)
        report_format: Report format (currently only "markdown" supported)
        max_test_retries: Maximum number of retries for failed tests
        delay_between_apps: Delay between testing different apps (seconds)
    """
    screenshot_on_error: bool = True
    screenshot_interval: int = 30
    collect_logcat: bool = True
    logcat_filter: List[str] = field(default_factory=lambda: ["E", "W", "F"])
    report_format: str = "markdown"
    max_test_retries: int = 3
    delay_between_apps: int = 5
    
    def to_dict(self) -> dict:
        """Convert GlobalSettings to dictionary."""
        return {
            "screenshot_on_error": self.screenshot_on_error,
            "screenshot_interval": self.screenshot_interval,
            "collect_logcat": self.collect_logcat,
            "logcat_filter": self.logcat_filter,
            "report_format": self.report_format,
            "max_test_retries": self.max_test_retries,
            "delay_between_apps": self.delay_between_apps
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GlobalSettings':
        """Create GlobalSettings from dictionary."""
        return cls(
            screenshot_on_error=data.get("screenshot_on_error", True),
            screenshot_interval=data.get("screenshot_interval", 30),
            collect_logcat=data.get("collect_logcat", True),
            logcat_filter=data.get("logcat_filter", ["E", "W", "F"]),
            report_format=data.get("report_format", "markdown"),
            max_test_retries=data.get("max_test_retries", 3),
            delay_between_apps=data.get("delay_between_apps", 5)
        )
    
    def validate(self) -> bool:
        """
        Validate the settings.
        
        Returns:
            bool: True if valid, False otherwise
        """
        if not isinstance(self.screenshot_on_error, bool):
            return False
        if not isinstance(self.screenshot_interval, int) or self.screenshot_interval < 0:
            return False
        if not isinstance(self.collect_logcat, bool):
            return False
        if not isinstance(self.logcat_filter, list) or len(self.logcat_filter) == 0:
            return False
        valid_filters = {"E", "W", "F", "I", "D", "V"}
        if not all(f in valid_filters for f in self.logcat_filter):
            return False
        if not isinstance(self.report_format, str) or self.report_format != "markdown":
            return False
        if not isinstance(self.max_test_retries, int) or self.max_test_retries < 0:
            return False
        if not isinstance(self.delay_between_apps, int) or self.delay_between_apps < 0:
            return False
        return True


class ConfigManager:
    """
    Manager for loading and saving configuration files.
    
    Handles loading of apps.json and settings.json files,
    and provides validation of configuration data.
    
    Attributes:
        platform_utils: PlatformUtils instance for path management
        apps_file: Path to apps.json
        settings_file: Path to settings.json
    """
    
    DEFAULT_APPS_FILE = "apps.json"
    DEFAULT_SETTINGS_FILE = "settings.json"
    
    def __init__(self, apps_file: Optional[str] = None, settings_file: Optional[str] = None):
        """
        Initialize ConfigManager.
        
        Args:
            apps_file: Path to apps.json (default: config/apps.json)
            settings_file: Path to settings.json (default: config/settings.json)
        """
        self.platform_utils = get_platform_utils()
        
        # Set file paths
        config_dir = self.platform_utils.get_path("config")
        self.apps_file = config_dir / (apps_file or self.DEFAULT_APPS_FILE)
        self.settings_file = config_dir / (settings_file or self.DEFAULT_SETTINGS_FILE)
    
    def load_apps(self) -> List[AppConfig]:
        """
        Load app configurations from apps.json.
        
        Returns:
            List of AppConfig objects
        
        Raises:
            FileNotFoundError: If apps.json doesn't exist
            json.JSONDecodeError: If JSON is invalid
            ValueError: If configuration is invalid
        """
        if not self.apps_file.exists():
            raise FileNotFoundError(
                f"Apps configuration file not found: {self.apps_file}\n"
                f"Please create file or copy from {self.apps_file}.sample"
            )
        
        with open(self.apps_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if "apps" not in data:
            raise ValueError("Invalid apps.json: 'apps' key not found")
        
        apps = []
        for app_data in data["apps"]:
            app_config = AppConfig.from_dict(app_data)
            if not app_config.validate():
                raise ValueError(f"Invalid app configuration: {app_data}")
            apps.append(app_config)
        
        return apps
    
    def load_settings(self) -> GlobalSettings:
        """
        Load global settings from settings.json.
        
        Returns:
            GlobalSettings object
        
        Raises:
            FileNotFoundError: If settings.json doesn't exist
            json.JSONDecodeError: If JSON is invalid
            ValueError: If settings are invalid
        """
        if not self.settings_file.exists():
            raise FileNotFoundError(
                f"Settings file not found: {self.settings_file}\n"
                f"Please create file or copy from {self.settings_file}.sample"
            )
        
        with open(self.settings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        settings = GlobalSettings.from_dict(data)
        if not settings.validate():
            raise ValueError(f"Invalid settings: {data}")
        
        return settings
    
    def save_apps(self, apps: List[AppConfig]) -> None:
        """
        Save app configurations to apps.json.
        
        Args:
            apps: List of AppConfig objects to save
        """
        data = {
            "apps": [app.to_dict() for app in apps]
        }
        
        # Ensure directory exists
        self.apps_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.apps_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def save_settings(self, settings: GlobalSettings) -> None:
        """
        Save global settings to settings.json.
        
        Args:
            settings: GlobalSettings object to save
        """
        data = settings.to_dict()
        
        # Ensure directory exists
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def validate(self) -> bool:
        """
        Validate all configuration files.
        
        Returns:
            bool: True if all configurations are valid, False otherwise
        """
        try:
            # Try to load apps
            apps = self.load_apps()
            if not apps:
                return False
            
            # Try to load settings
            settings = self.load_settings()
            
            return True
        except Exception:
            return False


# Global instances for convenience
_config_manager: Optional[ConfigManager] = None
_global_settings: Optional[GlobalSettings] = None


def get_config_manager() -> ConfigManager:
    """
    Get the global ConfigManager instance.
    
    Returns:
        ConfigManager: The global instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_global_settings() -> GlobalSettings:
    """
    Get the global settings.
    
    Returns:
        GlobalSettings: The global settings instance
    """
    global _global_settings
    if _global_settings is None:
        config_mgr = get_config_manager()
        try:
            _global_settings = config_mgr.load_settings()
        except (FileNotFoundError, ValueError, json.JSONDecodeError):
            # If settings file doesn't exist or is invalid, use defaults
            _global_settings = GlobalSettings()
    return _global_settings