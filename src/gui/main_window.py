"""
Main Window for Android App Auto Tester GUI

Provides to main application window with navigation.
"""

import customtkinter as ctk
from typing import Optional

from ..device_manager import DeviceManager, get_device_manager
from ..config_manager import get_config_manager
from .devices_view import DevicesView
from .apps_view import AppsView
from .config_view import ConfigView
from .test_view import TestView
from .report_view import ReportView

from ..utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(ctk.CTk):
    """
    Main application window.
    
    Provides navigation between different views:
    - Devices: View and select connected devices
    - Apps: Manage app configurations
    - Config: Global settings
    - Test: Run and monitor tests
    - Report: View test reports
    """
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        # Configure window
        self.title("Android App Auto Tester")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize components
        self.device_manager: Optional[DeviceManager] = get_device_manager()
        self.config_manager = get_config_manager()
        
        # Current view
        self.current_view: Optional[ctk.CTkFrame] = None
        
        # Build UI
        self._build_ui()
        
        # Load initial view
        self._show_devices_view()
    
    def _build_ui(self):
        """Build main UI layout using pack system."""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create header (fixed height at top)
        self._build_header()
        
        # Create navigation FIRST (fixed height at bottom - always visible)
        self._build_navigation()
        
        # Create content area LAST (expands to fill remaining space)
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, pady=(10, 0))
    
    def _build_header(self):
        """Build header section using pack layout."""
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="📱 Android App Auto Tester",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=15)
        
        # Status container
        status_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_container.pack(side="right", padx=20, pady=10)
        
        # Device status
        self.device_status_label = ctk.CTkLabel(
            status_container,
            text="Device: Not Connected",
            font=ctk.CTkFont(size=11),
            text_color="#888888"
        )
        self.device_status_label.pack(anchor="e", padx=10, pady=(5, 0))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            status_container,
            text="Ready",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_label.pack(anchor="e", padx=10, pady=(0, 5))
    
    def _build_navigation(self):
        """Build navigation bar with fixed height using pack layout."""
        nav_frame = ctk.CTkFrame(self.main_frame, height=60)
        nav_frame.pack(fill="x", side="bottom")
        nav_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Button container for horizontal layout - smaller padding
        button_container = ctk.CTkFrame(nav_frame, fg_color="transparent")
        button_container.pack(fill="both", expand=True, padx=10, pady=2)
        
        # Navigation buttons
        self.devices_btn = ctk.CTkButton(
            button_container,
            text="Devices",
            command=self._show_devices_view,
            width=100,
            height=32
        )
        self.devices_btn.pack(side="left", padx=5, pady=2)
        
        self.apps_btn = ctk.CTkButton(
            button_container,
            text="Apps",
            command=self._show_apps_view,
            width=100,
            height=32
        )
        self.apps_btn.pack(side="left", padx=5, pady=2)
        
        self.config_btn = ctk.CTkButton(
            button_container,
            text="Config",
            command=self._show_config_view,
            width=100,
            height=32
        )
        self.config_btn.pack(side="left", padx=5, pady=2)
        
        self.test_btn = ctk.CTkButton(
            button_container,
            text="Test",
            command=self._show_test_view,
            width=100,
            height=32,
            fg_color="#2CC985",  # Green
            hover_color="#1FA868"
        )
        self.test_btn.pack(side="left", padx=5, pady=2)
        
        self.report_btn = ctk.CTkButton(
            button_container,
            text="Report",
            command=self._show_report_view,
            width=100,
            height=32
        )
        self.report_btn.pack(side="left", padx=5, pady=2)
    
    def _clear_content(self):
        """Clear the content frame."""
        try:
            for widget in self.content_frame.winfo_children():
                widget.destroy()
        except Exception as e:
            logger.error(f"Failed to clear content: {e}")
    
    def _show_devices_view(self):
        """Show devices view."""
        try:
            self._clear_content()
            self.current_view = DevicesView(
                self.content_frame,
                self.device_manager,
                self
            )
            self.current_view.pack(fill="both", expand=True)
            self._update_status("View: Devices")
        except Exception as e:
            self._handle_view_error("Devices", e)
    
    def _show_apps_view(self):
        """Show apps view."""
        try:
            self._clear_content()
            self.current_view = AppsView(
                self.content_frame,
                self.config_manager,
                self
            )
            self.current_view.pack(fill="both", expand=True)
            self._update_status("View: Apps")
        except Exception as e:
            self._handle_view_error("Apps", e)
    
    def _show_config_view(self):
        """Show config view."""
        try:
            self._clear_content()
            self.current_view = ConfigView(
                self.content_frame,
                self.config_manager,
                self
            )
            self.current_view.pack(fill="both", expand=True)
            self._update_status("View: Config")
        except Exception as e:
            self._handle_view_error("Config", e)
    
    def _show_test_view(self):
        """Show test view."""
        try:
            self._clear_content()
            self.current_view = TestView(
                self.content_frame,
                self.device_manager,
                self.config_manager,
                self
            )
            self.current_view.pack(fill="both", expand=True)
            self._update_status("View: Test")
        except Exception as e:
            self._handle_view_error("Test", e)
    
    def _show_report_view(self):
        """Show report view."""
        try:
            self._clear_content()
            self.current_view = ReportView(
                self.content_frame,
                self
            )
            self.current_view.pack(fill="both", expand=True)
            self._update_status("View: Report")
        except Exception as e:
            self._handle_view_error("Report", e)
    
    def _handle_view_error(self, view_name: str, error: Exception):
        """
        Handle view loading error.
        
        Args:
            view_name: Name of the view that failed
            error: Exception that occurred
        """
        logger.error(f"Failed to load {view_name} view: {error}")
        import traceback
        self._update_status(f"Error loading {view_name} view")
        
        # Show error label
        error_label = ctk.CTkLabel(
            self.content_frame,
            text=f"Failed to load {view_name} View:\n{error}",
            text_color="#DC3545",
            font=ctk.CTkFont(size=14)
        )
        error_label.pack(fill="both", expand=True, padx=20, pady=20)
    
    def _update_status(self, message: str):
        """
        Update to status label.
        
        Args:
            message: Status message
        """
        try:
            self.status_label.configure(text=message)
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
    
    def _update_device_status(self, device_info=None):
        """
        Update to device status label.
        
        Args:
            device_info: DeviceInfo or None
        """
        try:
            if device_info:
                self.device_status_label.configure(
                    text=f"Device: {device_info.model} ({device_info.serial})",
                    text_color="#2CC985"
                )
            else:
                self.device_status_label.configure(
                    text="Device: Not Connected",
                    text_color="#888888"
                )
        except Exception as e:
            logger.error(f"Failed to update device status: {e}")
    
    def set_device_manager(self, device_manager: DeviceManager):
        """
        Set device manager.
        
        Args:
            device_manager: DeviceManager instance
        """
        self.device_manager = device_manager
        if device_manager:
            device_info = device_manager.get_device_info()
            self._update_device_status(device_info)


def run_gui():
    """Run GUI application."""
    try:
        app = MainWindow()
        app.mainloop()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error in GUI: {e}", exc_info=True)