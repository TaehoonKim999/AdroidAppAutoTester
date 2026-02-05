"""
UI Explorer Module

Handles automatic UI exploration and interaction.
Navigates app screens, clicks elements, scrolls, and detects errors.
"""

import hashlib
import re
import time
import random
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple, Any

try:
    import uiautomator2 as u2
except ImportError:
    u2 = None


@dataclass
class UIElement:
    """
    Information about a UI element.
    
    Attributes:
        resource_id: Resource ID of element
        class_name: Class name (e.g., "android.widget.Button")
        text: Text content
        content_desc: Content description
        bounds: Element bounds (left, top, right, bottom)
        clickable: Whether element is clickable
        scrollable: Whether element is scrollable
        checkable: Whether element is checkable
    """
    resource_id: str
    class_name: str
    text: str
    content_desc: str
    bounds: Tuple[int, int, int, int]
    clickable: bool
    scrollable: bool
    checkable: bool = False
    
    def to_dict(self) -> dict:
        """Convert UIElement to dictionary."""
        return {
            "resource_id": self.resource_id,
            "class_name": self.class_name,
            "text": self.text,
            "content_desc": self.content_desc,
            "bounds": self.bounds,
            "clickable": self.clickable,
            "scrollable": self.scrollable,
            "checkable": self.checkable
        }
    
    def get_signature(self) -> str:
        """
        Get a unique signature for this element.
        
        Returns:
            str: Unique signature string
        """
        signature = f"{self.class_name}|{self.text}|{self.resource_id}"
        return hashlib.md5(signature.encode()).hexdigest()


