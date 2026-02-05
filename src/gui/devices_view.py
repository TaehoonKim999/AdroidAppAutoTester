"""
Devices View for GUI

Displays and manages connected Android devices.
"""

import customtkinter as ctk
from typing import Optional, List, Callable

from ..device_manager import DeviceInfo, DeviceManager


class DevicesView(ctk.CTkFrame):
    """
    View for managing connected Android devices.
    
    Displays list of devices and allows selection.
    
    Attributes:
        device_manager: DeviceManager instance
        main_window: Reference to main window
        selected_device: Currently selected device
    """
    
    def __init__(self, parent, device_manager: Optional[DeviceManager], main_window):
        """
        Initialize devices view.
        
        Args:
            parent: Parent widget
            device_manager: DeviceManager instance
            main_window: Reference to main window
        """
        super().__init__(parent)
        
        self.device_manager = device_manager
        self.main_window = main_window
        self.selected_device: Optional[DeviceInfo] = None
        
        # Build UI
        self._build_ui()
        
        # Load devices
        self._load_devices()
    
    def _build_ui(self):
        """Build devices view UI."""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Connected Devices",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            self,
            text="🔄 Refresh",
            command=self._load_devices,
            width=120
        )
        refresh_btn.pack(pady=(0, 10))
        
        # Devices list
        self.devices_frame = ctk.CTkScrollableFrame(
            self,
            height=400
        )
        self.devices_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Device info frame
        self.info_frame = ctk.CTkFrame(self, height=200)
        self.info_frame.pack(fill="x", padx=10, pady=(10, 20))
        self.info_frame.pack_propagate(False)
        
        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Select a device to see details",
            font=ctk.CTkFont(size=14)
        )
        self.info_label.pack(expand=True, pady=20)
    
    def _load_devices(self):
        """Load and display connected devices."""
        # Clear current devices
        for widget in self.devices_frame.winfo_children():
            widget.destroy()
        
        # Get devices
        if self.device_manager:
            devices = self.device_manager.list_devices()
        else:
            devices = []
        
        # Display devices
        if not devices:
            no_devices_label = ctk.CTkLabel(
                self.devices_frame,
                text="No devices connected\n\nMake sure:\n• USB debugging is enabled\n• Device is connected\n• Device is authorized",
                font=ctk.CTkFont(size=14)
            )
            no_devices_label.pack(pady=20)
            self.main_window._update_status("No devices found")
            return
        
        for i, device in enumerate(devices, 1):
            device_frame = ctk.CTkFrame(
                self.devices_frame,
                height=80
            )
            device_frame.pack(fill="x", pady=5, padx=5)
            device_frame.pack_propagate(False)
            
            # Device number
            num_label = ctk.CTkLabel(
                device_frame,
                text=f"{i}.",
                font=ctk.CTkFont(size=16, weight="bold"),
                width=30
            )
            num_label.pack(side="left", padx=10, pady=10)
            
            # Device info
            info_text = f"Serial: {device.serial}"
            if device.model:
                info_text += f"\nModel: {device.model}"
            if device.android_version:
                info_text += f"\nAndroid: {device.android_version}"
            
            info_label = ctk.CTkLabel(
                device_frame,
                text=info_text,
                font=ctk.CTkFont(size=14),
                anchor="w"
            )
            info_label.pack(side="left", padx=10, pady=10)
            
            # Select button
            select_btn = ctk.CTkButton(
                device_frame,
                text="Select",
                command=lambda d=device: self._select_device(d),
                width=80
            )
            select_btn.pack(side="right", padx=10, pady=20)
        
        self.main_window._update_status(f"Found {len(devices)} device(s)")
    
    def _select_device(self, device: DeviceInfo):
        """
        Select a device.
        
        Args:
            device: DeviceInfo to select
        """
        self.selected_device = device
        
        # Update info display
        self._update_device_info(device)
        
        # Set device manager in main window (create new DeviceManager with this serial)
        from ..device_manager import get_device_manager
        new_device_manager = get_device_manager(device.serial)
        if new_device_manager and new_device_manager.connect():
            self.main_window.set_device_manager(new_device_manager)
            self.main_window._update_status(f"Selected: {device.serial}")
        else:
            self.main_window._update_status(f"Failed to connect: {device.serial}")
    
    def _update_device_info(self, device: DeviceInfo):
        """
        Update device info display.
        
        Args:
            device: DeviceInfo to display
        """
        self.info_label.configure(
            text=f"Selected Device:\n\n"
                  f"Serial: {device.serial}\n"
                  f"Model: {device.model or 'Unknown'}\n"
                  f"Android: {device.android_version or 'Unknown'}"
        )