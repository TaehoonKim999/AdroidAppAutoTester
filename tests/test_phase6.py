"""
Unit Tests for Phase 6: Report Generator

Tests:
- ReportData dataclass
- ReportGenerator class
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Mock uiautomator2 before importing src modules
sys.modules['uiautomator2'] = Mock()

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.report_generator import ReportData, ReportGenerator
from src.test_engine import TestResult


class TestReportData:
    """Test cases for ReportData dataclass."""
    
    def test_creation(self):
        """Test ReportData creation with valid data."""
        test_results = [
            TestResult(
                app_name="App 1",
                package="com.example.app1",
                success=True,
                duration=30.0
            ),
            TestResult(
                app_name="App 2",
                package="com.example.app2",
                success=False,
                duration=45.0,
                error_message="Test error"
            )
        ]
        
        report_data = ReportData(
            test_date="2024-01-01 12:00:00",
            device_info="Samsung Galaxy S21",
            total_tests=2,
            successful_tests=1,
            failed_tests=1,
            success_rate=50.0,
            total_duration=75.0,
            test_results=test_results
        )
        
        assert report_data.test_date == "2024-01-01 12:00:00"
        assert report_data.device_info == "Samsung Galaxy S21"
        assert report_data.total_tests == 2
        assert report_data.successful_tests == 1
        assert report_data.success_rate == 50.0
        
        print("✓ ReportData creation test passed")
    
    def test_to_dict(self):
        """Test ReportData to_dict conversion."""
        test_results = [
            TestResult(
                app_name="App 1",
                package="com.example.app1",
                success=True,
                duration=30.0
            )
        ]
        
        report_data = ReportData(
            test_date="2024-01-01 12:00:00",
            device_info="Samsung Galaxy S21",
            total_tests=1,
            successful_tests=1,
            failed_tests=0,
            success_rate=100.0,
            total_duration=30.0,
            test_results=test_results
        )
        
        data = report_data.to_dict()
        assert isinstance(data, dict)
        assert data["test_date"] == "2024-01-01 12:00:00"
        assert data["total_tests"] == 1
        assert isinstance(data["test_results"], list)
        assert len(data["test_results"]) == 1
        
        print("✓ ReportData to_dict test passed")


class TestReportGenerator:
    """Test cases for ReportGenerator class."""
    
    def test_initialization(self):
        """Test ReportGenerator initialization."""
        temp_dir = Path("/tmp/test_reports")
        generator = ReportGenerator(temp_dir)
        
        assert generator.output_dir == temp_dir
        
        print("✓ ReportGenerator initialization test passed")
    
    def test_generate_text_report(self):
        """Test generate_text_report method."""
        # Use a temporary directory
        temp_dir = Path("/tmp/test_reports_gen")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            generator = ReportGenerator(temp_dir)
            
            test_results = [
                TestResult(
                    app_name="Test App",
                    package="com.example.test",
                    success=True,
                    duration=30.0,
                    screens_visited=5,
                    elements_interacted=20,
                    actions_performed=["Click: OK"],
                    errors_found=[]
                )
            ]
            
            report_data = generator._prepare_report_data(test_results, "Test Device")
            file_path = generator.generate_text_report(report_data)
            
            assert file_path is not None
            assert file_path.exists()
            assert file_path.suffix == ".txt"
            
            # Check file content
            content = file_path.read_text(encoding='utf-8')
            assert "ANDROID APP AUTOMATIC TEST REPORT" in content
            assert "Test App" in content
            assert "com.example.test" in content
            
            print("✓ ReportGenerator generate_text_report test passed")
        
        finally:
            # Clean up
            if file_path and file_path.exists():
                file_path.unlink()
    
    def test_generate_html_report(self):
        """Test generate_html_report method."""
        temp_dir = Path("/tmp/test_reports_html")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            generator = ReportGenerator(temp_dir)
            
            test_results = [
                TestResult(
                    app_name="Test App",
                    package="com.example.test",
                    success=True,
                    duration=30.0,
                    screens_visited=5,
                    elements_interacted=20,
                    actions_performed=["Click: OK"],
                    errors_found=[]
                )
            ]
            
            report_data = generator._prepare_report_data(test_results, "Test Device")
            file_path = generator.generate_html_report(report_data)
            
            assert file_path is not None
            assert file_path.exists()
            assert file_path.suffix == ".html"
            
            # Check file content
            content = file_path.read_text(encoding='utf-8')
            assert "<!DOCTYPE html>" in content
            assert "Test App" in content
            assert "com.example.test" in content
            assert "Summary" in content
            
            print("✓ ReportGenerator generate_html_report test passed")
        
        finally:
            # Clean up
            if file_path and file_path.exists():
                file_path.unlink()
    
    def test_generate_json_report(self):
        """Test generate_json_report method."""
        temp_dir = Path("/tmp/test_reports_json")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            generator = ReportGenerator(temp_dir)
            
            test_results = [
                TestResult(
                    app_name="Test App",
                    package="com.example.test",
                    success=True,
                    duration=30.0
                )
            ]
            
            report_data = generator._prepare_report_data(test_results, "Test Device")
            file_path = generator.generate_json_report(report_data)
            
            assert file_path is not None
            assert file_path.exists()
            assert file_path.suffix == ".json"
            
            # Check file content
            import json
            content = json.loads(file_path.read_text(encoding='utf-8'))
            assert "test_date" in content
            assert "test_results" in content
            assert len(content["test_results"]) == 1
            
            print("✓ ReportGenerator generate_json_report test passed")
        
        finally:
            # Clean up
            if file_path and file_path.exists():
                file_path.unlink()
    
    def test_prepare_report_data(self):
        """Test _prepare_report_data method."""
        generator = ReportGenerator(Path("/tmp"))
        
        test_results = [
            TestResult(
                app_name="App 1",
                package="com.example.app1",
                success=True,
                duration=30.0
            ),
            TestResult(
                app_name="App 2",
                package="com.example.app2",
                success=False,
                duration=45.0,
                error_message="Test error"
            )
        ]
        
        report_data = generator._prepare_report_data(test_results, "Test Device")
        
        assert report_data.total_tests == 2
        assert report_data.successful_tests == 1
        assert report_data.failed_tests == 1
        assert report_data.success_rate == 50.0
        assert report_data.total_duration == 75.0
        assert report_data.device_info == "Test Device"
        assert len(report_data.test_results) == 2
        
        print("✓ ReportGenerator _prepare_report_data test passed")
    
    def test_generate_report_multiple_formats(self):
        """Test generate_report with multiple formats."""
        temp_dir = Path("/tmp/test_reports_multi")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            generator = ReportGenerator(temp_dir)
            
            test_results = [
                TestResult(
                    app_name="Test App",
                    package="com.example.test",
                    success=True,
                    duration=30.0
                )
            ]
            
            generated_files = generator.generate_report(
                test_results,
                device_info="Test Device",
                formats=["text", "html", "json"]
            )
            
            assert len(generated_files) == 3
            
            # Check all files exist
            file_types = {}
            for file_path in generated_files:
                assert file_path.exists()
                file_types[file_path.suffix] = file_path
            
            assert ".txt" in file_types
            assert ".html" in file_types
            assert ".json" in file_types
            
            print("✓ ReportGenerator generate_report multiple formats test passed")
        
        finally:
            # Clean up
            for file_path in generated_files:
                if file_path.exists():
                    file_path.unlink()
    
    def test_generate_html_content(self):
        """Test _generate_html_content method."""
        generator = ReportGenerator(Path("/tmp"))
        
        test_results = [
            TestResult(
                app_name="Test App",
                package="com.example.test",
                success=True,
                duration=30.0,
                screens_visited=5,
                elements_interacted=20,
                actions_performed=["Click: OK"],
                errors_found=[]
            )
        ]
        
        report_data = generator._prepare_report_data(test_results, "Test Device")
        html_content = generator._generate_html_content(report_data)
        
        assert isinstance(html_content, str)
        assert "<!DOCTYPE html>" in html_content
        assert "Test App" in html_content
        assert "Summary" in html_content
        assert "100.0%" in html_content  # success rate
        assert "30.00s" in html_content  # duration
        
        print("✓ ReportGenerator _generate_html_content test passed")


def run_all_tests():
    """Run all Phase 6 unit tests."""
    print("\n" + "="*60)
    print("  Phase 6: Report Generator Tests")
    print("="*60 + "\n")
    
    print("Testing ReportData...")
    test_report_data = TestReportData()
    test_report_data.test_creation()
    test_report_data.test_to_dict()
    print()
    
    print("Testing ReportGenerator...")
    test_report_generator = TestReportGenerator()
    test_report_generator.test_initialization()
    test_report_generator.test_generate_text_report()
    test_report_generator.test_generate_html_report()
    test_report_generator.test_generate_json_report()
    test_report_generator.test_prepare_report_data()
    test_report_generator.test_generate_report_multiple_formats()
    test_report_generator.test_generate_html_content()
    print()
    
    print("="*60)
    print("  All Phase 6 Tests Passed! ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()