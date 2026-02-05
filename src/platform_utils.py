"""
Platform Utilities Module

Provides OS-specific utilities for Windows and Linux platforms.
Handles path management, ADB command execution, and system command execution.
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple, Optional


class PlatformUtils:
    """
    Cross-platform utility class for Windows and Linux systems.
    
    Provides methods to detect the OS, manage project paths,
    execute system commands, and handle ADB operations.
    
    Attributes:
        system (str): Current OS name ("Windows" or "Linux")
        is_windows (bool): True if running on Windows
        is_linux (bool): True if running on Linux
        project_root (Path): Project root directory path
    """
    
    def __init__(self):
        """Initialize PlatformUtils and detect the operating system."""
        self.system = self._detect_system()
        self.is_windows = self.system == "Windows"
        self.is_linux = self.system == "Linux"
        self.project_root = self._get_project_root()
    
    def _detect_system(self) -> str:
        """
        Detect the current operating system.
        
        Returns:
            str: "Windows" or "Linux"
        """
        if sys.platform.startswith('win'):
            return "Windows"
        elif sys.platform.startswith('linux'):
            return "Linux"
        else:
            raise RuntimeError(f"Unsupported platform: {sys.platform}")
    
    def _get_project_root(self) -> Path:
        """
        Get the project root directory path.
        
        The project root is the directory containing this module's parent package.
        
        Returns:
            Path: Absolute path to the project root directory
        """
        # Get the directory containing this file
        current_file = Path(__file__).resolve()
        # Go up one level to src, then up again to project root
        project_root = current_file.parent.parent
        return project_root
    
    def get_adb_command(self) -> str:
        """
        Get the ADB command appropriate for the current OS.
        
        Returns:
            str: ADB command ("adb.exe" on Windows, "adb" on Linux)
        """
        if self.is_windows:
            return "adb.exe"
        else:
            return "adb"
    
    def get_path(self, name: str) -> Path:
        """
        Get the absolute path for a project directory or file.
        
        Args:
            name: Name of the path (one of: "config", "screenshots", 
                  "reports", "logs", "templates")
        
        Returns:
            Path: Absolute path to the requested directory/file
        
        Raises:
            ValueError: If the path name is not recognized
        """
        valid_paths = {
            "config": "config",
            "screenshots": "screenshots",
            "reports": "reports",
            "logs": "logs",
            "templates": "templates",
        }
        
        if name not in valid_paths:
            raise ValueError(
                f"Unknown path name: {name}. "
                f"Valid names are: {list(valid_paths.keys())}"
            )
        
        return self.project_root / valid_paths[name]
    
    def ensure_directories(self) -> None:
        """
        Ensure all required project directories exist.
        
        Creates the following directories if they don't exist:
        - config
        - screenshots
        - reports
        - logs
        - templates
        """
        directories = ["config", "screenshots", "reports", "logs", "templates"]
        
        for dir_name in directories:
            path = self.get_path(dir_name)
            path.mkdir(parents=True, exist_ok=True)
    
    def run_command(
        self,
        cmd: list,
        timeout: Optional[int] = None,
        capture_output: bool = True
    ) -> Tuple[int, str, str]:
        """
        Execute a system command and return the result.
        
        Args:
            cmd: Command to execute as a list of strings (e.g., ["ls", "-l"])
            timeout: Optional timeout in seconds (None for no timeout)
            capture_output: Whether to capture stdout and stderr
        
        Returns:
            Tuple[int, str, str]: (return_code, stdout, stderr)
        
        Example:
            >>> utils = PlatformUtils()
            >>> code, out, err = utils.run_command(["ls", "-l"])
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return -1, "", f"Command execution failed: {str(e)}"
    
    def check_adb_available(self) -> bool:
        """
        Check if ADB (Android Debug Bridge) is available.
        
        Returns:
            bool: True if ADB is available, False otherwise
        """
        adb_cmd = self.get_adb_command()
        code, _, _ = self.run_command([adb_cmd, "version"])
        return code == 0
    
    def get_connected_devices(self) -> list[str]:
        """
        Get a list of connected Android device serial numbers.
        
        Returns:
            List of device serial numbers (empty list if no devices connected)
        """
        adb_cmd = self.get_adb_command()
        code, output, _ = self.run_command([adb_cmd, "devices"])
        
        if code != 0:
            return []
        
        devices = []
        lines = output.strip().split('\n')[1:]  # Skip header line
        
        for line in lines:
            if line.strip() and '\tdevice' in line:
                serial = line.split('\t')[0].strip()
                devices.append(serial)
        
        return devices


# Global instance for convenience
_platform_utils: Optional[PlatformUtils] = None


def get_platform_utils() -> PlatformUtils:
    """
    Get the global PlatformUtils instance.
    
    Returns:
        PlatformUtils: The global instance
    """
    global _platform_utils
    if _platform_utils is None:
        _platform_utils = PlatformUtils()
    return _platform_utils