"""
Unit Tests for Phase 2: Device Manager

Tests:
- DeviceInfo dataclass
- DeviceManager class (without actual device connection)
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Mock uiautomator2 before importing device_manager
sys.modules['uiautomator2'] = Mock()

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.device_manager import DeviceInfo, DeviceManager
from src.platform_utils import get_platform_utils


class TestDeviceInfo:
    """Test cases for DeviceInfo dataclass."""
    
    def test_creation(self):
        """Test DeviceInfo creation with valid data."""
        info = DeviceInfo(
            serial="ABC123",
            model="Test Device",
            android_version="13",
            sdk_version=33
        )
        
        assert info.serial == "ABC123"
        assert info.model == "Test Device"
        assert info.android_version == "13"
        assert info.sdk_version == 33
        
        print("✓ DeviceInfo creation test passed")
    
    def test_to_dict(self):
        """Test DeviceInfo to_dict conversion."""
        info = DeviceInfo(
            serial="XYZ789",
            model="Another Device",
            android_version="12",
            sdk_version=31
        )
        
        data = info.to_dict()
        assert isinstance(data, dict)
        assert data["serial"] == "XYZ789"
        assert data["model"] == "Another Device"
        assert data["android_version"] == "12"
        assert data["sdk_version"] == 31
        
        print("✓ DeviceInfo to_dict test passed")
    
    def test_str_representation(self):
        """Test DeviceInfo string representation."""
        info = DeviceInfo(
            serial="ABC123",
            model="Galaxy S23",
            android_version="14",
            sdk_version=34
        )
        
        info_str = str(info)
        assert "Galaxy S23" in info_str
        assert "Android 14" in info_str
        assert "SDK 34" in info_str
        
        print("✓ DeviceInfo str representation test passed")


class TestDeviceManager:
    """Test cases for DeviceManager class (mocked, no actual device)."""
    
    def test_initialization(self):
        """Test DeviceManager initialization."""
        manager = DeviceManager(serial="TEST123")
        
        assert manager.serial == "TEST123"
        assert manager.device is None
        assert manager.device_info is None
        assert manager.is_connected() is False
        
        print("✓ DeviceManager initialization test passed")
    
    def test_initialization_without_serial(self):
        """Test DeviceManager initialization without serial (uses first device)."""
        manager = DeviceManager()
        
        assert manager.serial is None
        assert manager.device is None
        
        print("✓ DeviceManager initialization without serial test passed")
    
    @patch('src.device_manager.u2')
    def test_connection_without_adb(self, mock_u2):
        """Test connection fails when ADB is not available."""
        # Mock platform utils to return no ADB
        manager = DeviceManager(serial="TEST123")
        
        with patch.object(manager.platform_utils, 'check_adb_available', return_value=False):
            result = manager.connect()
        
        assert result is False
        assert manager.is_connected() is False
        
        print("✓ DeviceManager connection without ADB test passed")
    
    @patch('src.device_manager.u2')
    def test_connection_no_devices(self, mock_u2):
        """Test connection fails when no devices are found."""
        manager = DeviceManager(serial="TEST123")
        
        # Mock no devices available
        with patch.object(manager.platform_utils, 'get_connected_devices', return_value=[]):
            result = manager.connect()
        
        assert result is False
        
        print("✓ DeviceManager connection with no devices test passed")
    
    @patch('src.device_manager.u2')
    def test_connection_device_not_found(self, mock_u2):
        """Test connection fails when specified device is not found."""
        manager = DeviceManager(serial="TEST123")
        
        # Mock different device available
        with patch.object(manager.platform_utils, 'get_connected_devices', return_value=["OTHER999"]):
            result = manager.connect()
        
        assert result is False
        
        print("✓ DeviceManager connection with device not found test passed")
    
    def test_get_device_info_when_not_connected(self):
        """Test get_device_info returns None when not connected."""
        manager = DeviceManager(serial="TEST123")
        
        info = manager.get_device_info()
        assert info is None
        
        print("✓ DeviceManager get_device_info when not connected test passed")
    
    def test_disconnect(self):
        """Test disconnect method."""
        manager = DeviceManager(serial="TEST123")
        
        # Simulate connected state
        manager._connected = True
        manager.device = Mock()
        manager.device_info = DeviceInfo(
            serial="TEST123",
            model="Test",
            android_version="13",
            sdk_version=33
        )
        
        manager.disconnect()
        
        assert manager.is_connected() is False
        assert manager.device is None
        assert manager.device_info is None
        
        print("✓ DeviceManager disconnect test passed")
    
    def test_start_app_when_not_connected(self):
        """Test start_app fails when not connected."""
        manager = DeviceManager(serial="TEST123")
        
        result = manager.start_app("com.example.app", ".MainActivity")
        
        assert result is False
        
        print("✓ DeviceManager start_app when not connected test passed")
    
    def test_stop_app_when_not_connected(self):
        """Test stop_app fails when not connected."""
        manager = DeviceManager(serial="TEST123")
        
        result = manager.stop_app("com.example.app")
        
        assert result is False
        
        print("✓ DeviceManager stop_app when not connected test passed")
    
    def test_is_app_running_when_not_connected(self):
        """Test is_app_running returns False when not connected."""
        manager = DeviceManager(serial="TEST123")
        
        result = manager.is_app_running("com.example.app")
        
        assert result is False
        
        print("✓ DeviceManager is_app_running when not connected test passed")
    
    def test_get_current_activity_when_not_connected(self):
        """Test get_current_activity returns None when not connected."""
        manager = DeviceManager(serial="TEST123")
        
        result = manager.get_current_activity()
        
        assert result is None
        
        print("✓ DeviceManager get_current_activity when not connected test passed")
    
    def test_take_screenshot_when_not_connected(self):
        """Test take_screenshot returns None when not connected."""
        manager = DeviceManager(serial="TEST123")
        
        result = manager.take_screenshot("test.png")
        
        assert result is None
        
        print("✓ DeviceManager take_screenshot when not connected test passed")
    
    @patch('src.device_manager.u2')
    def test_get_device_info_retrieval(self, mock_u2):
        """Test _get_device_info retrieves correct information."""
        manager = DeviceManager(serial="TEST123")
        manager._connected = True
        manager.device = Mock()
        
        # Mock ADB commands to return device info
        def mock_run_command(cmd, **kwargs):
            if "ro.product.model" in cmd:
                return 0, "Galaxy S23", ""
            elif "ro.build.version.release" in cmd:
                return 0, "14", ""
            elif "ro.build.version.sdk" in cmd:
                return 0, "34", ""
            return 1, "", "Command failed"
        
        with patch.object(manager.platform_utils, 'run_command', side_effect=mock_run_command):
            info = manager._get_device_info()
        
        assert info.model == "Galaxy S23"
        assert info.android_version == "14"
        assert info.sdk_version == 34
        assert info.serial == "TEST123"
        
        print("✓ DeviceManager _get_device_info retrieval test passed")
    
    @patch('src.device_manager.u2')
    def test_get_device_info_with_fallbacks(self, mock_u2):
        """Test _get_device_info handles missing information."""
        manager = DeviceManager(serial="TEST123")
        manager._connected = True
        manager.device = Mock()
        
        # Mock ADB commands to return empty/invalid data
        def mock_run_command(cmd, **kwargs):
            return 0, "", ""  # Empty output
        
        with patch.object(manager.platform_utils, 'run_command', side_effect=mock_run_command):
            info = manager._get_device_info()
        
        assert info.model == "Unknown"
        assert info.android_version == "Unknown"
        assert info.sdk_version == 0
        
        print("✓ DeviceManager _get_device_info with fallbacks test passed")


class TestDeviceManagerIntegration:
    """Integration tests for DeviceManager (with mocked uiautomator2)."""
    
    @patch('src.device_manager.u2')
    def test_full_connection_workflow(self, mock_u2):
        """Test full connection workflow with mocked uiautomator2."""
        # Create mock device
        mock_device = Mock()
        mock_u2.connect.return_value = mock_device
        
        manager = DeviceManager(serial="TEST123")
        
        # Mock platform utils
        with patch.object(manager.platform_utils, 'check_adb_available', return_value=True), \
             patch.object(manager.platform_utils, 'get_connected_devices', return_value=["TEST123"]):
            
            # Test connection
            result = manager.connect()
            
            assert result is True
            assert manager.is_connected() is True
            assert manager.device == mock_device
            assert mock_u2.connect.called
        
        print("✓ DeviceManager full connection workflow test passed")
    
    @patch('src.device_manager.u2')
    def test_connection_with_retries(self, mock_u2):
        """Test connection retries on failure."""
        # Make first two attempts fail, third succeed
        mock_device = Mock()
        mock_u2.connect.side_effect = [
            Exception("Connection failed"),
            Exception("Connection failed"),
            mock_device
        ]
        
        manager = DeviceManager(serial="TEST123")
        
        with patch.object(manager.platform_utils, 'check_adb_available', return_value=True), \
             patch.object(manager.platform_utils, 'get_connected_devices', return_value=["TEST123"]), \
             patch('time.sleep'):  # Mock sleep to speed up test
            
            result = manager.connect()
        
        # Should succeed on third attempt
        assert result is True
        assert manager.is_connected() is True
        assert mock_u2.connect.call_count == 3
        
        print("✓ DeviceManager connection with retries test passed")


def run_all_tests():
    """Run all Phase 2 unit tests."""
    print("\n" + "="*60)
    print("  Phase 2: Device Manager Tests")
    print("="*60 + "\n")
    
    print("Testing DeviceInfo...")
    test_device_info = TestDeviceInfo()
    test_device_info.test_creation()
    test_device_info.test_to_dict()
    test_device_info.test_str_representation()
    print()
    
    print("Testing DeviceManager (unit tests)...")
    test_device_manager = TestDeviceManager()
    test_device_manager.test_initialization()
    test_device_manager.test_initialization_without_serial()
    test_device_manager.test_connection_without_adb()
    test_device_manager.test_connection_no_devices()
    test_device_manager.test_connection_device_not_found()
    test_device_manager.test_get_device_info_when_not_connected()
    test_device_manager.test_disconnect()
    test_device_manager.test_start_app_when_not_connected()
    test_device_manager.test_stop_app_when_not_connected()
    test_device_manager.test_is_app_running_when_not_connected()
    test_device_manager.test_get_current_activity_when_not_connected()
    test_device_manager.test_take_screenshot_when_not_connected()
    test_device_manager.test_get_device_info_retrieval()
    test_device_manager.test_get_device_info_with_fallbacks()
    print()
    
    print("Testing DeviceManager (integration tests)...")
    test_integration = TestDeviceManagerIntegration()
    test_integration.test_full_connection_workflow()
    test_integration.test_connection_with_retries()
    print()
    
    print("="*60)
    print("  All Phase 2 Tests Passed! ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()