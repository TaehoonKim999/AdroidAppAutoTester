# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Android App Auto Tester - automated UI testing system for Android apps via USB connection. Uses uiautomator2 for UI automation and ADB for device communication. Supports both CLI and GUI (customtkinter) interfaces.

## Common Commands

```bash
# Run GUI (recommended for interactive use)
python -m src.main --gui
python -m src.main -g

# Run CLI
python -m src.main                              # Show help
python -m src.main list                         # List connected devices
python -m src.main list --apps                  # List configured apps
python -m src.main run                          # Run all tests
python -m src.main run --app com.example.app    # Test specific app
python -m src.main config --get test_duration   # View config value
python -m src.main config --set test_duration 60

# Run tests
pytest tests/                   # All tests
python tests/test_phase1.py     # Run specific phase
pytest --cov=src tests/         # With coverage

# Setup (first time)
./setup_ubuntu.sh      # Ubuntu
setup_windows.bat      # Windows
```

## Architecture

Entry points:
- [src/main.py](src/main.py) - CLI interface, routes to GUI via `--gui` flag

Core modules (all use `get_*()` factory functions):
- [config_manager.py](src/config_manager.py) - Loads/saves `config/apps.json` and `config/settings.json`
- [device_manager.py](src/device_manager.py) - ADB/uiautomator2 device connection
- [test_engine.py](src/test_engine.py) - Orchestrates test runs, coordinates other modules
- [ui_explorer.py](src/ui_explorer.py) - Automated UI exploration (click, scroll, input)
- [log_collector.py](src/log_collector.py) - Logcat collection and error detection
- [report_generator.py](src/report_generator.py) - Generates text/HTML/JSON reports

GUI modules ([src/gui/](src/gui/)):
- `MainWindow` - Tab-based main window
- Views: `DevicesView`, `AppsView`, `ConfigView`, `TestView`, `ReportView`

Platform abstraction:
- [platform_utils.py](src/platform_utils.py) - OS-specific paths, ADB commands (Windows/Ubuntu)

## Key Data Structures

```python
# Config - src/config_manager.py
AppConfig(name, package, activity, test_duration, test_actions)
GlobalSettings(screenshot_on_error, collect_logcat, logcat_filter, max_test_retries, ...)

# Results - src/test_engine.py
TestResult(app_name, package, success, duration, screens_visited, errors_found, ...)
```

## Test Organization

Tests are split by development phase in `tests/`:
- Phase 1: Platform utils, config manager
- Phase 2: Device manager
- Phase 3: UI explorer
- Phase 4: Log collector
- Phase 5: Test engine
- Phase 6: Report generator
- Phase 7: GUI

Each test file has a `run_all_tests()` function and can run standalone.

## Configuration Files

- `config/apps.json` - List of apps to test (package, activity, duration)
- `config/settings.json` - Global settings (screenshot, logcat, retries)
- Sample files: `config/*.json.sample`

## Notes

- GUI uses customtkinter (modern tkinter wrapper)
- Device connection requires USB debugging enabled and ADB authorization
- Screenshots saved to `screenshots/`, logs to `logs/`, reports to `reports/`
