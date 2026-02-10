"""
Test View for GUI

Runs and monitors automated tests.
"""

import customtkinter as ctk
from typing import Optional, List
import threading

from ..device_manager import DeviceManager, get_device_manager
from ..config_manager import ConfigManager, AppConfig, get_global_settings
from ..report_generator import get_report_generator
from .base_view import BaseView

from ..utils.logger import get_logger

logger = get_logger(__name__)


class TestView(BaseView):
    """
    View for running and monitoring tests.
    
    Allows selection of apps and running tests with real-time progress.
    
    Attributes:
        device_manager: DeviceManager instance
        config_manager: ConfigManager instance
        main_window: Reference to main window
        apps: List of configured apps
        running: Test running status
    """
    
    def __init__(self, parent, device_manager: Optional[DeviceManager], config_manager: ConfigManager, main_window):
        """
        Initialize test view.

        Args:
            parent: Parent widget
            device_manager: DeviceManager instance
            config_manager: ConfigManager instance
            main_window: Reference to main window
        """
        try:
            self.device_manager = device_manager
            self.config_manager = config_manager
            # Call parent __init__ which triggers lifecycle hooks
            super().__init__(parent, main_window)
        except Exception as e:
            logger.error(f"Failed to initialize test view: {e}")
            import traceback
            raise

    def _setup_state(self):
        """Initialize test view state."""
        self.apps: List[AppConfig] = []
        self.running = False

    def _build_ui(self):
        """Build test view UI using pack layout with fixed bottom buttons."""
        try:
            # Title
            self._build_title("Run Tests")

            # Device status
            self.device_status_label = ctk.CTkLabel(
                self,
                text="Device: Not connected",
                font=ctk.CTkFont(size=14)
            )
            self.device_status_label.pack(fill="x", pady=(0, 10), padx=10)
        except Exception as e:
            logger.error(f"Failed to build title: {e}")
        
        try:
            # Scrollable content frame (expands to fill space)
            self.content_scrollable = ctk.CTkScrollableFrame(
                self,
                label_text=""
            )
            self.content_scrollable.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        except Exception as e:
            logger.error(f"Failed to create scrollable frame: {e}")
            self.content_scrollable = None
            return
        
        try:
            # Apps selection frame (inside scrollable)
            apps_frame = ctk.CTkFrame(self.content_scrollable)
            apps_frame.pack(fill="x", pady=(0, 10))
            
            apps_label = ctk.CTkLabel(
                apps_frame,
                text="Select Apps to Test:",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            apps_label.pack(side="left", padx=10, pady=10)
            
            self.select_all_var = ctk.BooleanVar(value=True)
            select_all_cb = ctk.CTkCheckBox(
                apps_frame,
                text="Select All",
                variable=self.select_all_var,
                command=self._toggle_select_all
            )
            select_all_cb.pack(side="left", padx=10, pady=10)
        except Exception as e:
            logger.error(f"Failed to build apps selection frame: {e}")
        
        try:
            # Apps list (inside scrollable) - create directly instead of using helper
            self.apps_frame = ctk.CTkScrollableFrame(
                self.content_scrollable,
                height=200,
                label_text=""
            )
            self.apps_frame.pack(fill="x", pady=(0, 10))
            self._bind_mousewheel(self.apps_frame)
        except Exception as e:
            logger.error(f"Failed to build apps frame: {e}")
            self.apps_frame = None
        
        try:
            # Progress frame (inside scrollable)
            progress_frame = ctk.CTkFrame(self.content_scrollable)
            progress_frame.pack(fill="x", pady=(0, 10))
            
            self.progress_label = ctk.CTkLabel(
                progress_frame,
                text="Ready to run tests",
                font=ctk.CTkFont(size=14)
            )
            self.progress_label.pack(pady=(10, 5))
            
            self.progress_bar = ctk.CTkProgressBar(
                progress_frame,
                width=400
            )
            self.progress_bar.pack(pady=10)
            self.progress_bar.set(0)
            
            # Log output
            log_label = ctk.CTkLabel(
                progress_frame,
                text="Log Output:",
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            log_label.pack(fill="x", padx=10, pady=(10, 5))
            
            self.log_text = ctk.CTkTextbox(
                progress_frame,
                height=150,
                font=ctk.CTkFont(family="Consolas", size=10)
            )
            self.log_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            self._log("Ready to run tests")
        except Exception as e:
            logger.error(f"Failed to build progress frame: {e}")
        
        try:
            # Buttons frame - FIXED AT BOTTOM (packed after scrollable)
            buttons_frame = ctk.CTkFrame(self, height=80)
            buttons_frame.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
            buttons_frame.pack_propagate(False)  # Prevent frame from shrinking
            
            # Button container for horizontal layout
            button_container = ctk.CTkFrame(buttons_frame, fg_color="transparent")
            button_container.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Run button
            self.run_btn = ctk.CTkButton(
                button_container,
                text="▶️ Run Tests",
                command=self._run_tests,
                width=130,
                height=35,
                fg_color="#28A745",
                hover_color="#218838"
            )
            self.run_btn.pack(side="left", padx=5, pady=5)
            
            # Stop button
            self.stop_btn = ctk.CTkButton(
                button_container,
                text="⏹ Stop",
                command=self._stop_tests,
                width=130,
                height=35,
                fg_color="#DC3545",
                hover_color="#BB2D3B"
            )
            self.stop_btn.pack(side="left", padx=5, pady=5)
            self.stop_btn.configure(state="disabled")
            
            # Clear log button
            clear_btn = ctk.CTkButton(
                button_container,
                text="🗑 Clear Log",
                command=self._clear_log,
                width=130,
                height=35
            )
            clear_btn.pack(side="left", padx=5, pady=5)
        except Exception as e:
            logger.error(f"Failed to build buttons frame: {e}")
    
    def _log(self, message: str):
        """
        Add a log message.
        
        Args:
            message: Log message
        """
        try:
            self.log_text.insert("end", f"{message}\n")
            self.log_text.see("end")
        except Exception as e:
            logger.error(f"Failed to log message: {e}")
    
    def _clear_log(self):
        """Clear the log text."""
        try:
            self.log_text.delete("1.0", "end")
        except Exception as e:
            logger.error(f"Failed to clear log: {e}")
    
    def _load_data(self):
        """Load and display configured apps."""
        try:
            self.apps = self.config_manager.load_apps()
        except (FileNotFoundError, ValueError, Exception) as e:
            # Handle case where apps.json doesn't exist or is invalid
            self.apps = []
            try:
                if self.main_window:
                    self.update_status(f"No apps configured - {e}")
            except Exception:
                pass  # Ignore errors updating status
            
            try:
                self._log(f"Warning: {e}")
                self._log("Please add apps in the Apps view")
            except Exception:
                pass  # Ignore errors logging
            
            return  # Return early to avoid errors
        
        if self.apps_frame is None:
            try:
                self._log("Error: Apps frame not initialized")
            except Exception:
                pass
            return  # Return early to avoid errors
        
        # Clear current apps
        try:
            for widget in self.apps_frame.winfo_children():
                widget.destroy()
        except Exception as e:
            logger.error(f"Failed to clear apps frame: {e}")
        
        # Display apps
        if not self.apps:
            try:
                no_apps_label = ctk.CTkLabel(
                    self.apps_frame,
                    text="No apps configured\n\nGo to Apps view to add apps",
                    font=ctk.CTkFont(size=14)
                )
                no_apps_label.pack(pady=20)
            except Exception as e:
                logger.error(f"Failed to create no apps label: {e}")
            return
        
        try:
            self.app_vars = {}
            for app in self.apps:
                var = ctk.BooleanVar(value=True)
                self.app_vars[app.package] = var
                
                app_frame = ctk.CTkFrame(
                    self.apps_frame,
                    height=50
                )
                app_frame.pack(fill="x", pady=5, padx=5)
                app_frame.pack_propagate(False)
                
                checkbox = ctk.CTkCheckBox(
                    app_frame,
                    text=f"{app.name} ({app.package})",
                    variable=var
                )
                checkbox.pack(side="left", padx=10, pady=15)

            # Rebind mousewheel to include new widgets
            if self.apps_frame:
                self.rebind_mousewheel(self.apps_frame)
        except Exception as e:
            logger.error(f"Failed to create app checkboxes: {e}")
            import traceback
        
        # Update device status
        try:
            if self.device_manager:
                device_info = self.device_manager.get_device_info()
                if device_info:
                    self.device_status_label.configure(
                        text=f"Device: {device_info.model} ({device_info.serial})"
                    )
                else:
                    self.device_status_label.configure(text="Device: Connected")
            else:
                self.device_status_label.configure(text="Device: Not connected")
        except Exception as e:
            logger.error(f"Failed to update device status: {e}")
    
    def _toggle_select_all(self):
        """Toggle selection of all apps."""
        try:
            if hasattr(self, 'app_vars'):
                select_all = self.select_all_var.get()
                for var in self.app_vars.values():
                    var.set(select_all)
        except Exception as e:
            logger.error(f"Failed to toggle select all: {e}")
    
    def _run_tests(self):
        """Run selected tests."""
        # Get selected apps
        try:
            selected_apps = [
                app for app in self.apps
                if self.app_vars[app.package].get()
            ]
        except (KeyError, AttributeError) as e:
            logger.error(f"Failed to get selected apps: {e}")
            self.update_status("Error getting selected apps")
            return
        
        if not selected_apps:
            self.update_status("No apps selected")
            return
        
        if not self.device_manager:
            self.update_status("No device connected")
            return
        
        # Update UI
        self.running = True
        self.run_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.progress_label.configure(text="Running tests...")
        self._clear_log()
        self._log(f"Starting tests for {len(selected_apps)} app(s)")
        
        # Run tests in thread
        thread = threading.Thread(target=self._run_tests_thread, args=(selected_apps,))
        thread.daemon = True
        thread.start()
    
    def _run_tests_thread(self, apps: List[AppConfig]):
        """
        Run tests in background thread.
        
        Args:
            apps: List of apps to test
        """
        # Lazy import to avoid initialization issues
        from ..test_engine import get_test_engine


        
        results = []
        try:
            # Initialize test engine
            settings = get_global_settings()
            test_engine = get_test_engine(self.device_manager, settings)
            
            # Run tests
            total = len(apps)
            for i, app in enumerate(apps, 1):
                if not self.running:
                    self._log("Tests stopped by user")
                    break
                
                # Update progress
                progress = (i - 1) / total
                self.progress_bar.set(progress)
                self.progress_label.configure(text=f"Testing {i}/{total}: {app.name}")
                
                # Run test
                self._log(f"Testing: {app.name} ({app.package})")
                result = test_engine.run_test(app)
                results.append(result)
                self._log(f"Completed: {app.name}")
            
            # Complete
            if self.running:
                self.progress_bar.set(1.0)
                self.progress_label.configure(text="Tests completed!")
                self._log("All tests completed successfully")
                self.update_status("Tests completed successfully")
                
                # Generate report
                self._generate_report(results, apps)
            
        except Exception as e:
            self.progress_label.configure(text=f"Error: {e}")
            self._log(f"Error: {e}")
            self.update_status(f"Test error: {e}")
        
        finally:
            self.running = False
            self.run_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
    
    def _generate_report(self, results: list, tested_apps: List[AppConfig]):
        """
        Generate test report.
        
        Args:
            results: List of test results
            tested_apps: List of tested apps
        """
        try:
            self._log("\n" + "="*50)
            self._log("Generating test report...")
            
            # Get device info
            device_info_str = None
            if self.device_manager:
                device_info = self.device_manager.get_device_info()
                if device_info:
                    device_info_str = f"{device_info.model} ({device_info.serial})"
            
            # Generate report
            report_generator = get_report_generator()
            report_files = report_generator.generate_report(
                results,
                device_info=device_info_str,
                formats=["text", "html", "json"]
            )
            
            # Log generated files
            self._log(f"Generated {len(report_files)} report file(s):")
            for report_file in report_files:
                self._log(f"  - {report_file}")
            
            self._log("="*50)
            self.update_status(f"Report generated: {len(report_files)} file(s)")
            
        except Exception as e:
            self._log(f"Error generating report: {e}")
            self.update_status(f"Report generation error: {e}")
    
    def _stop_tests(self):
        """Stop running tests."""
        self.running = False
        self.progress_label.configure(text="Stopping...")
        self._log("Stopping tests...")
        self.update_status("Stopping tests...")