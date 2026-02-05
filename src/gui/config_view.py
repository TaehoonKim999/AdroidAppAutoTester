"""
Config View for GUI

Displays and manages global settings.
"""

import customtkinter as ctk
from typing import Optional, List

from ..config_manager import ConfigManager, GlobalSettings


class ConfigView(ctk.CTkFrame):
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
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.main_window = main_window
        self.settings: Optional[GlobalSettings] = None
        
        # Entry widgets
        self.entries = {}
        
        # Build UI
        self._build_ui()
        
        # Load settings
        self._load_settings()
    
    def _build_ui(self):
        """Build config view UI."""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Global Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Settings frame
        self.settings_frame = ctk.CTkScrollableFrame(
            self,
            height=450
        )
        self.settings_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(fill="x", padx=10, pady=(10, 20))
        
        # Save button
        save_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Save",
            command=self._save_settings,
            width=120
        )
        save_btn.pack(side="left", padx=5, pady=10)
        
        # Reset button
        reset_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Reset",
            command=self._reset_settings,
            width=120,
            fg_color="#DC3545",
            hover_color="#BB2D3B"
        )
        reset_btn.pack(side="left", padx=5, pady=10)
    
    def _load_settings(self):
        """Load and display settings."""
        try:
            self.settings = self.config_manager.load_settings()
        except Exception as e:
            self.main_window._update_status(f"Error loading settings: {e}")
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
        
        self.main_window._update_status("Settings loaded")
    
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
            entry = ctk.CTkSwitch(
                setting_frame,
                text=value
            )
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
            # Get values from entries
            screenshot_on_error = self._get_setting_value("Screenshot on Error")
            screenshot_interval = self._get_setting_value("Screenshot Interval (seconds, 0=disabled)")
            collect_logcat = self._get_setting_value("Collect Logcat")
            logcat_filter = self._get_setting_value("Logcat Filter (E,W,F,I,D,V)")
            max_test_retries = self._get_setting_value("Max Test Retries")
            delay_between_apps = self._get_setting_value("Delay Between Apps (seconds)")
            
            # Parse logcat filter
            if isinstance(logcat_filter, str):
                logcat_filter = [f.strip() for f in logcat_filter.split(",")]
            else:
                logcat_filter = ["E", "W", "F"]
            
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
                self.main_window._update_status("Settings saved successfully")
            else:
                self.main_window._update_status("Invalid settings")
        
        except Exception as e:
            self.main_window._update_status(f"Error saving settings: {e}")
    
    def _reset_settings(self):
        """Reset settings to defaults."""
        try:
            # Create default settings
            default_settings = GlobalSettings()
            self.config_manager.save_settings(default_settings)
            self._load_settings()
            self.main_window._update_status("Settings reset to defaults")
        except Exception as e:
            self.main_window._update_status(f"Error resetting settings: {e}")
    
    def _get_setting_value(self, label: str):
        """
        Get value from entry widget.
        
        Args:
            label: Setting label
        
        Returns:
            Setting value
        """
        entry, setting_type = self.entries.get(label, (None, None))
        
        if entry is None:
            return None
        
        if setting_type == "bool":
            # CTkSwitch.get() returns 1 (ON) or 0 (OFF) as int
            # Convert to Python bool explicitly
            return entry.get() == 1
        elif setting_type == "int":
            try:
                return int(entry.get())
            except ValueError:
                return 0
        else:
            return entry.get()