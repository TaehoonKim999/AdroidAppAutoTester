"""
Main Entry Point for Android App Auto Tester

CLI interface for running automated tests with optional GUI.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .config_manager import AppConfig, GlobalSettings, get_config_manager, get_global_settings
from .device_manager import DeviceManager, get_device_manager
from .platform_utils import get_platform_utils
from .report_generator import get_report_generator
from .test_engine import get_test_engine


class CLI:
    """
    Command-line interface for Android App Auto Tester.
    
    Attributes:
        args: Parsed command-line arguments
        config_manager: ConfigManager instance
        settings: Global settings
        device_manager: DeviceManager instance
    """
    
    def __init__(self):
        """Initialize CLI."""
        self.config_manager = get_config_manager()
        self.settings = get_global_settings()
        self.device_manager = None
        self.args = None
    
    def run(self):
        """Run CLI application."""
        self.args = self._parse_args()
        
        try:
            if self.args.command == "list":
                self._list_devices()
            elif self.args.command == "run":
                self._run_tests()
            elif self.args.command == "config":
                self._manage_config()
            else:
                self._print_help()
        
        except KeyboardInterrupt:
            print("\n\n[INFO] Interrupted by user")
            sys.exit(1)
        
        except Exception as e:
            print(f"\n[ERROR] {e}")
            sys.exit(1)
    
    def _parse_args(self) -> argparse.Namespace:
        """
        Parse command-line arguments.
        
        Returns:
            Parsed arguments namespace
        """
        parser = argparse.ArgumentParser(
            description="Android App Auto Tester - Automated UI Testing Tool",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s list                          # List connected devices
  %(prog)s run                           # Run all configured tests
  %(prog)s run --app com.example.app       # Run specific app
  %(prog)s run --duration 60              # Run for 60 seconds
  %(prog)s run --report html json          # Generate HTML and JSON reports
  %(prog)s --gui                          # Launch GUI
            """
        )
        
        parser.add_argument(
            "--gui",
            "-g",
            action="store_true",
            help="Launch graphical user interface"
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Command to execute")
        
        # List command
        list_parser = subparsers.add_parser(
            "list",
            help="List connected devices and apps"
        )
        list_parser.add_argument(
            "--apps",
            action="store_true",
            help="List configured apps instead of devices"
        )
        
        # Run command
        run_parser = subparsers.add_parser(
            "run",
            help="Run automated tests"
        )
        run_parser.add_argument(
            "--app",
            type=str,
            help="Specific app package to test (default: all)"
        )
        run_parser.add_argument(
            "--duration",
            type=int,
            help="Test duration in seconds (overrides config)"
        )
        run_parser.add_argument(
            "--actions",
            nargs="+",
            choices=["scroll", "click_buttons", "input_text", "back_navigation"],
            help="Actions to perform (default: from config)"
        )
        run_parser.add_argument(
            "--report",
            nargs="+",
            choices=["text", "html", "json"],
            default=["text"],
            help="Report formats to generate (default: text)"
        )
        run_parser.add_argument(
            "--no-logcat",
            action="store_true",
            help="Disable logcat collection"
        )
        run_parser.add_argument(
            "--no-screenshot",
            action="store_true",
            help="Disable screenshots on error"
        )
        run_parser.add_argument(
            "--output-dir",
            type=str,
            help="Output directory for reports"
        )
        
        # Config command
        config_parser = subparsers.add_parser(
            "config",
            help="Manage configuration"
        )
        config_parser.add_argument(
            "--set",
            type=str,
            nargs=2,
            metavar=("KEY", "VALUE"),
            help="Set configuration value"
        )
        config_parser.add_argument(
            "--get",
            type=str,
            metavar="KEY",
            help="Get configuration value"
        )
        config_parser.add_argument(
            "--reset",
            action="store_true",
            help="Reset configuration to defaults"
        )
        
        return parser.parse_args()
    
    def _list_devices(self):
        """List connected Android devices."""
        print("\n" + "="*60)
        print("  Connected Devices")
        print("="*60 + "\n")
        
        self.device_manager = get_device_manager()
        devices = self.device_manager.list_devices()
        
        if not devices:
            print("[WARNING] No devices connected")
            print("\nMake sure:")
            print("  1. USB debugging is enabled on the device")
            print("  2. Device is connected via USB")
            print("  3. Device is authorized for ADB")
            sys.exit(1)
        
        for i, device in enumerate(devices, 1):
            print(f"{i}. {device.serial}")
            if device.model:
                print(f"   Model: {device.model}")
            if device.android_version:
                print(f"   Android: {device.android_version}")
            print()
        
        # List apps if requested
        if hasattr(self.args, 'apps') and self.args.apps:
            self._list_apps()
    
    def _list_apps(self):
        """List configured apps."""
        print("\n" + "="*60)
        print("  Configured Apps")
        print("="*60 + "\n")
        
        apps = self.config_manager.load_apps()
        
        if not apps:
            print("[WARNING] No apps configured")
            print("\nConfigure apps in: config/apps.json")
            return
        
        for i, app in enumerate(apps, 1):
            print(f"{i}. {app.name}")
            print(f"   Package: {app.package}")
            print(f"   Activity: {app.activity}")
            print(f"   Duration: {app.test_duration}s")
            print(f"   Actions: {', '.join(app.test_actions)}")
            print()
    
    def _run_tests(self):
        """Run automated tests."""
        # Load settings
        self.settings = get_global_settings()
        
        # Override settings from command line
        if self.args.duration:
            self.settings.test_duration = self.args.duration
        
        if self.args.no_logcat:
            self.settings.collect_logcat = False
        
        if self.args.no_screenshot:
            self.settings.screenshot_on_error = False
        
        # Initialize device manager
        print("[INFO] Initializing device manager...")
        self.device_manager = get_device_manager()
        
        devices = self.device_manager.list_devices()
        
        if not devices:
            print("[ERROR] No devices connected")
            sys.exit(1)
        
        if len(devices) > 1:
            print(f"[WARNING] Multiple devices found, using: {devices[0].serial}")
        
        # Connect to device
        print(f"[INFO] Connecting to device: {devices[0].serial}")
        if not self.device_manager.connect(devices[0].serial):
            print("[ERROR] Failed to connect to device")
            sys.exit(1)
        
        # Get device info
        device_info = self.device_manager.get_device_info()
        if device_info:
            print(f"[INFO] Device: {device_info.model or 'Unknown'}")
            print(f"[INFO] Android: {device_info.android_version or 'Unknown'}")
        
        # Load apps to test
        apps = self.config_manager.load_apps()
        
        if not apps:
            print("[ERROR] No apps configured")
            print("Configure apps in: config/apps.json")
            sys.exit(1)
        
        # Filter specific app if requested
        if self.args.app:
            apps = [app for app in apps if app.package == self.args.app]
            if not apps:
                print(f"[ERROR] App not found: {self.args.app}")
                sys.exit(1)
        
        # Override test duration for apps
        if self.args.duration:
            for app in apps:
                app.test_duration = self.args.duration
        
        # Override actions if specified
        if self.args.actions:
            for app in apps:
                app.test_actions = self.args.actions
        
        # Initialize test engine
        test_engine = get_test_engine(self.device_manager, self.settings)
        
        # Run tests
        print("\n[INFO] Starting test run...")
        results = test_engine.run_all_tests(apps)
        
        # Generate reports
        if results:
            output_dir = None
            if self.args.output_dir:
                output_dir = Path(self.args.output_dir)
            
            report_generator = get_report_generator(output_dir)
            
            device_info_str = None
            if device_info:
                device_info_str = f"{device_info.model} ({device_info.serial})"
            
            report_files = report_generator.generate_report(
                results,
                device_info=device_info_str,
                formats=self.args.report
            )
            
            if report_files:
                print("\n[OK] Reports generated:")
                for file_path in report_files:
                    print(f"  - {file_path}")
    
    def _manage_config(self):
        """Manage configuration settings."""
        if self.args.reset:
            self._reset_config()
        elif self.args.set:
            key, value = self.args.set
            self._set_config(key, value)
        elif self.args.get:
            self._get_config(self.args.get)
        else:
            self._show_config()
    
    def _reset_config(self):
        """Reset configuration to defaults."""
        print("[INFO] Resetting configuration to defaults...")
        self.config_manager.reset_settings()
        print("[OK] Configuration reset to defaults")
    
    def _set_config(self, key: str, value: str):
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        print(f"[INFO] Setting {key} = {value}")
        
        # Parse value to appropriate type
        if value.lower() in ["true", "false"]:
            value = value.lower() == "true"
        elif value.isdigit():
            value = int(value)
        
        self.config_manager.set_setting(key, value)
        print("[OK] Configuration saved")
    
    def _get_config(self, key: str):
        """
        Get configuration value.
        
        Args:
            key: Configuration key
        """
        settings = self.config_manager.load_settings()
        
        if key in settings:
            print(f"{key} = {settings[key]}")
        else:
            print(f"[ERROR] Unknown setting: {key}")
    
    def _show_config(self):
        """Show current configuration."""
        print("\n" + "="*60)
        print("  Current Configuration")
        print("="*60 + "\n")
        
        settings = self.config_manager.load_settings()
        
        for key, value in settings.items():
            print(f"{key}: {value}")
    
    def _print_help(self):
        """Print help information."""
        self._parse_args().print_help()


def _launch_gui():
    """Launch GUI application."""
    print("[INFO] Launching GUI...")
    
    try:
        from .gui import run_gui
        run_gui()
    except ImportError as e:
        print(f"[ERROR] Failed to import GUI: {e}")
        print("[ERROR] Make sure customtkinter is installed: pip install customtkinter")
        sys.exit(1)


def main():
    """Main entry point."""
    # Check for GUI argument before parsing
    if "--gui" in sys.argv or "-g" in sys.argv:
        _launch_gui()
    else:
        cli = CLI()
        cli.run()


if __name__ == "__main__":
    main()