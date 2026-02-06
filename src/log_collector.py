"""
Log Collector Module

Handles Android log collection and analysis.
Collects logcat logs, filters errors, and saves to files.
"""

import subprocess
import re
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .platform_utils import get_platform_utils
from .utils.logger import get_logger
from .exceptions import LogCollectionError, LogParseError

logger = get_logger(__name__)


@dataclass
class LogEntry:
    """
    A single log entry.
    
    Attributes:
        timestamp: Log entry timestamp
        pid: Process ID
        tid: Thread ID
        level: Log level (V, D, I, W, E, F)
        tag: Log tag
        message: Log message
        package: Package name (if applicable)
    """
    timestamp: str
    pid: int
    tid: int
    level: str
    tag: str
    message: str
    package: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert LogEntry to dictionary."""
        return {
            "timestamp": self.timestamp,
            "pid": self.pid,
            "tid": self.tid,
            "level": self.level,
            "tag": self.tag,
            "message": self.message,
            "package": self.package
        }
    
    def is_error(self) -> bool:
        """Check if this log entry is an error."""
        return self.level in ["E", "F"]
    
    def is_warning(self) -> bool:
        """Check if this log entry is a warning."""
        return self.level == "W"


@dataclass
class LogCollectionResult:
    """
    Result of log collection.
    
    Attributes:
        total_entries: Total number of log entries collected
        error_count: Number of error entries
        warning_count: Number of warning entries
        duration: Collection duration in seconds
        log_file: Path to saved log file
    """
    total_entries: int = 0
    error_count: int = 0
    warning_count: int = 0
    duration: float = 0.0
    log_file: Optional[Path] = None
    
    def to_dict(self) -> dict:
        """Convert LogCollectionResult to dictionary."""
        return {
            "total_entries": self.total_entries,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "duration": self.duration,
            "log_file": str(self.log_file) if self.log_file else None
        }


class LogCollector:
    """
    Collector for Android logs via logcat.
    
    Handles logcat collection, filtering, and analysis.
    
    Attributes:
        platform_utils: PlatformUtils instance
        device_serial: Device serial number
        log_filter: Log levels to collect
        package_filter: Package name to filter (optional)
        log_file: Current log file path
        collecting: Whether collection is in progress
        log_process: Logcat subprocess
        entries: Collected log entries
    """
    
    # Log level priorities (higher = more severe)
    LOG_LEVELS = {
        "V": 1,  # Verbose
        "D": 2,  # Debug
        "I": 3,  # Info
        "W": 4,  # Warning
        "E": 5,  # Error
        "F": 6   # Fatal
    }
    
    def __init__(
        self,
        device_serial: str,
        log_filter: List[str] = None,
        package_filter: Optional[str] = None
    ):
        """
        Initialize LogCollector.
        
        Args:
            device_serial: Android device serial number
            log_filter: Log levels to collect (default: ["E", "W", "F"])
            package_filter: Package name to filter logs
        """
        self.platform_utils = get_platform_utils()
        self.device_serial = device_serial
        self.log_filter = log_filter or ["E", "W", "F"]
        self.package_filter = package_filter
        
        self.log_file: Optional[Path] = None
        self.collecting = False
        self.log_process: Optional[subprocess.Popen] = None
        self.entries: List[LogEntry] = []
        self.start_time = 0.0
        self.log_thread: Optional[threading.Thread] = None
    
    def start_collection(self, duration: Optional[int] = None) -> None:
        """
        Start logcat collection in background thread.
        
        Args:
            duration: Collection duration in seconds (None for continuous)
        """
        if self.collecting:
            logger.warning("Log collection already in progress")
            return
        
        # Prepare log file
        self.log_file = self._prepare_log_file()

        logger.info("Starting log collection")
        logger.info(f"Filter: {self.log_filter}")
        if self.package_filter:
            logger.info(f"Package: {self.package_filter}")
        
        # Clear existing logcat buffer
        self._clear_logcat_buffer()
        
        # Start collection in background
        self.start_time = time.time()
        self.collecting = True
        self.entries = []
        
        # Start collection thread
        self.log_thread = threading.Thread(
            target=self._collect_logs,
            args=(duration,),
            daemon=True
        )
        self.log_thread.start()
    
    def stop_collection(self) -> LogCollectionResult:
        """
        Stop log collection and return result.
        
        Returns:
            LogCollectionResult: Collection result
        """
        if not self.collecting:
            return LogCollectionResult()

        logger.info("Stopping log collection")
        self.collecting = False
        
        # Stop logcat process
        if self.log_process:
            self.log_process.terminate()
            try:
                self.log_process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self.log_process.kill()
                self.log_process.wait()
            self.log_process = None
        
        # Wait for thread to finish
        if self.log_thread:
            self.log_thread.join(timeout=5.0)
            self.log_thread = None
        
        # Save logs to file
        if self.entries:
            self._save_logs()
        
        # Calculate result
        duration_time = time.time() - self.start_time
        result = LogCollectionResult(
            total_entries=len(self.entries),
            error_count=sum(1 for e in self.entries if e.is_error()),
            warning_count=sum(1 for e in self.entries if e.is_warning()),
            duration=duration_time,
            log_file=self.log_file
        )

        logger.info("Log collection completed")
        logger.info(f"Total entries: {result.total_entries}")
        logger.info(f"Errors: {result.error_count}, Warnings: {result.warning_count}")
        logger.info(f"Duration: {duration_time:.2f}s")

        return result
    
    def get_entries(self, level: Optional[str] = None) -> List[LogEntry]:
        """
        Get collected log entries.
        
        Args:
            level: Filter by log level (None for all)
        
        Returns:
            List of LogEntry objects
        """
        if level:
            return [e for e in self.entries if e.level == level]
        return self.entries
    
    def get_errors(self) -> List[LogEntry]:
        """
        Get error log entries.
        
        Returns:
            List of error LogEntry objects
        """
        return [e for e in self.entries if e.is_error()]
    
    def get_warnings(self) -> List[LogEntry]:
        """
        Get warning log entries.
        
        Returns:
            List of warning LogEntry objects
        """
        return [e for e in self.entries if e.is_warning()]
    
    def analyze_logs(self) -> dict:
        """
        Analyze collected logs and return statistics.
        
        Returns:
            Dictionary with log statistics
        """
        stats = {
            "total": len(self.entries),
            "by_level": {},
            "by_tag": {},
            "errors": [],
            "warnings": []
        }
        
        for entry in self.entries:
            # Count by level
            if entry.level not in stats["by_level"]:
                stats["by_level"][entry.level] = 0
            stats["by_level"][entry.level] += 1
            
            # Count by tag
            if entry.tag:
                if entry.tag not in stats["by_tag"]:
                    stats["by_tag"][entry.tag] = 0
                stats["by_tag"][entry.tag] += 1
            
            # Collect errors and warnings
            if entry.is_error():
                stats["errors"].append(entry.to_dict())
            elif entry.is_warning():
                stats["warnings"].append(entry.to_dict())
        
        return stats
    
    def _prepare_log_file(self) -> Path:
        """
        Prepare log file path.
        
        Returns:
            Path to log file
        """
        logs_dir = self.platform_utils.get_path("logs")
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_suffix = f"_{self.package_filter}" if self.package_filter else ""
        filename = f"logcat{package_suffix}_{timestamp}.txt"
        
        return logs_dir / filename
    
    def _clear_logcat_buffer(self) -> None:
        """Clear logcat buffer."""
        adb_cmd = self.platform_utils.get_adb_command()
        self.platform_utils.run_command([
            adb_cmd, "-s", self.device_serial,
            "logcat", "-c"
        ])
    
    def _collect_logs(self, duration: Optional[int] = None) -> None:
        """
        Collect logs in background thread.
        
        Args:
            duration: Collection duration in seconds
        """
        # Build logcat command
        adb_cmd = self.platform_utils.get_adb_command()
        logcat_cmd = [
            adb_cmd, "-s", self.device_serial,
            "logcat", "-v", "time"
        ]
        
        # Add package filter if specified
        if self.package_filter:
            logcat_cmd.append(f"*:{self.package_filter}")
        else:
            # Filter by log level
            logcat_cmd.append("*:V")  # Capture all levels, filter later
        
        try:
            # Start logcat process
            self.log_process = subprocess.Popen(
                logcat_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Set timeout for duration
            if duration:
                timeout_time = self.start_time + duration
            else:
                timeout_time = float('inf')
            
            # Read logs in real-time
            while self.collecting and time.time() < timeout_time:
                if self.log_process.poll() is not None:
                    break
                
                try:
                    line = self.log_process.stdout.readline()
                    if not line:
                        break
                    
                    # Parse and filter log
                    self._parse_log_line(line)

                except LogParseError as e:
                    logger.warning(f"Error reading log line: {e}")

        except LogCollectionError as e:
            logger.error(f"Log collection failed: {e}", exc_info=True)
        finally:
            self.collecting = False
            if self.log_process:
                self.log_process.terminate()
                try:
                    self.log_process.wait(timeout=1.0)
                except subprocess.TimeoutExpired:
                    self.log_process.kill()
                self.log_process = None
    
    def _parse_log_line(self, line: str) -> None:
        """
        Parse a single logcat line.
        
        Args:
            line: Log line string
        """
        # logcat time format: MM-DD HH:MM:SS.mmm PID  TID  LEVEL TAG: MESSAGE
        pattern = re.compile(
            r'(\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})\s+(\d+)\s+(\d+)\s+([VDIWEF])\s+([^:]+):\s+(.*)'
        )
        
        match = pattern.match(line)
        if not match:
            return
        
        timestamp, pid, tid, level, tag, message = match.groups()
        
        # Filter by log level
        if level not in self.log_filter:
            return
        
        # Try to extract package from message if possible
        package = self._extract_package(message) or self.package_filter
        
        entry = LogEntry(
            timestamp=timestamp,
            pid=int(pid),
            tid=int(tid),
            level=level,
            tag=tag.strip(),
            message=message.strip(),
            package=package
        )
        
        self.entries.append(entry)
    
    def _extract_package(self, message: str) -> Optional[str]:
        """
        Extract package name from log message.
        
        Args:
            message: Log message
        
        Returns:
            Package name or None
        """
        # Pattern for package names: com.example.app
        package_pattern = re.compile(r'([a-z]+\.[a-z]+\.[a-z]+(?:\.[a-z]+)*)')
        match = package_pattern.search(message)
        return match.group(1) if match else None
    
    def _save_logs(self) -> None:
        """Save collected logs to file."""
        if not self.log_file or not self.entries:
            return
        
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"# Log Collection Report\n")
                f.write(f"# Device: {self.device_serial}\n")
                f.write(f"# Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Total Entries: {len(self.entries)}\n")
                f.write(f"# Filter: {self.log_filter}\n")
                if self.package_filter:
                    f.write(f"# Package: {self.package_filter}\n")
                f.write(f"# " + "="*80 + "\n\n")
                
                for entry in self.entries:
                    f.write(
                        f"{entry.timestamp} {entry.pid:5d} {entry.tid:5d} "
                        f"{entry.level} {entry.tag:30s}: {entry.message}\n"
                    )

            logger.info(f"Logs saved to: {self.log_file}")

        except LogCollectionError as e:
            logger.error(f"Failed to save logs: {e}")


def get_log_collector(
    device_serial: str,
    log_filter: List[str] = None,
    package_filter: Optional[str] = None
) -> LogCollector:
    """
    Get a LogCollector instance.
    
    Args:
        device_serial: Android device serial number
        log_filter: Log levels to collect
        package_filter: Package name to filter
    
    Returns:
        LogCollector instance
    """
    return LogCollector(device_serial, log_filter, package_filter)