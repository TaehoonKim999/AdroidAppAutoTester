"""
Unit Tests for Phase 5: Test Engine

Tests:
- TestResult dataclass
- TestEngine class (mocked dependencies)
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Mock uiautomator2 before importing modules
sys.modules['uiautomator2'] = Mock()

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.test_engine import TestResult, TestEngine
from src.config_manager import AppConfig, GlobalSettings
from src.device_manager import DeviceManager
from src.log_collector import LogCollector


class TestTestResult:
    """Test cases for TestResult dataclass."""
    
    def test_creation(self):
        """Test TestResult creation with minimal data."""
        result = TestResult(
            app_name="Test App",
            package="com.example.test",
            success=True
        )
        
        assert result.app_name == "Test App"
        assert result.package == "com.example.test"
        assert result.success is True
        assert result.duration == 0.0
        assert result.screens_visited == 0
        
        print("✓ TestResult creation test passed")
    
    def test_creation_with_values(self):
        """Test TestResult creation with all values."""
        result = TestResult(
            app_name="Test App",
            package="com.example.test",
            success=True,
            duration=30.5,
            screens_visited=10,
            elements_interacted=50,
            actions_performed=["Click: OK", "Scroll: down"],
            errors_found=["Error dialog"],
            log_file=Path("/path/to/log.txt"),
            screenshot_files=[Path("/path/to/screenshot.png")],
            retry_count=2,
            error_message="Test error"
        )
        
        assert result.duration == 30.5
        assert result.screens_visited == 10
        assert result.elements_interacted == 50
        assert len(result.actions_performed) == 2
        assert len(result.errors_found) == 1
        assert result.retry_count == 2
        assert result.error_message == "Test error"
        
        print("✓ TestResult creation with values test passed")
    
    def test_to_dict(self):
        """Test TestResult to_dict conversion."""
        result = TestResult(
            app_name="Test App",
            package="com.example.test",
            success=True,
            duration=30.5,
            log_file=Path("/path/to/log.txt"),
            screenshot_files=[Path("/path/to/screenshot.png")]
        )
        
        data = result.to_dict()
        assert isinstance(data, dict)
        assert data["app_name"] == "Test App"
        assert data["success"] is True
        assert data["duration"] == 30.5
        assert isinstance(data["log_file"], str)
        assert isinstance(data["screenshot_files"], list)
        
        print("✓ TestResult to_dict test passed")


class TestTestEngine:
    """Test cases for TestEngine class."""
    
    def test_initialization(self):
        """Test TestEngine initialization."""
        mock_device_manager = Mock(spec=DeviceManager)
        mock_settings = Mock(spec=GlobalSettings)
        
        engine = TestEngine(mock_device_manager, mock_settings)
        
        assert engine.device_manager == mock_device_manager
        assert engine.settings == mock_settings
        assert engine.ui_explorer is None
        assert engine.log_collector is None
        
        print("✓ TestEngine initialization test passed")
    
    def test_initialize_components(self):
        """Test _initialize_components method."""
        mock_device_manager = Mock(spec=DeviceManager)
        mock_settings = Mock(spec=GlobalSettings)
        
        # Mock settings attributes
        mock_settings.logcat_filter = ["E", "W", "F"]
        
        # Mock device info
        mock_device_info = Mock()
        mock_device_info.serial = "TEST123"
        mock_device_manager.get_device_info.return_value = mock_device_info
        
        # Mock device
        mock_device_manager.device = Mock()
        
        engine = TestEngine(mock_device_manager, mock_settings)
        
        app_config = AppConfig(
            name="Test App",
            package="com.example.test",
            activity=".MainActivity"
        )
        
        engine._initialize_components(app_config)
        
        # Check that components are initialized
        assert engine.ui_explorer is not None
        assert engine.log_collector is not None
        
        print("✓ TestEngine _initialize_components test passed")
    
    def test_take_screenshot(self):
        """Test _take_screenshot method."""
        mock_device_manager = Mock(spec=DeviceManager)
        mock_settings = Mock(spec=GlobalSettings)
        
        # Mock connected state
        mock_device_manager.is_connected.return_value = True
        mock_device_manager.take_screenshot.return_value = Path("/path/to/test_20240101_120000.png")
        
        engine = TestEngine(mock_device_manager, mock_settings)
        
        result = engine._take_screenshot("test")
        
        assert result is not None
        assert result.suffix == ".png"
        mock_device_manager.take_screenshot.assert_called_once()
        
        print("✓ TestEngine _take_screenshot test passed")
    
    def test_take_screenshot_not_connected(self):
        """Test _take_screenshot when device not connected."""
        mock_device_manager = Mock(spec=DeviceManager)
        mock_settings = Mock(spec=GlobalSettings)
        
        # Mock disconnected state
        mock_device_manager.is_connected.return_value = False
        
        engine = TestEngine(mock_device_manager, mock_settings)
        
        result = engine._take_screenshot("test")
        
        assert result is None
        mock_device_manager.take_screenshot.assert_not_called()
        
        print("✓ TestEngine _take_screenshot not connected test passed")
    
    def test_take_error_screenshot(self):
        """Test _take_error_screenshot method."""
        mock_device_manager = Mock(spec=DeviceManager)
        mock_settings = Mock(spec=GlobalSettings)
        
        mock_device_manager.is_connected.return_value = True
        mock_device_manager.take_screenshot.return_value = Path("/path/to/test_error_attempt1_20240101_120000.png")
        
        engine = TestEngine(mock_device_manager, mock_settings)
        
        result = engine._take_error_screenshot("test", 1)
        
        assert result is not None
        assert "error" in str(result).lower()
        assert "attempt1" in str(result).lower()
        
        print("✓ TestEngine _take_error_screenshot test passed")
    
    def test_print_test_summary(self):
        """Test _print_test_summary method."""
        mock_device_manager = Mock(spec=DeviceManager)
        mock_settings = Mock(spec=GlobalSettings)
        
        engine = TestEngine(mock_device_manager, mock_settings)
        
        result = TestResult(
            app_name="Test App",
            package="com.example.test",
            success=True,
            duration=30.5,
            screens_visited=10,
            elements_interacted=50,
            actions_performed=["Click: OK"],
            errors_found=[],
            retry_count=0
        )
        
        # Should not raise exception
        engine._print_test_summary(result)
        
        print("✓ TestEngine _print_test_summary test passed")
    
    def test_print_overall_summary(self):
        """Test _print_overall_summary method."""
        mock_device_manager = Mock(spec=DeviceManager)
        mock_settings = Mock(spec=GlobalSettings)
        
        engine = TestEngine(mock_device_manager, mock_settings)
        
        results = [
            TestResult(
                app_name="App 1",
                package="com.example.app1",
                success=True,
                duration=30.5
            ),
            TestResult(
                app_name="App 2",
                package="com.example.app2",
                success=False,
                duration=45.0,
                error_message="Test error"
            )
        ]
        
        # Should not raise exception
        engine._print_overall_summary(results)
        
        print("✓ TestEngine _print_overall_summary test passed")


def run_all_tests():
    """Run all Phase 5 unit tests."""
    print("\n" + "="*60)
    print("  Phase 5: Test Engine Tests")
    print("="*60 + "\n")
    
    print("Testing TestResult...")
    test_test_result = TestTestResult()
    test_test_result.test_creation()
    test_test_result.test_creation_with_values()
    test_test_result.test_to_dict()
    print()
    
    print("Testing TestEngine...")
    test_test_engine = TestTestEngine()
    test_test_engine.test_initialization()
    test_test_engine.test_initialize_components()
    test_test_engine.test_take_screenshot()
    test_test_engine.test_take_screenshot_not_connected()
    test_test_engine.test_take_error_screenshot()
    test_test_engine.test_print_test_summary()
    test_test_engine.test_print_overall_summary()
    print()
    
    print("="*60)
    print("  All Phase 5 Tests Passed! ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()