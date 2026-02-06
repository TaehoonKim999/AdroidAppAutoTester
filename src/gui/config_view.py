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

    def _bind_mousewheel(self, widget):
        """
        Bind mouse wheel scrolling to a scrollable widget.

        Args:
            widget: CTkScrollableFrame to bind mouse wheel events
        """
        # CTkScrollableFrame has _parent_canvas attribute for internal canvas
        def on_mousewheel(event):
            try:
                # Windows and MacOS
                if event.delta:
                    widget._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass

        def on_mousewheel_linux_up(event):
            try:
                widget._parent_canvas.yview_scroll(-1, "units")
            except Exception:
                pass

        def on_mousewheel_linux_down(event):
            try:
                widget._parent_canvas.yview_scroll(1, "units")
            except Exception:
                pass

        def bind_to_widget(w):
            """Recursively bind mouse wheel to widget and all its children."""
            try:
                w.bind("<MouseWheel>", on_mousewheel, add="+")
                w.bind("<Button-4>", on_mousewheel_linux_up, add="+")
                w.bind("<Button-5>", on_mousewheel_linux_down, add="+")
            except Exception:
                pass

            # Bind to all children recursively
            try:
                for child in w.winfo_children():
                    bind_to_widget(child)
            except Exception:
                pass

        # Bind to the scrollable frame and all its children
        bind_to_widget(widget)

        # Also bind to the internal canvas
        try:
            widget._parent_canvas.bind("<MouseWheel>", on_mousewheel, add="+")
            widget._parent_canvas.bind("<Button-4>", on_mousewheel_linux_up, add="+")
            widget._parent_canvas.bind("<Button-5>", on_mousewheel_linux_down, add="+")
        except Exception:
            pass

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

        # Enable mouse wheel scrolling
        self._bind_mousewheel(self.settings_frame)
        
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

        # Rebind mousewheel to include new widgets
        self._bind_mousewheel(self.settings_frame)

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
                self.main_window._update_status("Settings saved successfully")
            else:
                self.main_window._update_status("Invalid settings")
        
        except Exception as e:
            import traceback
            traceback.print_exc()
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
        try:
            entry, setting_type = self.entries.get(label, (None, None))
            
            if entry is None:
                print(f"[WARNING] Entry not found for label: {label}")
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
                    print(f"[WARNING] Invalid int value for {label}: {entry.get()}, using default")
                    return 0
            else:
                # String type
                try:
                    value = entry.get()
                    if value is None:
                        return ""
                    return str(value).strip()
                except Exception as e:
                    print(f"[WARNING] Error getting string value for {label}: {e}")
                    return ""
        except Exception as e:
            print(f"[ERROR] Error in _get_setting_value for {label}: {e}")
            return None
