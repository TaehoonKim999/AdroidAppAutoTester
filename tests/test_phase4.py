"""
Unit Tests for Phase 4: Log Collector

Tests:
- LogEntry dataclass
- LogCollectionResult dataclass
- LogCollector class
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.log_collector import LogEntry, LogCollectionResult, LogCollector


class TestLogEntry:
    """Test cases for LogEntry dataclass."""
    
    def test_creation(self):
        """Test LogEntry creation with valid data."""
        entry = LogEntry(
            timestamp="01-02 12:34:56.789",
            pid=12345,
            tid=54321,
            level="E",
            tag="AndroidRuntime",
            message="Error: NullPointerException",
            package="com.example.app"
        )
        
        assert entry.timestamp == "01-02 12:34:56.789"
        assert entry.pid == 12345
        assert entry.tid == 54321
        assert entry.level == "E"
        assert entry.tag == "AndroidRuntime"
        assert entry.message == "Error: NullPointerException"
        assert entry.package == "com.example.app"
        
        print("✓ LogEntry creation test passed")
    
    def test_to_dict(self):
        """Test LogEntry to_dict conversion."""
        entry = LogEntry(
            timestamp="01-02 12:34:56.789",
            pid=12345,
            tid=54321,
            level="E",
            tag="AndroidRuntime",
            message="Error: NullPointerException",
            package="com.example.app"
        )
        
        data = entry.to_dict()
        assert isinstance(data, dict)
        assert data["timestamp"] == "01-02 12:34:56.789"
        assert data["pid"] == 12345
        assert data["level"] == "E"
        
        print("✓ LogEntry to_dict test passed")
    
    def test_is_error(self):
        """Test is_error method."""
        error_entry = LogEntry(
            timestamp="01-02 12:34:56.789",
            pid=12345,
            tid=54321,
            level="E",
            tag="AndroidRuntime",
            message="Error",
            package="com.example.app"
        )
        
        fatal_entry = LogEntry(
            timestamp="01-02 12:34:56.789",
            pid=12345,
            tid=54321,
            level="F",
            tag="AndroidRuntime",
            message="Fatal",
            package="com.example.app"
        )
        
        warning_entry = LogEntry(
            timestamp="01-02 12:34:56.789",
            pid=12345,
            tid=54321,
            level="W",
            tag="AndroidRuntime",
            message="Warning",
            package="com.example.app"
        )
        
        assert error_entry.is_error() is True
        assert fatal_entry.is_error() is True
        assert warning_entry.is_error() is False
        
        print("✓ LogEntry is_error test passed")
    
    def test_is_warning(self):
        """Test is_warning method."""
        warning_entry = LogEntry(
            timestamp="01-02 12:34:56.789",
            pid=12345,
            tid=54321,
            level="W",
            tag="AndroidRuntime",
            message="Warning",
            package="com.example.app"
        )
        
        error_entry = LogEntry(
            timestamp="01-02 12:34:56.789",
            pid=12345,
            tid=54321,
            level="E",
            tag="AndroidRuntime",
            message="Error",
            package="com.example.app"
        )
        
        assert warning_entry.is_warning() is True
        assert error_entry.is_warning() is False
        
        print("✓ LogEntry is_warning test passed")


class TestLogCollectionResult:
    """Test cases for LogCollectionResult dataclass."""
    
    def test_creation(self):
        """Test LogCollectionResult creation with default values."""
        result = LogCollectionResult()
        
        assert result.total_entries == 0
        assert result.error_count == 0
        assert result.warning_count == 0
        assert result.duration == 0.0
        assert result.log_file is None
        
        print("✓ LogCollectionResult creation test passed")
    
    def test_creation_with_values(self):
        """Test LogCollectionResult creation with custom values."""
        result = LogCollectionResult(
            total_entries=100,
            error_count=5,
            warning_count=10,
            duration=30.5,
            log_file=Path("/path/to/log.txt")
        )
        
        assert result.total_entries == 100
        assert result.error_count == 5
        assert result.warning_count == 10
        assert result.duration == 30.5
        assert result.log_file == Path("/path/to/log.txt")
        
        print("✓ LogCollectionResult creation with values test passed")
    
    def test_to_dict(self):
        """Test LogCollectionResult to_dict conversion."""
        result = LogCollectionResult(
            total_entries=100,
            error_count=5,
            warning_count=10,
            duration=30.5,
            log_file=Path("/path/to/log.txt")
        )
        
        data = result.to_dict()
        assert isinstance(data, dict)
        assert data["total_entries"] == 100
        assert data["error_count"] == 5
        assert data["duration"] == 30.5
        
        print("✓ LogCollectionResult to_dict test passed")


class TestLogCollector:
    """Test cases for LogCollector class."""
    
    def test_initialization(self):
        """Test LogCollector initialization."""
        collector = LogCollector("TEST123")
        
        assert collector.device_serial == "TEST123"
        assert collector.log_filter == ["E", "W", "F"]
        assert collector.package_filter is None
        assert len(collector.entries) == 0
        assert collector.collecting is False
        
        print("✓ LogCollector initialization test passed")
    
    def test_initialization_with_filters(self):
        """Test LogCollector initialization with custom filters."""
        collector = LogCollector(
            "TEST123",
            log_filter=["E", "W"],
            package_filter="com.example.app"
        )
        
        assert collector.log_filter == ["E", "W"]
        assert collector.package_filter == "com.example.app"
        
        print("✓ LogCollector initialization with filters test passed")
    
    def test_parse_logs(self):
        """Test _parse_logs method."""
        collector = LogCollector("TEST123", log_filter=["E", "W", "I"])
        
        raw_logs = """
