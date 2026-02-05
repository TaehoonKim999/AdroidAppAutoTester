"""
Unit Tests for Phase 3: UI Explorer

Tests:
- UIElement dataclass
- ExplorationResult dataclass
- UIExplorer class (mocked, no actual device)
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Mock uiautomator2 before importing ui_explorer
sys.modules['uiautomator2'] = Mock()

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui_explorer import UIElement, ExplorationResult, UIExplorer


class TestUIElement:
    """Test cases for UIElement dataclass."""
    
    def test_creation(self):
        """Test UIElement creation with valid data."""
        element = UIElement(
            resource_id="test_btn",
            class_name="android.widget.Button",
            text="OK",
            content_desc="Confirm button",
            bounds=(100, 200, 300, 400),
            clickable=True,
            scrollable=False
        )
        
        assert element.resource_id == "test_btn"
        assert element.class_name == "android.widget.Button"
        assert element.text == "OK"
        assert element.bounds == (100, 200, 300, 400)
        assert element.clickable is True
        assert element.scrollable is False
        
        print("✓ UIElement creation test passed")
    
    def test_to_dict(self):
        """Test UIElement to_dict conversion."""
        element = UIElement(
            resource_id="test_btn",
            class_name="android.widget.Button",
            text="OK",
            content_desc="",
            bounds=(100, 200, 300, 400),
            clickable=True,
            scrollable=False
        )
        
        data = element.to_dict()
        assert isinstance(data, dict)
        assert data["resource_id"] == "test_btn"
        assert data["text"] == "OK"
        assert data["clickable"] is True
        
        print("✓ UIElement to_dict test passed")
    
    def test_get_signature(self):
        """Test UIElement signature generation."""
        element = UIElement(
            resource_id="test_btn",
            class_name="android.widget.Button",
            text="OK",
            content_desc="",
            bounds=(100, 200, 300, 400),
            clickable=True,
            scrollable=False
        )
        
        sig = element.get_signature()
        assert isinstance(sig, str)
        assert len(sig) == 32  # MD5 hash length
        
        print("✓ UIElement get_signature test passed")


class TestExplorationResult:
    """Test cases for ExplorationResult dataclass."""
    
    def test_creation(self):
        """Test ExplorationResult creation with default values."""
        result = ExplorationResult()
        
        assert result.screens_visited == 0
        assert result.elements_interacted == 0
        assert len(result.actions_performed) == 0
        assert len(result.errors_found) == 0
        assert result.duration == 0.0
        
        print("✓ ExplorationResult creation test passed")
    
    def test_creation_with_values(self):
        """Test ExplorationResult creation with custom values."""
        result = ExplorationResult(
            screens_visited=5,
            elements_interacted=20,
            actions_performed=["Click: OK", "Scroll: down"],
            errors_found=["Error dialog closed"],
            duration=30.5
        )
        
        assert result.screens_visited == 5
        assert result.elements_interacted == 20
        assert len(result.actions_performed) == 2
        assert len(result.errors_found) == 1
        assert result.duration == 30.5
        
        print("✓ ExplorationResult creation with values test passed")
    
    def test_to_dict(self):
        """Test ExplorationResult to_dict conversion."""
        result = ExplorationResult(
            screens_visited=3,
            elements_interacted=10,
            actions_performed=["Click: OK"],
            errors_found=[],
            duration=15.0
        )
        
        data = result.to_dict()
        assert isinstance(data, dict)
        assert data["screens_visited"] == 3
        assert data["elements_interacted"] == 10
        assert data["duration"] == 15.0
        
        print("✓ ExplorationResult to_dict test passed")


class TestUIExplorer:
    """Test cases for UIExplorer class (mocked, no actual device)."""
    
    def test_initialization(self):
        """Test UIExplorer initialization."""
        mock_device = Mock()
        explorer = UIExplorer(mock_device)
        
        assert explorer.device == mock_device
        assert len(explorer.visited_screens) == 0
        assert isinstance(explorer.result, ExplorationResult)
        assert explorer.start_time == 0.0
        assert explorer._stop_requested is False
        
        print("✓ UIExplorer initialization test passed")
    
    def test_stop(self):
        """Test stop method."""
        mock_device = Mock()
        explorer = UIExplorer(mock_device)
        
        assert explorer._stop_requested is False
        explorer.stop()
        assert explorer._stop_requested is True
        
        print("✓ UIExplorer stop test passed")
    
    def test_get_all_elements(self):
        """Test get_all_elements with mock XML."""
        mock_device = Mock()
        explorer = UIExplorer(mock_device)
        
        # Mock XML hierarchy
        xml = '''
        <hierarchy>
            <node resource-id="com.app:id/button1" class="android.widget.Button" text="OK" 
                  content-desc="" clickable="true" scrollable="false" 
                  bounds="[100,200][300,400]" />
            <node resource-id="com.app:id/scroll_view" class="android.widget.ScrollView" 
                  text="" content-desc="" clickable="false" scrollable="true" 
                  bounds="[0,0][1080,1920]" />
        </hierarchy>
        '''
        
        mock_device.dump_hierarchy.return_value = xml
        elements = explorer.get_all_elements()
        
        assert len(elements) == 2
        assert elements[0].class_name == "android.widget.Button"
        assert elements[1].class_name == "android.widget.ScrollView"
        
        print("✓ UIExplorer get_all_elements test passed")
    
    def test_get_clickable_elements(self):
        """Test get_clickable_elements."""
        mock_device = Mock()
        explorer = UIExplorer(mock_device)
        
        # Mock XML with clickable and non-clickable elements
        xml = '''
        <hierarchy>
            <node resource-id="btn1" class="android.widget.Button" text="OK" 
                  content-desc="" clickable="true" scrollable="false" 
                  bounds="[100,200][300,400]" />
            <node resource-id="label1" class="android.widget.TextView" text="Hello" 
                  content-desc="" clickable="false" scrollable="false" 
                  bounds="[100,500][300,600]" />
            <node resource-id="btn2" class="android.widget.Button" text="Cancel" 
                  content-desc="" clickable="true" scrollable="false" 
                  bounds="[400,200][600,400]" />
        </hierarchy>
        '''
        
        mock_device.dump_hierarchy.return_value = xml
        clickable = explorer.get_clickable_elements()
        
        assert len(clickable) == 2
        assert all(el.clickable for el in clickable)
        
        print("✓ UIExplorer get_clickable_elements test passed")
    
    def test_get_scrollable_elements(self):
        """Test get_scrollable_elements."""
        mock_device = Mock()
        explorer = UIExplorer(mock_device)
        
        # Mock XML with scrollable and non-scrollable elements
        xml = '''
        <hierarchy>
            <node resource-id="scroll1" class="android.widget.ScrollView" text="" 
                  content-desc="" clickable="false" scrollable="true" 
                  bounds="[0,0][1080,1920]" />
            <node resource-id="btn1" class="android.widget.Button" text="OK" 
                  content-desc="" clickable="true" scrollable="false" 
                  bounds="[100,200][300,400]" />
        </hierarchy>
        '''
        
        mock_device.dump_hierarchy.return_value = xml
        scrollable = explorer.get_scrollable_elements()
        
        assert len(scrollable) == 1
        assert scrollable[0].scrollable is True
        
        print("✓ UIExplorer get_scrollable_elements test passed")
    
    def test_get_input_fields(self):
        """Test get_input_fields."""
        mock_device = Mock()
        explorer = UIExplorer(mock_device)
        
        # Mock XML with EditText fields
        xml = '''
        <hierarchy>
            <node resource-id="input1" class="android.widget.EditText" text="" 
                  content-desc="" clickable="true" scrollable="false" 
                  bounds="[100,200][980,300]" />
            <node resource-id="btn1" class="android.widget.Button" text="OK" 
                  content-desc="" clickable="true" scrollable="false" 
                  bounds="[400,500][680,600]" />
            <node resource-id="input2" class="android.widget.AutoCompleteTextView" 
                  text="" content-desc="" clickable="true" scrollable="false" 
                  bounds="[100,400][980,500]" />
        </hierarchy>
        '''
        
        mock_device.dump_hierarchy.return_value = xml
        inputs = explorer.get_input_fields()
        
        assert len(inputs) == 2
        
        print("✓ UIExplorer get_input_fields test passed")
    
    def test_click_element(self):
        """Test click_element with mock device."""
        mock_device = Mock()
        explorer = UIExplorer(mock_device)
        
        element = UIElement(
            resource_id="btn1",
            class_name="android.widget.Button",
            text="OK",
            content_desc="",
            bounds=(100, 200, 300, 400),
            clickable=True,
            scrollable=False
        )
        
        result = explorer.click_element(element)
        
        assert result is True
        mock_device.click.assert_called_once_with(200, 300)  # Center point
        
        print("✓ UIExplorer click_element test passed")
    
    def test_scroll_screen_down(self):
        """Test scroll_screen down."""
        mock_device = Mock()
        mock_device.info = {"displayWidth": 1080, "displayHeight": 1920}
        explorer = UIExplorer(mock_device)
        
        result = explorer.scroll_screen("down")
        
        assert result is True
        mock_device.swipe.assert_called_once()
        
        print("✓ UIExplorer scroll_screen down test passed")
    
    def test_press_back(self):
        """Test press_back."""
        mock_device = Mock()
        explorer = UIExplorer(mock_device)
        
        result = explorer.press_back()
        
        assert result is True
        mock_device.press.assert_called_once_with("back")
        
        print("✓ UIExplorer press_back test passed")
    
    def test_press_home(self):
        """Test press_home."""
        mock_device = Mock()
        explorer = UIExplorer(mock_device)
        
        result = explorer.press_home()
        
        assert result is True
        mock_device.press.assert_called_once_with("home")
        
        print("✓ UIExplorer press_home test passed")
    
    def test_detect_error_dialog(self):
        """Test detect_error_dialog."""
        mock_device = Mock()
        explorer = UIExplorer(mock_device)
        
        # Mock XML with error dialog
        xml = '''
        <hierarchy>
            <node resource-id="message" class="android.widget.TextView" 
                  text="Unfortunately, App has stopped" content-desc="" 
                  clickable="false" scrollable="false" bounds="[100,200][980,300]" />
            <node resource-id="btn_ok" class="android.widget.Button" text="OK" 
                  content-desc="" clickable="true" scrollable="false" 
                  bounds="[400,400][680,500]" />
        </hierarchy>
        '''
        
        mock_device.dump_hierarchy.return_value = xml
        detected = explorer.detect_error_dialog()
        
        assert detected is True
        
        print("✓ UIExplorer detect_error_dialog test passed")
    
    def test_get_screen_signature(self):
        """Test get_screen_signature."""
        mock_device = Mock()
        explorer = UIExplorer(mock_device)
        
        # Mock XML with elements
        xml = '''
        <hierarchy>
            <node resource-id="btn1" class="android.widget.Button" text="OK" 
                  content-desc="" clickable="true" scrollable="false" 
                  bounds="[100,200][300,400]" />
            <node resource-id="btn2" class="android.widget.Button" text="Cancel" 
                  content-desc="" clickable="true" scrollable="false" 
                  bounds="[400,200][600,400]" />
        </hierarchy>
        '''
        
        mock_device.dump_hierarchy.return_value = xml
        sig1 = explorer.get_screen_signature()
        sig2 = explorer.get_screen_signature()
        
        # Should return same signature for same screen
        assert sig1 == sig2
        assert len(sig1) == 32  # MD5 hash length
        
        print("✓ UIExplorer get_screen_signature test passed")


def run_all_tests():
    """Run all Phase 3 unit tests."""
    print("\n" + "="*60)
    print("  Phase 3: UI Explorer Tests")
    print("="*60 + "\n")
    
    print("Testing UIElement...")
    test_ui_element = TestUIElement()
    test_ui_element.test_creation()
    test_ui_element.test_to_dict()
    test_ui_element.test_get_signature()
    print()
    
    print("Testing ExplorationResult...")
    test_exploration_result = TestExplorationResult()
    test_exploration_result.test_creation()
    test_exploration_result.test_creation_with_values()
    test_exploration_result.test_to_dict()
    print()
    
    print("Testing UIExplorer...")
    test_ui_explorer = TestUIExplorer()
    test_ui_explorer.test_initialization()
    test_ui_explorer.test_stop()
    test_ui_explorer.test_get_all_elements()
    test_ui_explorer.test_get_clickable_elements()
    test_ui_explorer.test_get_scrollable_elements()
    test_ui_explorer.test_get_input_fields()
    test_ui_explorer.test_click_element()
    test_ui_explorer.test_scroll_screen_down()
    test_ui_explorer.test_press_back()
    test_ui_explorer.test_press_home()
    test_ui_explorer.test_detect_error_dialog()
    test_ui_explorer.test_get_screen_signature()
    print()
    
    print("="*60)
    print("  All Phase 3 Tests Passed! ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()