"""
Test Engine Module

Coordinates entire testing workflow.
Integrates device management, UI exploration, and log collection.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .config_manager import AppConfig, GlobalSettings
from .device_manager import DeviceManager, DeviceInfo
from .log_collector import LogCollector, LogCollectionResult
from .platform_utils import get_platform_utils
from .ui_explorer import UIExplorer, ExplorationResult


@dataclass
class TestResult:
    """
    Result of a single app test.
    
    Attributes:
        app_name: App name that was tested
        package: Package name
        success: Whether test completed successfully
        duration: Test duration in seconds
        screens_visited: Number of screens visited
        elements_interacted: Number of elements interacted with
        actions_performed: List of actions performed
        errors_found: List of errors detected
        log_file: Path to log file
        screenshot_files: List of screenshot files taken
        retry_count: Number of retries performed
        error_message: Error message if test failed
    """
    app_name: str
    package: str
    success: bool
    duration: float = 0.0
    screens_visited: int = 0
    elements_interacted: int = 0
    actions_performed: List[str] = field(default_factory=list)
    errors_found: List[str] = field(default_factory=list)
    log_file: Optional[Path] = None
    screenshot_files: List[Path] = field(default_factory=list)
    retry_count: int = 0
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert TestResult to dictionary."""
        return {
            "app_name": self.app_name,
            "package": self.package,
            "success": self.success,
            "duration": self.duration,
            "screens_visited": self.screens_visited,
            "elements_interacted": self.elements_interacted,
            "actions_performed": self.actions_performed,
            "errors_found": self.errors_found,
            "log_file": str(self.log_file) if self.log_file else None,
            "screenshot_files": [str(f) for f in self.screenshot_files],
            "retry_count": self.retry_count,
            "error_message": self.error_message
        }