01-02 12:34:56.789  12345  54321 E AndroidRuntime: FATAL EXCEPTION: main
01-02 12:34:57.123  12346  54322 W ActivityManager: Activity pause timeout
01-02 12:34:58.456  12347  54323 I System.out: Test message
"""
        
        collector._parse_logs(raw_logs)
        
        assert len(collector.entries) == 3
        assert collector.entries[0].level == "E"
        assert collector.entries[1].level == "W"
        assert collector.entries[2].level == "I"
        
        print("✓ LogCollector _parse_logs test passed")
    
    def test_parse_logs_with_filtering(self):
        """Test _parse_logs with level filtering."""
        collector = LogCollector("TEST123", log_filter=["E"])
        
        raw_logs = """
01-02 12:34:56.789  12345  54321 E AndroidRuntime: Error
01-02 12:34:57.123  12346  54322 W ActivityManager: Warning
01-02 12:34:58.456  12347  54323 I System.out: Info
"""
        
        collector._parse_logs(raw_logs)
        
        # Should only collect error logs
        assert len(collector.entries) == 1
        assert collector.entries[0].level == "E"
        
        print("✓ LogCollector _parse_logs with filtering test passed")
    
    def test_get_entries(self):
        """Test get_entries method."""
        collector = LogCollector("TEST123")
        
        entry1 = LogEntry(
            timestamp="01-02 12:34:56.789",
            pid=12345,
            tid=54321,
            level="E",
            tag="AndroidRuntime",
            message="Error",
            package="com.example.app"
        )
        
        entry2 = LogEntry(
            timestamp="01-02 12:34:57.789",
            pid=12345,
            tid=54321,
            level="W",
            tag="ActivityManager",
            message="Warning",
            package="com.example.app"
        )
        
        collector.entries = [entry1, entry2]
        
        # Get all entries
        all_entries = collector.get_entries()
        assert len(all_entries) == 2
        
        # Get error entries
        error_entries = collector.get_entries("E")
        assert len(error_entries) == 1
        assert error_entries[0].level == "E"
        
        print("✓ LogCollector get_entries test passed")
    
    def test_get_errors(self):
        """Test get_errors method."""
        collector = LogCollector("TEST123")
        
        entry1 = LogEntry(
            timestamp="01-02 12:34:56.789",
            pid=12345,
            tid=54321,
            level="E",
            tag="AndroidRuntime",
            message="Error",
            package="com.example.app"
        )
        
        entry2 = LogEntry(
            timestamp="01-02 12:34:57.789",
            pid=12345,
            tid=54321,
            level="F",
            tag="AndroidRuntime",
            message="Fatal",
            package="com.example.app"
        )
        
        entry3 = LogEntry(
            timestamp="01-02 12:34:58.789",
            pid=12345,
            tid=54321,
            level="W",
            tag="ActivityManager",
            message="Warning",
            package="com.example.app"
        )
        
        collector.entries = [entry1, entry2, entry3]
        
        errors = collector.get_errors()
        assert len(errors) == 2
        
        print("✓ LogCollector get_errors test passed")
    
    def test_get_warnings(self):
        """Test get_warnings method."""
        collector = LogCollector("TEST123")
        
        entry1 = LogEntry(
            timestamp="01-02 12:34:56.789",
            pid=12345,
            tid=54321,
            level="W",
            tag="ActivityManager",
            message="Warning",
            package="com.example.app"
        )
        
        entry2 = LogEntry(
            timestamp="01-02 12:34:57.789",
            pid=12345,
            tid=54321,
            level="E",
            tag="AndroidRuntime",
            message="Error",
            package="com.example.app"
        )
        
        collector.entries = [entry1, entry2]
        
        warnings = collector.get_warnings()
        assert len(warnings) == 1
        assert warnings[0].level == "W"
        
        print("✓ LogCollector get_warnings test passed")
    
    def test_analyze_logs(self):
        """Test analyze_logs method."""
        collector = LogCollector("TEST123")
        
        entry1 = LogEntry(
            timestamp="01-02 12:34:56.789",
            pid=12345,
            tid=54321,
            level="E",
            tag="AndroidRuntime",
            message="Error",
            package="com.example.app"
        )
        
        entry2 = LogEntry(
            timestamp="01-02 12:34:57.789",
            pid=12345,
            tid=54321,
            level="W",
            tag="ActivityManager",
            message="Warning",
            package="com.example.app"
        )
        
        entry3 = LogEntry(
            timestamp="01-02 12:34:58.789",
            pid=12345,
            tid=54321,
            level="E",
            tag="System",
            message="Another error",
            package="com.example.app"
        )
        
        collector.entries = [entry1, entry2, entry3]
        
        stats = collector.analyze_logs()
        
        assert stats["total"] == 3
        assert stats["by_level"]["E"] == 2
        assert stats["by_level"]["W"] == 1
        assert len(stats["by_tag"]) == 3
        assert len(stats["errors"]) == 2
        assert len(stats["warnings"]) == 1
        
        print("✓ LogCollector analyze_logs test passed")
    
    def test_extract_package(self):
        """Test _extract_package method."""
        collector = LogCollector("TEST123")
        
        # Test with package in message
        message1 = "Starting com.example.app"
        package1 = collector._extract_package(message1)
        assert package1 == "com.example.app"
        
        # Test with nested package
        message2 = "Process com.example.app.service"
        package2 = collector._extract_package(message2)
        assert package2 == "com.example.app.service"
        
        # Test without package
        message3 = "No package here"
        package3 = collector._extract_package(message3)
        assert package3 is None
        
        print("✓ LogCollector _extract_package test passed")


def run_all_tests():
    """Run all Phase 4 unit tests."""
    print("\n" + "="*60)
    print("  Phase 4: Log Collector Tests")
    print("="*60 + "\n")
    
    print("Testing LogEntry...")
    test_log_entry = TestLogEntry()
    test_log_entry.test_creation()
    test_log_entry.test_to_dict()
    test_log_entry.test_is_error()
    test_log_entry.test_is_warning()
    print()
    
    print("Testing LogCollectionResult...")
    test_log_collection_result = TestLogCollectionResult()
    test_log_collection_result.test_creation()
    test_log_collection_result.test_creation_with_values()
    test_log_collection_result.test_to_dict()
    print()
    
    print("Testing LogCollector...")
    test_log_collector = TestLogCollector()
    test_log_collector.test_initialization()
    test_log_collector.test_initialization_with_filters()
    test_log_collector.test_parse_logs()
    test_log_collector.test_parse_logs_with_filtering()
    test_log_collector.test_get_entries()
    test_log_collector.test_get_errors()
    test_log_collector.test_get_warnings()
    test_log_collector.test_analyze_logs()
    test_log_collector.test_extract_package()
    print()
    
    print("="*60)
    print("  All Phase 4 Tests Passed! ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()