"""
Apps View for GUI

Displays and manages app configurations and installed apps.
"""

import customtkinter as ctk
from typing import Optional, List

from ..config_manager import ConfigManager, AppConfig
from .base_view import BaseView

from ..utils.logger import get_logger

logger = get_logger(__name__)


class AppsView(BaseView):
    """
    View for managing app configurations and viewing installed apps.
    
    Displays list of configured apps and installed apps on device,
    allows adding/editing/deleting configurations.
    
    Attributes:
        config_manager: ConfigManager instance
        main_window: Reference to main window
        apps: List of configured apps
        device_manager: DeviceManager instance (optional)
    """
    
    def __init__(self, parent, config_manager: ConfigManager, main_window):
        """
        Initialize apps view.

        Args:
            parent: Parent widget
            config_manager: ConfigManager instance
            main_window: Reference to main window
        """
        self.config_manager = config_manager
        # Call parent __init__ which triggers lifecycle hooks
        super().__init__(parent, main_window)

    def _setup_state(self):
        """Initialize apps view state."""
        self.device_manager = self.main_window.device_manager
        self.apps: List[AppConfig] = []
        self.installed_apps: List[dict] = []
        self._installed_apps_loaded = False

    def _build_ui(self):
        """Build apps view UI."""
        # Title
        self._build_title("App Configurations")

        # Tabview for configured and installed apps
        self.tabview = ctk.CTkTabview(
            self,
            width=700,
            height=500
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Add tabs
        self.tabview.add("Configured Apps")
        self.tabview.add("Installed Apps")

        # Configured Apps Tab
        self._build_configured_apps_tab()

        # Installed Apps Tab
        self._build_installed_apps_tab()
    
    def _build_configured_apps_tab(self):
        """Build the configured apps tab."""
        tab_frame = self.tabview.tab("Configured Apps")
        
        # Buttons frame - FIXED AT TOP
        buttons_frame = ctk.CTkFrame(tab_frame, height=60)
        buttons_frame.pack(fill="x", padx=10, pady=(10, 5))
        buttons_frame.pack_propagate(False)
        
        # Button container for horizontal layout
        button_container = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        button_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add button
        add_btn = ctk.CTkButton(
            button_container,
            text="➕ Add App",
            command=self._add_app,
            width=130,
            height=35
        )
        add_btn.pack(side="left", padx=5, pady=5)

        # Refresh button
        refresh_btn = ctk.CTkButton(
            button_container,
            text="🔄 Refresh",
            command=self._load_data,
            width=130,
            height=35
        )
        refresh_btn.pack(side="left", padx=5, pady=5)

        # Configured apps list (expands to fill space)
        self.configured_apps_frame = ctk.CTkScrollableFrame(tab_frame)
        self.configured_apps_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._bind_mousewheel(self.configured_apps_frame)
        
        # App info frame - FIXED AT BOTTOM
        self.info_frame = ctk.CTkFrame(tab_frame, height=100)
        self.info_frame.pack(fill="x", side="bottom", padx=10, pady=(0, 10))
        self.info_frame.pack_propagate(False)
        
        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Select an app to see details",
            font=ctk.CTkFont(size=14)
        )
        self.info_label.pack(expand=True, pady=20)
    
    def _build_installed_apps_tab(self):
        """Build the installed apps tab."""
        tab_frame = self.tabview.tab("Installed Apps")
        
        # Header - FIXED AT TOP
        header_frame = ctk.CTkFrame(tab_frame, height=60)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        # Button container for horizontal layout
        button_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            button_container,
            text="🔄 Refresh Installed Apps",
            command=self._load_installed_apps,
            width=200,
            height=35
        )
        refresh_btn.pack(side="left", padx=5, pady=5)
        
        # Device status
        self.device_status_label = ctk.CTkLabel(
            button_container,
            text="Loading...",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.device_status_label.pack(side="right", padx=10, pady=10)
        
        # Installed apps list (expands to fill space)
        self.installed_apps_frame = ctk.CTkScrollableFrame(tab_frame)
        self.installed_apps_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._bind_mousewheel(self.installed_apps_frame)

        # Show placeholder message initially
        self._show_no_installed_apps("Click Refresh to load installed apps")

    def _load_data(self):
        """Load and display configured apps."""
        try:
            self.apps = self.config_manager.load_apps()
        except Exception as e:
            self.update_status(f"Error loading apps: {e}")
            logger.error(f"Failed to load apps: {e}")
            return
        
        # Clear current apps
        for widget in self.configured_apps_frame.winfo_children():
            widget.destroy()
        
        # Display apps
        if not self.apps:
            no_apps_label = ctk.CTkLabel(
                self.configured_apps_frame,
                text="No apps configured\n\nAdd apps to test",
                font=ctk.CTkFont(size=14)
            )
            no_apps_label.pack(pady=20)
            self.update_status("No apps configured")
            return
        
        for i, app in enumerate(self.apps, 1):
            app_frame = ctk.CTkFrame(
                self.configured_apps_frame,
                height=100
            )
            app_frame.pack(fill="x", pady=5, padx=5)
            app_frame.pack_propagate(False)
            
            # App number
            num_label = ctk.CTkLabel(
                app_frame,
                text=f"{i}.",
                font=ctk.CTkFont(size=16, weight="bold"),
                width=30
            )
            num_label.pack(side="left", padx=10, pady=10)
            
            # App info
            info_text = f"Name: {app.name}\n"
            info_text += f"Package: {app.package}\n"
            info_text += f"Activity: {app.activity}\n"
            info_text += f"Duration: {app.test_duration}s"
            
            info_label = ctk.CTkLabel(
                app_frame,
                text=info_text,
                font=ctk.CTkFont(size=14),
                anchor="w"
            )
            info_label.pack(side="left", padx=10, pady=10)
            
            # Buttons
            edit_btn = ctk.CTkButton(
                app_frame,
                text="Edit",
                command=lambda a=app: self._edit_app(a),
                width=60
            )
            edit_btn.pack(side="right", padx=5, pady=20)
            
            delete_btn = ctk.CTkButton(
                app_frame,
                text="Delete",
                command=lambda a=app: self._delete_app(a),
                width=60,
                fg_color="#DC3545",
                hover_color="#BB2D3B"
            )
            delete_btn.pack(side="right", padx=5, pady=20)

        # Rebind mousewheel to include new widgets
        self.rebind_mousewheel(self.configured_apps_frame)

        self.update_status(f"Found {len(self.apps)} configured app(s)")
    
    def _load_installed_apps(self):
        """Load and display installed apps from device."""
        # Check if device is connected
        if not self.device_manager or not self.device_manager.is_connected():
            self.device_status_label.configure(
                text="No device connected",
                text_color="#DC3545"
            )
            self._show_no_installed_apps("No device connected\nPlease connect a device in Devices tab")
            return
        
        try:
            # Use aapt=True to get actual app names from device
            self.installed_apps = self.device_manager.get_installed_apps(third_party_only=True, use_aapt=True)
            
            if not self.installed_apps:
                self.device_status_label.configure(
                    text=f"Found 0 apps",
                    text_color="#888888"
                )
                self._show_no_installed_apps("No third-party apps found on device")
                return
            
            self.device_status_label.configure(
                text=f"Found {len(self.installed_apps)} apps",
                text_color="#2CC985"
            )
            
            # Clear current apps
            for widget in self.installed_apps_frame.winfo_children():
                widget.destroy()
            
            # Display apps (limit to first 100 to avoid performance issues)
            for i, app_info in enumerate(self.installed_apps[:100], 1):
                app_frame = ctk.CTkFrame(
                    self.installed_apps_frame,
                    height=80
                )
                app_frame.pack(fill="x", pady=5, padx=5)
                app_frame.pack_propagate(False)
                
                # App number
                num_label = ctk.CTkLabel(
                    app_frame,
                    text=f"{i}.",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    width=30
                )
                num_label.pack(side="left", padx=10, pady=10)
                
                # App info
                info_text = f"Name: {app_info['name']}\n"
                info_text += f"Package: {app_info['package']}"
                
                info_label = ctk.CTkLabel(
                    app_frame,
                    text=info_text,
                    font=ctk.CTkFont(size=14),
                    anchor="w"
                )
                info_label.pack(side="left", padx=10, pady=10)
                
                # Add button
                add_btn = ctk.CTkButton(
                    app_frame,
                    text="+ Add to Test",
                    command=lambda a=app_info: self._add_installed_app(a),
                    width=100,
                    fg_color="#2CC985",
                    hover_color="#1FA868"
                )
                add_btn.pack(side="right", padx=10, pady=20)

            # Rebind mousewheel to include new widgets
            self.rebind_mousewheel(self.installed_apps_frame)

            self._installed_apps_loaded = True
            self.update_status(f"Loaded {len(self.installed_apps[:100])} installed app(s)")
        
        except Exception as e:
            self.device_status_label.configure(
                text="Error loading apps",
                text_color="#DC3545"
            )
            self._show_no_installed_apps(f"Error: {str(e)}")
            self.update_status(f"Error loading installed apps: {e}")
    
    def _show_no_installed_apps(self, message: str):
        """Show message when no apps are available."""
        for widget in self.installed_apps_frame.winfo_children():
            widget.destroy()
        
        no_apps_label = ctk.CTkLabel(
            self.installed_apps_frame,
            text=message,
            font=ctk.CTkFont(size=14)
        )
        no_apps_label.pack(pady=20)
    
    def _add_installed_app(self, app_info: dict):
        """
        Add an installed app to configured apps.
        
        Args:
            app_info: Dict with 'package' and 'name' keys
        """
        # Create dialog for app configuration
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add App Configuration")
        dialog.geometry("450x350")
        
        # Name
        name_label = ctk.CTkLabel(dialog, text="Name:")
        name_label.pack(pady=(20, 5))
        name_entry = ctk.CTkEntry(dialog, width=350)
        name_entry.pack()
        name_entry.insert(0, app_info['name'])
        
        # Package
        package_label = ctk.CTkLabel(dialog, text="Package:")
        package_label.pack(pady=(10, 5))
        package_entry = ctk.CTkEntry(dialog, width=350)
        package_entry.pack()
        package_entry.insert(0, app_info['package'])
        package_entry.configure(state="disabled")  # Package name from device
        
        # Activity
        activity_label = ctk.CTkLabel(dialog, text="Activity (main):")
        activity_label.pack(pady=(10, 5))
        activity_entry = ctk.CTkEntry(dialog, width=350)
        activity_entry.pack()
        activity_entry.insert(0, ".MainActivity")
        
        # Duration
        duration_label = ctk.CTkLabel(dialog, text="Test Duration (seconds):")
        duration_label.pack(pady=(10, 5))
        duration_entry = ctk.CTkEntry(dialog, width=350)
        duration_entry.pack()
        duration_entry.insert(0, "120")
        
        # Save button
        def save():
            try:
                app = AppConfig(
                    name=name_entry.get(),
                    package=app_info['package'],
                    activity=activity_entry.get(),
                    test_duration=int(duration_entry.get())
                )
                
                if app.validate():
                    self.apps.append(app)
                    self.config_manager.save_apps(self.apps)
                    self._load_data()
                    dialog.destroy()

                    # Switch to configured apps tab
                    self.tabview.set("Configured Apps")
                    self.update_status("App added successfully")
                else:
                    self.update_status("Invalid app configuration")
            except Exception as e:
                self.update_status(f"Error: {e}")
        
        save_btn = ctk.CTkButton(
            dialog,
            text="Save",
            command=save,
            width=100
        )
        save_btn.pack(pady=20)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            dialog,
            text="Cancel",
            command=dialog.destroy,
            width=100,
            fg_color="#888888",
            hover_color="#666666"
        )
        cancel_btn.pack(pady=5)
    
    def _add_app(self):
        """Add a new app configuration."""
        # Create dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add App")
        dialog.geometry("400x350")
        
        # Name
        name_label = ctk.CTkLabel(dialog, text="Name:")
        name_label.pack(pady=(20, 5))
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.pack()
        
        # Package
        package_label = ctk.CTkLabel(dialog, text="Package:")
        package_label.pack(pady=(10, 5))
        package_entry = ctk.CTkEntry(dialog, width=300)
        package_entry.pack()
        
        # Activity
        activity_label = ctk.CTkLabel(dialog, text="Activity:")
        activity_label.pack(pady=(10, 5))
        activity_entry = ctk.CTkEntry(dialog, width=300)
        activity_entry.pack()
        activity_entry.insert(0, ".MainActivity")
        
        # Duration
        duration_label = ctk.CTkLabel(dialog, text="Duration (seconds):")
        duration_label.pack(pady=(10, 5))
        duration_entry = ctk.CTkEntry(dialog, width=300)
        duration_entry.pack()
        duration_entry.insert(0, "120")
        
        # Save button
        def save():
            try:
                app = AppConfig(
                    name=name_entry.get(),
                    package=package_entry.get(),
                    activity=activity_entry.get(),
                    test_duration=int(duration_entry.get())
                )
                
                if app.validate():
                    self.apps.append(app)
                    self.config_manager.save_apps(self.apps)
                    self._load_data()
                    dialog.destroy()
                    self.update_status("App added successfully")
                else:
                    self.update_status("Invalid app configuration")
            except Exception as e:
                self.update_status(f"Error: {e}")
        
        save_btn = ctk.CTkButton(
            dialog,
            text="Save",
            command=save,
            width=100
        )
        save_btn.pack(pady=20)
    
    def _edit_app(self, app: AppConfig):
        """
        Edit an existing app.
        
        Args:
            app: AppConfig to edit
        """
        # Create dialog window
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit App")
        dialog.geometry("400x350")
        
        # Name
        name_label = ctk.CTkLabel(dialog, text="Name:")
        name_label.pack(pady=(20, 5))
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.pack()
        name_entry.insert(0, app.name)
        
        # Package
        package_label = ctk.CTkLabel(dialog, text="Package:")
        package_label.pack(pady=(10, 5))
        package_entry = ctk.CTkEntry(dialog, width=300)
        package_entry.pack()
        package_entry.insert(0, app.package)
        
        # Activity
        activity_label = ctk.CTkLabel(dialog, text="Activity:")
        activity_label.pack(pady=(10, 5))
        activity_entry = ctk.CTkEntry(dialog, width=300)
        activity_entry.pack()
        activity_entry.insert(0, app.activity)
        
        # Duration
        duration_label = ctk.CTkLabel(dialog, text="Duration (seconds):")
        duration_label.pack(pady=(10, 5))
        duration_entry = ctk.CTkEntry(dialog, width=300)
        duration_entry.pack()
        duration_entry.insert(0, str(app.test_duration))
        
        # Save button
        def save():
            try:
                app.name = name_entry.get()
                app.package = package_entry.get()
                app.activity = activity_entry.get()
                app.test_duration = int(duration_entry.get())
                
                if app.validate():
                    self.config_manager.save_apps(self.apps)
                    self._load_data()
                    dialog.destroy()
                    self.update_status("App updated successfully")
                else:
                    self.update_status("Invalid app configuration")
            except Exception as e:
                self.update_status(f"Error: {e}")
        
        save_btn = ctk.CTkButton(
            dialog,
            text="Save",
            command=save,
            width=100
        )
        save_btn.pack(pady=20)
    
    def _delete_app(self, app: AppConfig):
        """
        Delete an app.
        
        Args:
            app: AppConfig to delete
        """
        if app in self.apps:
            self.apps.remove(app)
            self.config_manager.save_apps(self.apps)
            self._load_data()
            self.update_status("App deleted")