class TestEngine:
    """
    Engine for running automated app tests.
    
    Coordinates device connection, app launch, UI exploration,
    and log collection.
    
    Attributes:
        device_manager: DeviceManager instance
        ui_explorer: UIExplorer instance
        log_collector: LogCollector instance
        platform_utils: PlatformUtils instance
        settings: Global settings
    """
    
    def __init__(
        self,
        device_manager: DeviceManager,
        settings: GlobalSettings
    ):
        """
        Initialize TestEngine.
        
        Args:
            device_manager: DeviceManager instance
            settings: Global settings
        """
        self.device_manager = device_manager
        self.settings = settings
        self.platform_utils = get_platform_utils()
        
        # Initialize dependent components
        self.ui_explorer: Optional[UIExplorer] = None
        self.log_collector: Optional[LogCollector] = None
    
    def run_test(self, app_config: AppConfig) -> TestResult:
        """
        Run a test for a single app.
        
        Args:
            app_config: App configuration to test
        
        Returns:
            TestResult: Test result
        """
        print(f"\n{'='*60}")
        print(f"Testing: {app_config.name}")
        print(f"Package: {app_config.package}")
        print(f"Activity: {app_config.activity}")
        print(f"Duration: {app_config.test_duration}s")
        print(f"Actions: {', '.join(app_config.test_actions)}")
        print(f"{'='*60}\n")
        
        result = TestResult(
            app_name=app_config.name,
            package=app_config.package,
            success=False
        )
        
        # Start timer
        start_time = time.time()
        
        try:
            # Retry logic
            for attempt in range(self.settings.max_test_retries + 1):
                result.retry_count = attempt
                
                if attempt > 0:
                    print(f"\n[INFO] Retry attempt {attempt}/{self.settings.max_test_retries}")
                    time.sleep(2)  # Wait before retry
                
                # Run the test
                test_success = self._run_test_attempt(
                    app_config,
                    result,
                    start_time
                )
                
                if test_success:
                    result.success = True
                    break
                
                # Take screenshot on error
                if self.settings.screenshot_on_error:
                    screenshot = self._take_error_screenshot(app_config.name, attempt)
                    if screenshot:
                        result.screenshot_files.append(screenshot)
        
        except Exception as e:
            print(f"[ERROR] Test execution failed: {e}")
            import traceback
            traceback.print_exc()
            result.success = False
            result.error_message = str(e)
            
            # Take screenshot on error
            if self.settings.screenshot_on_error:
                screenshot = self._take_error_screenshot(app_config.name, result.retry_count)
                if screenshot:
                    result.screenshot_files.append(screenshot)
        
        # Calculate duration
        result.duration = time.time() - start_time
        
        # Stop app
        try:
            self.device_manager.stop_app(app_config.package)
        except Exception as e:
            print(f"[WARNING] Error stopping app: {e}")
        
        # Print result summary
        self._print_test_summary(result)
        
        return result
    
    def run_all_tests(self, app_configs: List[AppConfig]) -> List[TestResult]:
        """
        Run tests for all configured apps.
        
        Args:
            app_configs: List of app configurations to test
        
        Returns:
            List of TestResult objects
        """
        results = []
        
        print(f"\n{'='*60}")
        print(f"Starting test run for {len(app_configs)} app(s)")
        print(f"{'='*60}\n")
        
        for i, app_config in enumerate(app_configs, 1):
            print(f"\n[INFO] Test {i}/{len(app_configs)}")
            
            result = self.run_test(app_config)
            results.append(result)
            
            # Delay between apps
            if i < len(app_configs):
                print(f"\n[INFO] Waiting {self.settings.delay_between_apps}s before next test...")
                time.sleep(self.settings.delay_between_apps)
        
        # Print overall summary
        self._print_overall_summary(results)
        
        return results
    
    def _run_test_attempt(
        self,
        app_config: AppConfig,
        result: TestResult,
        start_time: float
    ) -> bool:
        """
        Run a single test attempt.
        
        Args:
            app_config: App configuration
            result: Test result to populate
            start_time: Test start time
        
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"[INFO] Starting test attempt for {app_config.name}")
        
        # Start app
        if not self.device_manager.start_app(app_config.package, app_config.activity):
            result.error_message = "Failed to start app"
            print(f"[ERROR] Failed to start app {app_config.package}")
            return False
        
        print(f"[INFO] App started successfully")
        
        # Initialize components
        self._initialize_components(app_config)
        
        # Start log collection (async)
        try:
            if self.settings.collect_logcat and self.log_collector:
                print(f"[INFO] Starting log collection")
                self.log_collector.start_collection(app_config.test_duration)
        except Exception as e:
            print(f"[WARNING] Failed to start log collection: {e}")
        
        # Start UI exploration (blocks for duration)
        exploration_result = None
        if self.ui_explorer:
            try:
                print(f"[INFO] Starting UI exploration for {app_config.name}")
                print(f"[INFO] Expected duration: {app_config.test_duration}s")
                
                exploration_start = time.time()
                exploration_result = self.ui_explorer.explore(
                    app_config.test_duration,
                    app_config.test_actions
                )
                exploration_duration = time.time() - exploration_start
                
                print(f"[INFO] UI exploration completed for {app_config.name}")
                print(f"[INFO] Actual duration: {exploration_duration:.1f}s")
                
                # Update result with exploration data
                result.screens_visited = exploration_result.screens_visited
                result.elements_interacted = exploration_result.elements_interacted
                result.actions_performed = exploration_result.actions_performed
                result.errors_found.extend(exploration_result.errors_found)
            except Exception as e:
                print(f"[ERROR] UI exploration failed: {e}")
                import traceback
                traceback.print_exc()
                result.error_message = f"Exploration error: {e}"
                result.errors_found.append(f"Exploration failed: {e}")
                # Still continue to stop log collection
                exploration_result = None
        else:
            print(f"[WARNING] UI explorer not initialized")
            result.error_message = "UI explorer not initialized"
        
        # Stop log collection and get result
        log_result = None
        try:
            if self.settings.collect_logcat and self.log_collector:
                print(f"[INFO] Stopping log collection")
                log_result = self.log_collector.stop_collection()
                result.log_file = log_result.log_file
                # Add log errors if any
                if log_result.error_count > 0:
                    result.errors_found.append(f"Logcat errors: {log_result.error_count}")
        except Exception as e:
            print(f"[WARNING] Failed to stop log collection: {e}")
        
        # Take final screenshot only if errors found
        if exploration_result and exploration_result.errors_found:
            screenshot = self._take_screenshot(f"{app_config.name}_final")
            if screenshot:
                result.screenshot_files.append(screenshot)
        
        # Check for errors
        if exploration_result and exploration_result.errors_found:
            result.error_message = f"Errors found during exploration: {len(exploration_result.errors_found)}"
            return False
        
        return True
    
    def _initialize_components(self, app_config: AppConfig) -> None:
        """
        Initialize UI explorer and log collector.
        
        Args:
            app_config: App configuration
        """
        print(f"[INFO] Initializing components for {app_config.name}")
        
        # Initialize UI explorer
        try:
            if self.device_manager.device:
                self.ui_explorer = UIExplorer(self.device_manager.device)
                print(f"[INFO] UI explorer initialized")
            else:
                print(f"[WARNING] Device not available for UI explorer")
                self.ui_explorer = None
        except Exception as e:
            print(f"[WARNING] Failed to initialize UI explorer: {e}")
            self.ui_explorer = None
        
        # Initialize log collector
        try:
            device_info = self.device_manager.get_device_info()
            if device_info:
                self.log_collector = LogCollector(
                    device_info.serial,
                    log_filter=self.settings.logcat_filter,
                    package_filter=app_config.package
                )
                print(f"[INFO] Log collector initialized for {device_info.serial}")
            else:
                print(f"[WARNING] Device info not available for log collector")
                self.log_collector = None
        except Exception as e:
            print(f"[WARNING] Failed to initialize log collector: {e}")
            self.log_collector = None
    
    def _take_screenshot(self, filename: str) -> Optional[Path]:
        """
        Take a screenshot with current timestamp.
        
        Args:
            filename: Base filename (without extension)
        
        Returns:
            Path to screenshot or None if failed
        """
        if not self.device_manager.is_connected():
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            full_filename = f"{filename}_{timestamp}.png"
            
            return self.device_manager.take_screenshot(full_filename)
        except Exception as e:
            print(f"[WARNING] Failed to take screenshot: {e}")
            return None
    
    def _take_error_screenshot(
        self,
        app_name: str,
        attempt: int
    ) -> Optional[Path]:
        """
        Take a screenshot on error.
        
        Args:
            app_name: App name
            attempt: Attempt number
        
        Returns:
            Path to screenshot or None if failed
        """
        filename = f"{app_name}_error_attempt{attempt}"
        return self._take_screenshot(filename)
    
    def _print_test_summary(self, result: TestResult) -> None:
        """Print test result summary."""
        print(f"\n{'='*60}")
        print(f"Test Summary: {result.app_name}")
        print(f"{'='*60}")
        print(f"Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
        print(f"Duration: {result.duration:.2f}s")
        print(f"Retry Count: {result.retry_count}")
        print(f"Screens Visited: {result.screens_visited}")
        print(f"Elements Interacted: {result.elements_interacted}")
        print(f"Actions Performed: {len(result.actions_performed)}")
        
        if result.errors_found:
            print(f"\nErrors Found ({len(result.errors_found)}):")
            for error in result.errors_found[:5]:  # Show first 5
                print(f"  - {error}")
            if len(result.errors_found) > 5:
                print(f"  ... and {len(result.errors_found) - 5} more")
        
        if result.log_file:
            print(f"\nLog File: {result.log_file}")
        
        if result.screenshot_files:
            print(f"\nScreenshots ({len(result.screenshot_files)}):")
            for screenshot in result.screenshot_files:
                print(f"  - {screenshot}")
        
        if result.error_message:
            print(f"\nError: {result.error_message}")
        
        print(f"{'='*60}\n")
    
    def _print_overall_summary(self, results: List[TestResult]) -> None:
        """Print overall test run summary."""
        print(f"\n{'='*60}")
        print(f"Overall Test Summary")
        print(f"{'='*60}")
        
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        
        print(f"Total Tests: {total}")
        print(f"Successful: {successful} ✅")
        print(f"Failed: {failed} ❌")
        
        if total > 0:
            success_rate = (successful / total) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        total_duration = sum(r.duration for r in results)
        print(f"Total Duration: {total_duration:.2f}s")
        
        print(f"\n{'='*60}\n")


def get_test_engine(
    device_manager: DeviceManager,
    settings: GlobalSettings
) -> TestEngine:
    """
    Get a TestEngine instance.
    
    Args:
        device_manager: DeviceManager instance
        settings: Global settings
    
    Returns:
        TestEngine instance
    """
    return TestEngine(device_manager, settings)