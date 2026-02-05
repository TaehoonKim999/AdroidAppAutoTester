"""
Report Generator Module

Generates test reports in various formats.
Supports text, HTML, and JSON reports.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .platform_utils import get_platform_utils
from .test_engine import TestResult


@dataclass
class ReportData:
    """
    Data container for report generation.
    
    Attributes:
        test_date: Test execution date/time
        device_info: Device information
        total_tests: Total number of tests
        successful_tests: Number of successful tests
        failed_tests: Number of failed tests
        success_rate: Success rate percentage
        total_duration: Total duration in seconds
        test_results: List of individual test results
    """
    test_date: str
    device_info: Optional[str]
    total_tests: int
    successful_tests: int
    failed_tests: int
    success_rate: float
    total_duration: float
    test_results: List[TestResult]
    
    def to_dict(self) -> dict:
        """Convert ReportData to dictionary."""
        return {
            "test_date": self.test_date,
            "device_info": self.device_info,
            "total_tests": self.total_tests,
            "successful_tests": self.successful_tests,
            "failed_tests": self.failed_tests,
            "success_rate": self.success_rate,
            "total_duration": self.total_duration,
            "test_results": [r.to_dict() for r in self.test_results]
        }


class ReportGenerator:
    """
    Generator for test reports in multiple formats.
    
    Supports text, HTML, and JSON report formats.
    
    Attributes:
        platform_utils: PlatformUtils instance
        output_dir: Output directory for reports
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize ReportGenerator.
        
        Args:
            output_dir: Output directory for reports (default: reports/)
        """
        self.platform_utils = get_platform_utils()
        self.output_dir = output_dir or self.platform_utils.get_path("reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(
        self,
        test_results: List[TestResult],
        device_info: Optional[str] = None,
        formats: List[str] = None
    ) -> List[Path]:
        """
        Generate reports in specified formats.
        
        Args:
            test_results: List of test results
            device_info: Device information string
            formats: List of formats to generate ("text", "html", "json")
        
        Returns:
            List of generated report file paths
        """
        if formats is None:
            formats = ["text"]
        
        # Prepare report data
        report_data = self._prepare_report_data(test_results, device_info)
        
        generated_files = []
        
        # Generate reports in specified formats
        for format_type in formats:
            try:
                if format_type == "text":
                    file_path = self.generate_text_report(report_data)
                elif format_type == "html":
                    file_path = self.generate_html_report(report_data)
                elif format_type == "json":
                    file_path = self.generate_json_report(report_data)
                else:
                    print(f"[WARNING] Unknown format: {format_type}")
                    continue
                
                if file_path:
                    generated_files.append(file_path)
                    print(f"[OK] Generated {format_type.upper()} report: {file_path}")
            
            except Exception as e:
                print(f"[ERROR] Failed to generate {format_type} report: {e}")
        
        return generated_files
    
    def generate_text_report(self, report_data: ReportData) -> Optional[Path]:
        """
        Generate text format report.
        
        Args:
            report_data: Report data
        
        Returns:
            Path to generated report or None if failed
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.txt"
        file_path = self.output_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Header
                f.write("="*80 + "\n")
                f.write("                    ANDROID APP AUTOMATIC TEST REPORT\n")
                f.write("="*80 + "\n\n")
                
                # Summary
                f.write("SUMMARY\n")
                f.write("-"*80 + "\n")
                f.write(f"Test Date:     {report_data.test_date}\n")
                if report_data.device_info:
                    f.write(f"Device:        {report_data.device_info}\n")
                f.write(f"Total Tests:   {report_data.total_tests}\n")
                f.write(f"Successful:    {report_data.successful_tests} ✅\n")
                f.write(f"Failed:        {report_data.failed_tests} ❌\n")
                f.write(f"Success Rate:  {report_data.success_rate:.1f}%\n")
                f.write(f"Duration:      {report_data.total_duration:.2f}s\n")
                f.write("\n")
                
                # Test Results
                f.write("TEST RESULTS\n")
                f.write("-"*80 + "\n")
                
                for i, result in enumerate(report_data.test_results, 1):
                    f.write(f"\n{i}. {result.app_name}\n")
                    f.write(f"   Package:    {result.package}\n")
                    f.write(f"   Status:     {'✅ PASS' if result.success else '❌ FAIL'}\n")
                    f.write(f"   Duration:   {result.duration:.2f}s\n")
                    f.write(f"   Screens:    {result.screens_visited}\n")
                    f.write(f"   Elements:   {result.elements_interacted}\n")
                    f.write(f"   Actions:    {len(result.actions_performed)}\n")
                    
                    if result.errors_found:
                        f.write(f"   Errors:     {len(result.errors_found)}\n")
                        for error in result.errors_found[:3]:
                            f.write(f"              - {error}\n")
                    
                    if result.error_message:
                        f.write(f"   Message:    {result.error_message}\n")
                
                # Footer
                f.write("\n" + "="*80 + "\n")
                f.write("                          END OF REPORT\n")
                f.write("="*80 + "\n")
            
            return file_path
            
        except Exception as e:
            print(f"[ERROR] Failed to generate text report: {e}")
            return None
    
    def generate_html_report(self, report_data: ReportData) -> Optional[Path]:
        """
        Generate HTML format report.
        
        Args:
            report_data: Report data
        
        Returns:
            Path to generated report or None if failed
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.html"
        file_path = self.output_dir / filename
        
        html_content = self._generate_html_content(report_data)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return file_path
            
        except Exception as e:
            print(f"[ERROR] Failed to generate HTML report: {e}")
            return None
    
    def generate_json_report(self, report_data: ReportData) -> Optional[Path]:
        """
        Generate JSON format report.
        
        Args:
            report_data: Report data
        
        Returns:
            Path to generated report or None if failed
        """
        try:
            import json
        except ImportError:
            print("[ERROR] json module not available")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.json"
        file_path = self.output_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data.to_dict(), f, indent=2)
            
            return file_path
            
        except Exception as e:
            print(f"[ERROR] Failed to generate JSON report: {e}")
            return None
    
    def _prepare_report_data(
        self,
        test_results: List[TestResult],
        device_info: Optional[str]
    ) -> ReportData:
        """
        Prepare report data from test results.
        
        Args:
            test_results: List of test results
            device_info: Device information
        
        Returns:
            ReportData object
        """
        total_tests = len(test_results)
        successful_tests = sum(1 for r in test_results if r.success)
        failed_tests = total_tests - successful_tests
        
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0.0
        total_duration = sum(r.duration for r in test_results)
        
        return ReportData(
            test_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            device_info=device_info,
            total_tests=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            success_rate=success_rate,
            total_duration=total_duration,
            test_results=test_results
        )
    
    def _generate_html_content(self, report_data: ReportData) -> str:
        """
        Generate HTML content for report.
        
        Args:
            report_data: Report data
        
        Returns:
            HTML string
        """
        success_color = "#4CAF50"  # Green
        fail_color = "#F44336"    # Red
        warning_color = "#FF9800"  # Orange
        
        # Build test results HTML
        results_html = ""
        for result in report_data.test_results:
            status_color = success_color if result.success else fail_color
            status_icon = "✅" if result.success else "❌"
            
            results_html += f"""
            <div class="test-result">
                <div class="result-header">
                    <h3>{result.app_name}</h3>
                    <span class="status {'pass' if result.success else 'fail'}">{status_icon}</span>
                </div>
                <div class="result-details">
                    <div class="detail-row">
                        <span class="label">Package:</span>
                        <span class="value">{result.package}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Status:</span>
                        <span class="value {'pass' if result.success else 'fail'}">
                            {'PASS' if result.success else 'FAIL'}
                        </span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Duration:</span>
                        <span class="value">{result.duration:.2f}s</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Screens:</span>
                        <span class="value">{result.screens_visited}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Elements:</span>
                        <span class="value">{result.elements_interacted}</span>
                    </div>
                    <div class="detail-row">
                        <span class="label">Actions:</span>
                        <span class="value">{len(result.actions_performed)}</span>
                    </div>
            """
            
            if result.errors_found:
                results_html += f"""
                    <div class="detail-row">
                        <span class="label">Errors ({len(result.errors_found)}):</span>
                    </div>
                    <div class="errors-list">
                """
                for error in result.errors_found[:5]:
                    results_html += f"<div class='error-item'>{error}</div>"
                if len(result.errors_found) > 5:
                    results_html += f"<div class='error-item'>... and {len(result.errors_found) - 5} more</div>"
                results_html += "</div>"
            
            if result.error_message:
                results_html += f"""
                    <div class="detail-row">
                        <span class="label">Message:</span>
                        <span class="value error-message">{result.error_message}</span>
                    </div>
            """
            
            results_html += "</div></div>"
        
        # Build complete HTML
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Report - {report_data.test_date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .summary {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .summary h2 {{
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .summary-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .summary-card .label {{
            color: #666;
            font-size: 0.9em;
        }}
        .test-result {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid {success_color};
        }}
        .test-result.fail {{
            border-left-color: {fail_color};
        }}
        .result-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .result-header h3 {{
            color: #333;
        }}
        .status {{
            font-size: 1.5em;
        }}
        .result-details {{
            margin-top: 15px;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .detail-row:last-child {{
            border-bottom: none;
        }}
        .label {{
            font-weight: 600;
            color: #666;
        }}
        .value {{
            color: #333;
        }}
        .value.pass {{
            color: {success_color};
            font-weight: bold;
        }}
        .value.fail {{
            color: {fail_color};
            font-weight: bold;
        }}
        .errors-list {{
            background: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
        }}
        .error-item {{
            color: #856404;
            padding: 5px 0;
            padding-left: 20px;
            position: relative;
        }}
        .error-item:before {{
            content: "•";
            position: absolute;
            left: 5px;
        }}
        .error-message {{
            color: {fail_color};
            font-weight: 600;
        }}
        footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📱 Android App Automatic Test Report</h1>
            <p>Generated on {report_data.test_date}</p>
        </header>
        
        <div class="summary">
            <h2>📊 Summary</h2>
            {f'<p><strong>Device:</strong> {report_data.device_info}</p>' if report_data.device_info else ''}
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="value">{report_data.total_tests}</div>
                    <div class="label">Total Tests</div>
                </div>
                <div class="summary-card">
                    <div class="value" style="color: {success_color}">{report_data.successful_tests}</div>
                    <div class="label">Successful ✅</div>
                </div>
                <div class="summary-card">
                    <div class="value" style="color: {fail_color}">{report_data.failed_tests}</div>
                    <div class="label">Failed ❌</div>
                </div>
                <div class="summary-card">
                    <div class="value">{report_data.success_rate:.1f}%</div>
                    <div class="label">Success Rate</div>
                </div>
                <div class="summary-card">
                    <div class="value">{report_data.total_duration:.0f}s</div>
                    <div class="label">Duration</div>
                </div>
            </div>
        </div>
        
        <div class="test-results">
            <h2 style="color: #667eea; margin-bottom: 20px;">📋 Test Results</h2>
            {results_html}
        </div>
        
        <footer>
            <p>Generated by Android App Auto Tester</p>
        </footer>
    </div>
</body>
</html>
"""
        return html


def get_report_generator(output_dir: Optional[Path] = None) -> ReportGenerator:
    """
    Get a ReportGenerator instance.
    
    Args:
        output_dir: Output directory for reports
    
    Returns:
        ReportGenerator instance
    """
    return ReportGenerator(output_dir)