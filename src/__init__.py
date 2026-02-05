"""
Android App Auto Tester - Source Code Package

This package contains the core modules for the Android App Auto Tester system.
"""

__version__ = "1.0.0"
__author__ = "Android App Auto Tester Team"

# Import key classes for convenience
from .platform_utils import PlatformUtils
from .config_manager import ConfigManager, AppConfig, GlobalSettings

__all__ = [
    "PlatformUtils",
    "ConfigManager",
    "AppConfig",
    "GlobalSettings",
]