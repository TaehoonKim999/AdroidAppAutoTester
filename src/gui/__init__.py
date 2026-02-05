"""
GUI Module for Android App Auto Tester

Provides graphical user interface using customtkinter.
"""

import sys
import tkinter
from .main_window import MainWindow
from .devices_view import DevicesView
from .apps_view import AppsView
from .config_view import ConfigView
from .test_view import TestView
from .report_view import ReportView

__all__ = [
    'MainWindow',
    'DevicesView',
    'AppsView',
    'ConfigView',
    'TestView',
    'ReportView',
    'run_gui'
]


def run_gui():
    """Run GUI application."""
    app = MainWindow()
    app.mainloop()