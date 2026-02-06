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
from .utils.logger import get_session_logger
from .exceptions import (
    TestError, TestFailedError, UIExplorationError,
    LogCollectionError, DeviceError, ADBError
)


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

        # Initialize logger with session ID
        session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logger = get_session_logger(__name__, session_id=session_id)

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
        self.logger.info("=" * 60)
        self.logger.info(f"Testing: {app_config.name}")
        self.logger.info(f"Package: {app_config.package}")
        self.logger.info(f"Activity: {app_config.activity}")
        self.logger.info(f"Duration: {app_config.test_duration}s")
        self.logger.info(f"Actions: {', '.join(app_config.test_actions)}")
        self.logger.info("=" * 60)
        
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
                    self.logger.info(f"Retry attempt {attempt}/{self.settings.max_test_retries}")
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
        
        except (TestFailedError, DeviceError, Exception) as e:
            self.logger.error(f"Test execution failed: {e}", exc_info=True)
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
        except (ADBError, DeviceError) as e:
            self.logger.warning(f"Error stopping app: {e}")
        
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

        self.logger.info("=" * 60)
        self.logger.info(f"Starting test run for {len(app_configs)} app(s)")
        self.logger.info("=" * 60)

        for i, app_config in enumerate(app_configs, 1):
            
            self.logger.info(f"Running test {i}/{len(app_configs)}: {app_config.name}")

            result = self.run_test(app_config)
            results.append(result)
            
            # Delay between apps
            if i < len(app_configs):
                
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
        
        
        # Start app
        if not self.device_manager.start_app(app_config.package, app_config.activity):
            result.error_message = "Failed to start app"
            
            return False
        
        
        
        # Initialize components
        self._initialize_components(app_config)
        
        # Start log collection (async)
        try:
            if self.settings.collect_logcat and self.log_collector:


                self.log_collector.start_collection(app_config.test_duration)
        except LogCollectionError as e:
            self.logger.warning(f"Failed to start log collection: {e}")

        # Start UI exploration (blocks for duration)
        exploration_result = None
        if self.ui_explorer:
            try:
                self.logger.info(f"Starting UI exploration for {app_config.name}")
                self.logger.info(f"Expected duration: {app_config.test_duration}s")

                exploration_start = time.time()
                exploration_result = self.ui_explorer.explore(
                    app_config.test_duration,
                    app_config.test_actions
                )
                exploration_duration = time.time() - exploration_start

                self.logger.info(f"UI exploration completed for {app_config.name}")
                self.logger.info(f"Actual duration: {exploration_duration:.1f}s")

                # Update result with exploration data
                result.screens_visited = exploration_result.screens_visited
                result.elements_interacted = exploration_result.elements_interacted
                result.actions_performed = exploration_result.actions_performed
                result.errors_found.extend(exploration_result.errors_found)
            except UIExplorationError as e:
                self.logger.error(f"UI exploration failed: {e}", exc_info=True)
                result.error_message = f"Exploration error: {e}"
                result.errors_found.append(f"Exploration failed: {e}")
                # Still continue to stop log collection
                exploration_result = None
        else:
            self.logger.warning("UI explorer not initialized")
            result.error_message = "UI explorer not initialized"
        
        # Stop log collection and get result
        log_result = None
        try:
            if self.settings.collect_logcat and self.log_collector:
                self.logger.info("Stopping log collection")
                log_result = self.log_collector.stop_collection()
                result.log_file = log_result.log_file
                # Add log errors if any
                if log_result.error_count > 0:
                    result.errors_found.append(f"Logcat errors: {log_result.error_count}")
        except LogCollectionError as e:
            self.logger.warning(f"Failed to stop log collection: {e}")
        
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
        
        
        # Initialize UI explorer
        try:
            if self.device_manager.device:
                self.ui_explorer = UIExplorer(self.device_manager.device)

            else:

                self.ui_explorer = None
        except (UIExplorationError, DeviceError) as e:

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

            else:

                self.log_collector = None
        except LogCollectionError as e:

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
        except (DeviceError, ADBError) as e:

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
        self.logger.info("=" * 60)
        self.logger.info(f"Test Summary: {result.app_name}")
        self.logger.info("=" * 60)
        self.logger.info(f"Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
        self.logger.info(f"Duration: {result.duration:.2f}s")
        self.logger.info(f"Retry Count: {result.retry_count}")
        self.logger.info(f"Screens Visited: {result.screens_visited}")
        self.logger.info(f"Elements Interacted: {result.elements_interacted}")
        self.logger.info(f"Actions Performed: {len(result.actions_performed)}")
        
        if result.errors_found:
            self.logger.info(f"Errors Found ({len(result.errors_found)}):")
            for error in result.errors_found[:5]:  # Show first 5
                self.logger.info(f"  - {error}")
            if len(result.errors_found) > 5:
                self.logger.info(f"  ... and {len(result.errors_found) - 5} more")
        
        if result.log_file:
            self.logger.info(f"Log File: {result.log_file}")
        
        if result.screenshot_files:
            self.logger.info(f"Screenshots ({len(result.screenshot_files)}):")
            for screenshot in result.screenshot_files:
                self.logger.info(f"  - {screenshot}")
        
        if result.error_message:
            self.logger.info(f"Error: {result.error_message}")

        self.logger.info("=" * 60)
    
    def _print_overall_summary(self, results: List[TestResult]) -> None:
        """Print overall test run summary."""
        self.logger.info("=" * 60)
        self.logger.info("Overall Test Summary")
        self.logger.info("=" * 60)
        
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        
        self.logger.info(f"Total Tests: {total}")
        self.logger.info(f"Successful: {successful} ✅")
        self.logger.info(f"Failed: {failed} ❌")
        
        if total > 0:
            success_rate = (successful / total) * 100
            self.logger.info(f"Success Rate: {success_rate:.1f}%")
        
        total_duration = sum(r.duration for r in results)
        self.logger.info(f"Total Duration: {total_duration:.2f}s")

        self.logger.info("=" * 60)


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