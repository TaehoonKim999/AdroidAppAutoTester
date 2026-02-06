"""
Report View for GUI

Displays test reports.
"""

import customtkinter as ctk
from pathlib import Path
from typing import Optional
import webbrowser

from .base_view import BaseView


class ReportView(BaseView):
    """
    View for displaying test reports.

    Allows viewing and opening generated reports.

    Attributes:
        main_window: Reference to main window
        reports_dir: Reports directory path
    """

    def _setup_state(self):
        """Initialize report view state."""
        self.reports_dir = Path("reports")

    def _build_ui(self):
        """Build report view UI."""
        # Title
        self._build_title("Test Reports")
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Refresh",
            command=self._load_reports,
            width=120
        )
        refresh_btn.pack(side="left", padx=5, pady=10)
        
        # Delete All button
        delete_all_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑 Delete All Reports",
            command=self._delete_all_reports,
            width=160,
            fg_color="#DC3545",
            hover_color="#BB2D3B"
        )
        delete_all_btn.pack(side="right", padx=5, pady=10)
        
        # Reports list
        self.reports_frame = self._build_scrollable_frame(height=450)

    def _load_data(self):
        """Load reports after UI is built."""
        self._load_reports()

    def _load_reports(self):
        """Load and display test reports."""
        # Clear current reports
        for widget in self.reports_frame.winfo_children():
            widget.destroy()
        
        # Check if reports directory exists
        if not self.reports_dir.exists():
            no_reports_label = ctk.CTkLabel(
                self.reports_frame,
                text="No reports found\n\nRun tests to generate reports",
                font=ctk.CTkFont(size=14)
            )
            no_reports_label.pack(pady=20)
            self.main_window._update_status("No reports directory")
            return
        
        # Get report files
        report_files = []
        for ext in ["*.txt", "*.html", "*.json"]:
            report_files.extend(sorted(
                self.reports_dir.glob(ext),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            ))
        
        # Display reports
        if not report_files:
            no_reports_label = ctk.CTkLabel(
                self.reports_frame,
                text="No reports found\n\nRun tests to generate reports",
                font=ctk.CTkFont(size=14)
            )
            no_reports_label.pack(pady=20)
            self.main_window._update_status("No reports found")
            return
        
        for report_file in report_files:
            report_frame = ctk.CTkFrame(
                self.reports_frame,
                height=80
            )
            report_frame.pack(fill="x", pady=5, padx=5)
            report_frame.pack_propagate(False)
            
            # File icon
            icon = self._get_file_icon(report_file.suffix)
            icon_label = ctk.CTkLabel(
                report_frame,
                text=icon,
                font=ctk.CTkFont(size=24)
            )
            icon_label.pack(side="left", padx=10, pady=20)
            
            # File info
            info_text = f"Name: {report_file.name}\n"
            import time
            mtime = report_file.stat().st_mtime
            info_text += f"Modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))}\n"
            info_text += f"Size: {report_file.stat().st_size} bytes"
            
            info_label = ctk.CTkLabel(
                report_frame,
                text=info_text,
                font=ctk.CTkFont(size=14),
                anchor="w"
            )
            info_label.pack(side="left", padx=10, pady=10)
            
            # Buttons
            if report_file.suffix == ".html":
                preview_btn = ctk.CTkButton(
                    report_frame,
                    text="Preview",
                    command=lambda f=report_file: self._preview_report(f),
                    width=60
                )
                preview_btn.pack(side="right", padx=5, pady=20)
            
            open_btn = ctk.CTkButton(
                report_frame,
                text="Open",
                command=lambda f=report_file: self._open_report(f),
                width=60
            )
            open_btn.pack(side="right", padx=5, pady=20)
            
            delete_btn = ctk.CTkButton(
                report_frame,
                text="Delete",
                command=lambda f=report_file: self._delete_report(f),
                width=60,
                fg_color="#DC3545",
                hover_color="#BB2D3B"
            )
            delete_btn.pack(side="right", padx=5, pady=20)

        # Rebind mousewheel to include new widgets
        self._bind_mousewheel(self.reports_frame)

        self.main_window._update_status(f"Found {len(report_files)} report(s)")
    
    def _get_file_icon(self, suffix: str) -> str:
        """
        Get icon for file type.
        
        Args:
            suffix: File suffix (.txt, .html, .json)
        
        Returns:
            Icon string
        """
        if suffix == ".html":
            return "🌐"
        elif suffix == ".json":
            return "📊"
        else:
            return "📄"
    
    def _preview_report(self, report_file: Path):
        """
        Preview HTML report in dialog.
        
        Args:
            report_file: Path to HTML report file
        """
        try:
            # Create preview dialog
            preview_dialog = ctk.CTkToplevel(self)
            preview_dialog.title(f"Preview: {report_file.name}")
            preview_dialog.geometry("1000x700")
            
            # Read HTML content
            with open(report_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Create HTML preview (simplified - display as text)
            preview_label = ctk.CTkLabel(
                preview_dialog,
                text="HTML Report Preview (Content)",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            preview_label.pack(pady=(10, 5))
            
            # Text view for HTML content
            html_text = ctk.CTkTextbox(
                preview_dialog,
                font=ctk.CTkFont(family="Consolas", size=10)
            )
            html_text.pack(fill="both", expand=True, padx=10, pady=10)
            html_text.insert("1.0", html_content)
            html_text.configure(state="disabled")
            
            # Close button
            close_btn = ctk.CTkButton(
                preview_dialog,
                text="Close",
                command=preview_dialog.destroy,
                width=100
            )
            close_btn.pack(pady=10)
            
            self.main_window._update_status(f"Preview: {report_file.name}")
            
        except Exception as e:
            self.main_window._update_status(f"Error previewing report: {e}")
    
    def _open_report(self, report_file: Path):
        """
        Open report file.
        
        Args:
            report_file: Path to report file
        """
        try:
            if report_file.suffix == ".html":
                webbrowser.open(f"file://{report_file.absolute()}")
            else:
                # Open with default system application
                import os
                os.startfile(str(report_file))
            self.main_window._update_status(f"Opened: {report_file.name}")
        except Exception as e:
            self.main_window._update_status(f"Error opening report: {e}")
    
    def _delete_report(self, report_file: Path):
        """
        Delete report file.
        
        Args:
            report_file: Path to report file
        """
        try:
            if report_file.exists():
                report_file.unlink()
                self._load_reports()
                self.main_window._update_status(f"Deleted: {report_file.name}")
        except Exception as e:
            self.main_window._update_status(f"Error deleting report: {e}")
    
    def _delete_all_reports(self):
        """Delete all report files in the reports directory."""
        # Check if reports directory exists
        if not self.reports_dir.exists():
            self.main_window._update_status("No reports to delete")
            return
        
        # Get all report files
        report_files = []
        for ext in ["*.txt", "*.html", "*.json"]:
            report_files.extend(self.reports_dir.glob(ext))
        
        if not report_files:
            self.main_window._update_status("No reports to delete")
            return
        
        # Show confirmation dialog
        from tkinter import messagebox


        confirm = messagebox.askyesno(
            "Delete All Reports",
            f"Are you sure you want to delete {len(report_files)} report file(s)?\n\nThis action cannot be undone."
        )
        
        if not confirm:
            return
        
        # Delete all files
        deleted_count = 0
        failed_count = 0
        for report_file in report_files:
            try:
                report_file.unlink()
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete {report_file.name}: {e}")
                failed_count += 1
        
        # Reload and update status
        self._load_reports()
        
        if failed_count == 0:
            self.main_window._update_status(f"Deleted {deleted_count} report(s)")
        else:
            self.main_window._update_status(f"Deleted {deleted_count} report(s), {failed_count} failed")
