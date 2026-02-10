"""
Config View for GUI

Displays and manages global settings.
"""

import customtkinter as ctk
from typing import Optional, List

from ..config_manager import ConfigManager, GlobalSettings
from .base_view import BaseView


class ConfigView(BaseView):
    """
    View for managing global settings.
    
    Allows editing of global configuration.
    
    Attributes:
        config_manager: ConfigManager instance
        main_window: Reference to main window
        settings: Current settings
    """
    
    def __init__(self, parent, config_manager: ConfigManager, main_window):
        """
        Initialize config view.

        Args:
            parent: Parent widget
            config_manager: ConfigManager instance
            main_window: Reference to main window
        """
        self.config_manager = config_manager
        # Call parent __init__ which triggers lifecycle hooks
        super().__init__(parent, main_window)

    def _setup_state(self):
        """Initialize config view state."""
        self.settings: Optional[GlobalSettings] = None
        self.entries = {}

    def _build_ui(self):
        """Build config view UI with fixed bottom buttons."""
        # Title
        self._build_title("Global Settings")

        # Scrollable settings frame (expands to fill space)
        self.settings_frame = self._build_scrollable_frame(height=None)

        # Buttons frame - FIXED AT BOTTOM
        buttons_frame = ctk.CTkFrame(self, height=80)
        buttons_frame.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
        buttons_frame.pack_propagate(False)  # Prevent frame from shrinking

        # Button container for horizontal layout
        button_container = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        button_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Save button
        save_btn = ctk.CTkButton(
            button_container,
            text="💾 Save",
            command=self._save_settings,
            width=130,
            height=35
        )
        save_btn.pack(side="left", padx=5, pady=5)

        # Reset button
        reset_btn = ctk.CTkButton(
            button_container,
            text="🔄 Reset",
            command=self._reset_settings,
            width=130,
            height=35,
            fg_color="#DC3545",
            hover_color="#BB2D3B"
        )
        reset_btn.pack(side="left", padx=5, pady=5)
    
    def _load_data(self):
        """Load and display settings."""
        try:
            self.settings = self.config_manager.load_settings()
        except Exception as e:
            self.update_status(f"Error loading settings: {e}")
            return

        # Clear current settings
        for widget in self.settings_frame.winfo_children():
            widget.destroy()
        self.entries.clear()

        # Display settings
        self._add_setting("Screenshot on Error", "bool", self.settings.screenshot_on_error)
        self._add_setting("Screenshot Interval (seconds, 0=disabled)", "int", self.settings.screenshot_interval)
        self._add_setting("Collect Logcat", "bool", self.settings.collect_logcat)
        self._add_setting("Logcat Filter (E,W,F,I,D,V)", "str", ",".join(self.settings.logcat_filter))
        self._add_setting("Max Test Retries", "int", self.settings.max_test_retries)
        self._add_setting("Delay Between Apps (seconds)", "int", self.settings.delay_between_apps)

        # Rebind mousewheel to include new widgets
        self.rebind_mousewheel(self.settings_frame)

        self.update_status("Settings loaded")
    
    def _add_setting(self, label: str, setting_type: str, value):
        """
        Add a setting to display.
        
        Args:
            label: Setting label
            setting_type: Type of setting (bool, int, str)
            value: Current value
        """
        setting_frame = ctk.CTkFrame(
            self.settings_frame,
            height=60
        )
        setting_frame.pack(fill="x", pady=5, padx=5)
        setting_frame.pack_propagate(False)
        
        # Label
        label_widget = ctk.CTkLabel(
            setting_frame,
            text=label,
            font=ctk.CTkFont(size=14),
            width=300,
            anchor="w"
        )
        label_widget.pack(side="left", padx=10, pady=20)
        
        # Entry widget
        if setting_type == "bool":
            # Don't pass text to CTkSwitch to avoid issues
            entry = ctk.CTkSwitch(setting_frame)
            if value:
                entry.select()
            entry.pack(side="right", padx=10, pady=15)
        else:
            entry = ctk.CTkEntry(
                setting_frame,
                width=200
            )
            entry.insert(0, str(value))
            entry.pack(side="right", padx=10, pady=15)
        
        self.entries[label] = (entry, setting_type)
    
    def _save_settings(self):
        """Save settings to file."""
        try:
            # Get values from entries with default values for None
            screenshot_on_error = self._get_setting_value("Screenshot on Error")
            if screenshot_on_error is None:
                screenshot_on_error = True
            
            screenshot_interval = self._get_setting_value("Screenshot Interval (seconds, 0=disabled)")
            if screenshot_interval is None:
                screenshot_interval = 30
            
            collect_logcat = self._get_setting_value("Collect Logcat")
            if collect_logcat is None:
                collect_logcat = True
            
            logcat_filter = self._get_setting_value("Logcat Filter (E,W,F,I,D,V)")
            if logcat_filter is None or logcat_filter == "":
                logcat_filter = ["E", "W", "F"]
            
            # Parse logcat filter
            if isinstance(logcat_filter, str):
                logcat_filter = [f.strip() for f in logcat_filter.split(",") if f.strip()]
                if not logcat_filter:
                    logcat_filter = ["E", "W", "F"]
            
            max_test_retries = self._get_setting_value("Max Test Retries")
            if max_test_retries is None:
                max_test_retries = 3
            
            delay_between_apps = self._get_setting_value("Delay Between Apps (seconds)")
            if delay_between_apps is None:
                delay_between_apps = 5
            
            # Ensure correct types
            if not isinstance(screenshot_on_error, bool):
                screenshot_on_error = bool(screenshot_on_error)
            if not isinstance(screenshot_interval, int):
                try:
                    screenshot_interval = int(screenshot_interval)
                except (ValueError, TypeError):
                    screenshot_interval = 30
            if not isinstance(collect_logcat, bool):
                collect_logcat = bool(collect_logcat)
            if not isinstance(max_test_retries, int):
                try:
                    max_test_retries = int(max_test_retries)
                except (ValueError, TypeError):
                    max_test_retries = 3
            if not isinstance(delay_between_apps, int):
                try:
                    delay_between_apps = int(delay_between_apps)
                except (ValueError, TypeError):
                    delay_between_apps = 5
            
            # Create settings object
            new_settings = GlobalSettings(
                screenshot_on_error=screenshot_on_error,
                screenshot_interval=screenshot_interval,
                collect_logcat=collect_logcat,
                logcat_filter=logcat_filter,
                max_test_retries=max_test_retries,
                delay_between_apps=delay_between_apps
            )
            
            # Validate and save
            if new_settings.validate():
                self.config_manager.save_settings(new_settings)
                self.settings = new_settings
                self.update_status("Settings saved successfully")
            else:
                self.update_status("Invalid settings")
        
        except Exception as e:
            import traceback


            self.update_status(f"Error saving settings: {e}")
    
    def _reset_settings(self):
        """Reset settings to defaults."""
        try:
            # Create default settings
            default_settings = GlobalSettings()
            self.config_manager.save_settings(default_settings)
            self._load_settings()
            self.update_status("Settings reset to defaults")
        except Exception as e:
            self.update_status(f"Error resetting settings: {e}")
    
    def _get_setting_value(self, label: str):
        """
        Get value from entry widget.
        
        Args:
            label: Setting label
        
        Returns:
            Setting value
        """
        try:
            entry, setting_type = self.entries.get(label, (None, None))
            
            if entry is None:
                logger.warning(f"Entry not found for label: {label}")
                return None
            
            if setting_type == "bool":
                # CTkSwitch.get() returns 1 (ON) or 0 (OFF) as int
                # Convert to Python bool explicitly
                return entry.get() == 1
            elif setting_type == "int":
                try:
                    value = entry.get()
                    if value == "":
                        return 0
                    return int(value)
                except ValueError as e:
                    logger.warning(f"Invalid int value for {label}: {entry.get()}, using default")
                    return 0
            else:
                # String type
                try:
                    value = entry.get()
                    if value is None:
                        return ""
                    return str(value).strip()
                except Exception as e:
                    logger.warning(f"Error getting string value for {label}: {e}")
                    return ""
        except Exception as e:
            logger.error(f"Error in _get_setting_value for {label}: {e}")
            return None
