"""
Custom exceptions for Android App Auto Tester.

Provides hierarchical exception classes for better error handling
and debugging throughout the application.
"""


class AutoTesterError(Exception):
    """Base exception for all Auto Tester errors."""

    def __init__(self, message: str, details: dict = None):
        """
        Initialize AutoTesterError.

        Args:
            message: Human-readable error message
            details: Optional dict with additional context
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        """Return formatted error message."""
        if self.details:
            detail_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({detail_str})"
        return self.message


# ==================== Device Errors ====================

class DeviceError(AutoTesterError):
    """Base exception for device-related errors."""
    pass


class DeviceNotFoundError(DeviceError):
    """Raised when specified device is not found or not connected."""
    pass


class DeviceConnectionError(DeviceError):
    """Raised when connection to device fails."""
    pass


class DeviceTimeoutError(DeviceError):
    """Raised when device operation times out."""
    pass


class DeviceDisconnectedError(DeviceError):
    """Raised when device disconnects during operation."""
    pass


class ADBError(DeviceError):
    """Raised when ADB command fails."""
    pass


# ==================== Configuration Errors ====================

class ConfigError(AutoTesterError):
    """Base exception for configuration-related errors."""
    pass


class ConfigNotFoundError(ConfigError):
    """Raised when configuration file is not found."""
    pass


class ConfigValidationError(ConfigError):
    """Raised when configuration validation fails."""
    pass


class ConfigParseError(ConfigError):
    """Raised when configuration file cannot be parsed."""
    pass


# ==================== Test Execution Errors ====================

class TestError(AutoTesterError):
    """Base exception for test execution errors."""
    pass


class TestFailedError(TestError):
    """Raised when test execution fails."""
    pass


class UIExplorationError(TestError):
    """Raised when UI exploration fails."""
    pass


class AppLaunchError(TestError):
    """Raised when app fails to launch."""
    pass


class LogCollectionError(TestError):
    """Raised when log collection fails."""
    pass


class TestTimeoutError(TestError):
    """Raised when test exceeds maximum duration."""
    pass


# ==================== UI Errors ====================

class UIError(AutoTesterError):
    """Base exception for UI-related errors."""
    pass


class UIElementNotFoundError(UIError):
    """Raised when UI element cannot be found."""
    pass


class UIInteractionError(UIError):
    """Raised when UI interaction fails."""
    pass


# ==================== Log Errors ====================

class LogError(AutoTesterError):
    """Base exception for log-related errors."""
    pass


class LogParseError(LogError):
    """Raised when log parsing fails."""
    pass


# ==================== Report Generation Errors ====================

class ReportError(AutoTesterError):
    """Base exception for report generation errors."""
    pass


class ReportTemplateError(ReportError):
    """Raised when report template is invalid or not found."""
    pass


class ReportGenerationError(ReportError):
    """Raised when report generation fails."""
    pass


# ==================== Platform Errors ====================

class PlatformError(AutoTesterError):
    """Base exception for platform-specific errors."""
    pass


class UnsupportedPlatformError(PlatformError):
    """Raised when running on unsupported platform."""
    pass


class PlatformCommandError(PlatformError):
    """Raised when platform-specific command fails."""
    pass


# ==================== GUI Errors ====================

class GUIError(AutoTesterError):
    """Base exception for GUI-related errors."""
    pass


class GUIInitializationError(GUIError):
    """Raised when GUI component fails to initialize."""
    pass


class GUIUpdateError(GUIError):
    """Raised when GUI update operation fails."""
    pass