@dataclass
class ExplorationResult:
    """
    Result of UI exploration.
    
    Attributes:
        screens_visited: Number of unique screens visited
        elements_interacted: Number of elements interacted with
        actions_performed: List of actions performed
        errors_found: List of errors detected
        duration: Exploration duration in seconds
    """
    screens_visited: int = 0
    elements_interacted: int = 0
    actions_performed: List[str] = field(default_factory=list)
    errors_found: List[str] = field(default_factory=list)
    duration: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert ExplorationResult to dictionary."""
        return {
            "screens_visited": self.screens_visited,
            "elements_interacted": self.elements_interacted,
            "actions_performed": self.actions_performed,
            "errors_found": self.errors_found,
            "duration": self.duration
        }


class UIExplorer:
    """
    Automatic UI explorer for Android apps.
    
    Navigates through app screens, clicks elements, scrolls,
    and performs various actions to test. application.
    
    Attributes:
        device: uiautomator2 device instance
        visited_screens: Set of screen signatures (to avoid revisiting)
        result: Current exploration result
        start_time: Exploration start time
    """
    
    ERROR_DIALOG_KEYWORDS = [
        "has stopped",
        "has stopped working",
        "unfortunately",
        "force close",
        "stopped unexpectedly",
        "application not responding"
    ]
    
    DEFAULT_TIMEOUT = 10  # seconds
    SCREEN_WAIT_TIME = 1  # seconds
    ACTION_WAIT_TIME = 0.5  # seconds
    
    def __init__(self, device: Any):
        """
        Initialize UIExplorer.
        
        Args:
            device: uiautomator2 device instance
        """
        if u2 is None:
            raise ImportError(
                "uiautomator2 is not installed. "
                "Please install it with: pip install uiautomator2"
            )
        
        self.device = device
        self.visited_screens: Set[str] = set()
        self.result = ExplorationResult()
        self.start_time = 0.0
        self._stop_requested = False
    
    def explore(
        self,
        duration: int,
        actions: List[str] = None
    ) -> ExplorationResult:
        """
        Explore UI for specified duration.
        
        Args:
            duration: Exploration duration in seconds
            actions: List of actions to perform (scroll, click_buttons, 
                      input_text, back_navigation)
        
        Returns:
            ExplorationResult: Exploration results
        """
        if actions is None:
            actions = ["scroll", "click_buttons"]
        
        print(f"[INFO] Starting UI exploration for {duration} seconds")
        print(f"[INFO] Actions: {', '.join(actions)}")
        
        self.start_time = time.time()
        self.result = ExplorationResult()
        self.visited_screens.clear()
        self._stop_requested = False
        
        loop_count = 0
        last_progress_time = 0
        
        try:
            # Main exploration loop
            while True:
                try:
                    # Calculate elapsed time
                    elapsed = time.time() - self.start_time
                    remaining_time = duration - elapsed
                    
                    # Check if time expired
                    if elapsed >= duration:
                        print(f"[INFO] Time expired: {elapsed:.1f}s >= {duration}s")
                        break
                    
                    if remaining_time <= 0:
                        print(f"[INFO] No remaining time")
                        break
                    
                    # Check for stop request
                    if self._stop_requested:
                        print("[INFO] Exploration stopped by request")
                        break
                    
                    loop_count += 1
                    
                    # Log progress every 10 seconds
                    if int(elapsed) - last_progress_time >= 10:
                        print(f"[INFO] Exploration progress: {int(elapsed)}/{duration}s (loop {loop_count})")
                        last_progress_time = int(elapsed)
                    
                    # Check for error dialogs
                    try:
                        if self.detect_error_dialog():
                            print("[WARNING] Error dialog detected")
                            self._handle_error_dialog()
                    except Exception as e:
                        print(f"[WARNING] Error checking for error dialog: {e}")
                    
                    # Get current screen signature
                    try:
                        screen_sig = self.get_screen_signature()
                        if screen_sig not in self.visited_screens:
                            self.visited_screens.add(screen_sig)
                            self.result.screens_visited += 1
                            print(f"[INFO] New screen visited (total: {self.result.screens_visited})")
                    except Exception as e:
                        print(f"[WARNING] Error getting screen signature: {e}")
                    
                    # Perform random action
                    try:
                        action = self._choose_random_action(actions)
                        if action:
                            self._perform_action(action, remaining_time)
                        else:
                            # No action possible - try pressing back
                            if self.result.screens_visited > 0:
                                print("[INFO] No action possible, pressing back")
                                try:
                                    self.press_back()
                                except Exception as e:
                                    print(f"[WARNING] Failed to press back: {e}")
                    except Exception as e:
                        print(f"[WARNING] Error performing action: {e}")
                        self.result.errors_found.append(f"Action error: {e}")
                    
                    # Wait between actions
                    time.sleep(self.ACTION_WAIT_TIME)
                
                except Exception as loop_error:
                    print(f"[WARNING] Error in exploration loop: {loop_error}")
                    self.result.errors_found.append(f"Loop error: {loop_error}")
                    # Continue loop despite error
                    time.sleep(0.5)
        
        except Exception as e:
            print(f"[ERROR] Exploration failed: {e}")
            import traceback
            traceback.print_exc()
            self.result.errors_found.append(f"Exploration error: {e}")
        
        # Calculate duration
        self.result.duration = time.time() - self.start_time
        
        print(f"[INFO] Exploration completed")
        print(f"[INFO] Screens visited: {self.result.screens_visited}")
        print(f"[INFO] Elements interacted: {self.result.elements_interacted}")
        print(f"[INFO] Actions performed: {len(self.result.actions_performed)}")
        print(f"[INFO] Total duration: {self.result.duration:.1f}s")
        print(f"[INFO] Loop iterations: {loop_count}")
        
        return self.result
    
    def stop(self) -> None:
        """Request to stop exploration."""
        self._stop_requested = True
    
    def get_all_elements(self) -> List[UIElement]:
        """
        Get all UI elements on current screen.
        
        Returns:
            List of UIElement objects
        """
        try:
            xml = self.device.dump_hierarchy()
            return self._parse_xml_elements(xml)
        except Exception as e:
            print(f"[WARNING] Error getting elements: {e}")
            return []
    
    def get_clickable_elements(self) -> List[UIElement]:
        """
        Get clickable elements on current screen.
        
        Returns:
            List of clickable UIElement objects
        """
        all_elements = self.get_all_elements()
        return [el for el in all_elements if el.clickable]
    
    def get_scrollable_elements(self) -> List[UIElement]:
        """
        Get scrollable elements on current screen.
        
        Returns:
            List of scrollable UIElement objects
        """
        all_elements = self.get_all_elements()
        return [el for el in all_elements if el.scrollable]
    
    def get_input_fields(self) -> List[UIElement]:
        """
        Get text input fields on current screen.
        
        Returns:
            List of input field UIElement objects
        """
        all_elements = self.get_all_elements()
        input_classes = [
            "android.widget.EditText",
            "android.widget.AutoCompleteTextView"
        ]
        return [
            el for el in all_elements 
            if any(cls in el.class_name for cls in input_classes)
        ]
    
    def click_element(self, element: UIElement) -> bool:
        """
        Click on a UI element.
        
        Args:
            element: UIElement to click
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            bounds = element.bounds
            x = (bounds[0] + bounds[2]) // 2
            y = (bounds[1] + bounds[3]) // 2
            
            print(f"[INFO] Clicking element: {element.text or element.resource_id}")
            self.device.click(x, y)
            
            self.result.elements_interacted += 1
            self.result.actions_performed.append(
                f"Click: {element.text or element.resource_id}"
            )
            
            time.sleep(self.SCREEN_WAIT_TIME)
            return True
            
        except Exception as e:
            print(f"[WARNING] Failed to click element: {e}")
            self.result.errors_found.append(f"Click failed: {e}")
            return False
    
    def scroll_screen(self, direction: str = "down") -> bool:
        """
        Scroll screen.
        
        Args:
            direction: Scroll direction ("up", "down", "left", "right")
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            width = self.device.info["displayWidth"]
            height = self.device.info["displayHeight"]
            
            # Calculate scroll coordinates
            center_x = width // 2
            center_y = height // 2
            
            if direction == "down":
                start_y = int(height * 0.2)
                end_y = int(height * 0.8)
                self.device.swipe(center_x, start_y, center_x, end_y, 0.5)
            elif direction == "up":
                start_y = int(height * 0.8)
                end_y = int(height * 0.2)
                self.device.swipe(center_x, start_y, center_x, end_y, 0.5)
            elif direction == "right":
                start_x = int(width * 0.2)
                end_x = int(width * 0.8)
                self.device.swipe(start_x, center_y, end_x, center_y, 0.5)
            elif direction == "left":
                start_x = int(width * 0.8)
                end_x = int(width * 0.2)
                self.device.swipe(start_x, center_y, end_x, center_y, 0.5)
            else:
                print(f"[WARNING] Unknown scroll direction: {direction}")
                return False
            
            print(f"[INFO] Scrolled {direction}")
            self.result.actions_performed.append(f"Scroll: {direction}")
            
            time.sleep(self.SCREEN_WAIT_TIME)
            return True
            
        except Exception as e:
            print(f"[WARNING] Failed to scroll: {e}")
            self.result.errors_found.append(f"Scroll failed: {e}")
            return False
    
    def input_text(self, element: UIElement, text: str) -> bool:
        """
        Input text into an element.
        
        Args:
            element: UIElement to input text into
            text: Text to input
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Click element first to focus
            if not self.click_element(element):
                return False
            
            # Clear existing text
            self.device.send_keys("", clear=True)
            
            # Input new text
            print(f"[INFO] Inputting text: {text}")
            self.device.send_keys(text)
            
            self.result.elements_interacted += 1
            self.result.actions_performed.append(
                f"Input: {text} into {element.resource_id}"
            )
            
            time.sleep(self.SCREEN_WAIT_TIME)
            return True
            
        except Exception as e:
            print(f"[WARNING] Failed to input text: {e}")
            self.result.errors_found.append(f"Input failed: {e}")
            return False
    
    def press_back(self) -> bool:
        """
        Press back button.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("[INFO] Pressing back")
            self.device.press("back")
            
            self.result.actions_performed.append("Press: Back")
            
            time.sleep(self.SCREEN_WAIT_TIME)
            return True
            
        except Exception as e:
            print(f"[WARNING] Failed to press back: {e}")
            self.result.errors_found.append(f"Back press failed: {e}")
            return False
    
    def press_home(self) -> bool:
        """
        Press home button.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("[INFO] Pressing home")
            self.device.press("home")
            
            self.result.actions_performed.append("Press: Home")
            
            time.sleep(self.SCREEN_WAIT_TIME)
            return True
            
        except Exception as e:
            print(f"[WARNING] Failed to press home: {e}")
            self.result.errors_found.append(f"Home press failed: {e}")
            return False
    
    def detect_error_dialog(self) -> bool:
        """
        Detect if an error dialog is shown.
        
        Returns:
            bool: True if error dialog detected
        """
        try:
            all_elements = self.get_all_elements()
            
            for element in all_elements:
                text_lower = element.text.lower() if element.text else ""
                content_desc_lower = element.content_desc.lower() if element.content_desc else ""
                
                for keyword in self.ERROR_DIALOG_KEYWORDS:
                    if keyword in text_lower or keyword in content_desc_lower:
                        return True
            
            return False
            
        except Exception as e:
            print(f"[WARNING] Error detecting error dialog: {e}")
            return False
    
    def _handle_error_dialog(self) -> None:
        """Handle error dialog by trying to close it."""
        try:
            # Try to find "OK" button
            elements = self.get_all_elements()
            
            for element in elements:
                if element.clickable:
                    text = element.text.lower() if element.text else ""
                    if text in ["ok", "close", "dismiss"]:
                        self.click_element(element)
                        self.result.errors_found.append("Error dialog closed")
                        return
            
            # If no button found, press back
            self.press_back()
            self.result.errors_found.append("Error dialog handled with back")
            
        except Exception as e:
            print(f"[WARNING] Error handling error dialog: {e}")
    
    def get_screen_signature(self) -> str:
        """
        Get a unique signature for current screen.
        
        Creates a hash based on structure and elements of screen.
        
        Returns:
            str: Screen signature
        """
        try:
            elements = self.get_all_elements()
            
            # Sort elements by position
            sorted_elements = sorted(elements, key=lambda e: e.bounds)
            
            # Create signature from element types and positions
            sig_parts = []
            for el in sorted_elements[:10]:  # Use first 10 elements
                sig_parts.append(f"{el.class_name}:{el.bounds}")
            
            signature = "|".join(sig_parts)
            return hashlib.md5(signature.encode()).hexdigest()
            
        except Exception as e:
            print(f"[WARNING] Error getting screen signature: {e}")
            return "unknown"
    
    def _choose_random_action(self, available_actions: List[str]) -> Optional[str]:
        """
        Choose a random action based on available actions.
        
        Args:
            available_actions: List of actions to choose from
        
        Returns:
            Action name or None if no action available
        """
        if not available_actions:
            return None
        
        # Weight actions based on available elements
        weighted_actions = []
        
        if "scroll" in available_actions:
            if self.get_scrollable_elements():
                weighted_actions.extend(["scroll"] * 3)
        
        if "click_buttons" in available_actions:
            clickable = self.get_clickable_elements()
            if clickable:
                weighted_actions.extend(["click"] * 5)
        
        if "input_text" in available_actions:
            inputs = self.get_input_fields()
            if inputs:
                weighted_actions.extend(["input"] * 2)
        
        if "back_navigation" in available_actions:
            # Less likely to go back
            weighted_actions.extend(["back"] * 1)
        
        if not weighted_actions:
            return None
        
        return random.choice(weighted_actions)
    
    def _perform_action(self, action: str, remaining_time: float) -> bool:
        """
        Perform a specific action.
        
        Args:
            action: Action name
            remaining_time: Remaining exploration time
        
        Returns:
            bool: True if action performed, False otherwise
        """
        if action == "scroll":
            direction = random.choice(["down", "up"])
            return self.scroll_screen(direction)
        
        elif action == "click":
            elements = self.get_clickable_elements()
            if elements:
                # Prefer unvisited elements
                element = random.choice(elements)
                return self.click_element(element)
            return False
        
        elif action == "input":
            elements = self.get_input_fields()
            if elements:
                element = random.choice(elements)
                test_texts = ["test", "123", "hello world", "sample"]
                text = random.choice(test_texts)
                return self.input_text(element, text)
            return False
        
        elif action == "back":
            # Only go back if we've visited multiple screens
            if self.result.screens_visited > 1:
                return self.press_back()
            return False
        
        return False
    
    def _parse_xml_elements(self, xml: str) -> List[UIElement]:
        """
        Parse UI elements from XML hierarchy.
        
        Args:
            xml: XML hierarchy string
        
        Returns:
            List of UIElement objects
        """
        elements = []
        
        # Simple XML parsing (regex-based)
        # Note: For production, use proper XML parser like xml.etree.ElementTree
        node_pattern = re.compile(r'<node[^>]*>')
        
        for match in node_pattern.finditer(xml):
            node_str = match.group(0)
            
            # Extract attributes
            resource_id = self._get_xml_attr(node_str, "resource-id")
            class_name = self._get_xml_attr(node_str, "class")
            text = self._get_xml_attr(node_str, "text")
            content_desc = self._get_xml_attr(node_str, "content-desc")
            clickable = self._get_xml_attr(node_str, "clickable") == "true"
            scrollable = self._get_xml_attr(node_str, "scrollable") == "true"
            checkable = self._get_xml_attr(node_str, "checkable") == "true"
            
            # Extract bounds
            bounds_str = self._get_xml_attr(node_str, "bounds")
            bounds = (0, 0, 0, 0)
            if bounds_str:
                try:
                    # Format: "[0,0][1080,100]"
                    coords = re.findall(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
                    if coords:
                        x1, y1, x2, y2 = coords[0]
                        bounds = (int(x1), int(y1), int(x2), int(y2))
                except (ValueError, IndexError):
                    pass
            
            # Skip elements without bounds
            if bounds == (0, 0, 0, 0):
                continue
            
            elements.append(UIElement(
                resource_id=resource_id or "",
                class_name=class_name or "",
                text=text or "",
                content_desc=content_desc or "",
                bounds=bounds,
                clickable=clickable,
                scrollable=scrollable,
                checkable=checkable
            ))
        
        return elements
    
    def _get_xml_attr(self, node_str: str, attr_name: str) -> Optional[str]:
        """
        Extract attribute value from XML node string.
        
        Args:
            node_str: XML node string
            attr_name: Attribute name to extract
        
        Returns:
            Attribute value or None
        """
        pattern = re.compile(f'{attr_name}="([^"]*)"')
        match = pattern.search(node_str)
        return match.group(1) if match else None