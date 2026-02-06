"""
Base view class for GUI components.

Provides common functionality for all GUI views including:
- Lifecycle hooks
- Mouse wheel scrolling
- Status updates
- UI building helpers
"""

import customtkinter as ctk
from typing import Optional


class BaseView(ctk.CTkFrame):
    """
    Base class for all GUI views.

    Provides common functionality:
    - Standardized initialization lifecycle
    - Mouse wheel binding for scrollable frames
    - Status message updates
    - Common UI building patterns

    Subclasses should override:
    - _setup_state(): Initialize view-specific state
    - _build_ui(): Build view UI components
    - _load_data(): Load initial data (optional)

    Attributes:
        main_window: Reference to MainWindow instance
    """

    def __init__(self, parent, main_window):
        """
        Initialize base view.

        Args:
            parent: Parent widget
            main_window: Reference to MainWindow instance
        """
        super().__init__(parent)
        self.main_window = main_window

        # Call lifecycle hooks
        self._setup_state()
        self._build_ui()
        self._load_data()

    def _setup_state(self):
        """
        Initialize view-specific state.

        Override this method to set up instance variables,
        references to managers, etc.

        Example:
            self.selected_item = None
            self.items = []
        """
        pass

    def _build_ui(self):
        """
        Build view UI components.

        Override this method to create UI elements.
        Must be implemented by subclass.

        Raises:
            NotImplementedError: If not overridden by subclass
        """
        raise NotImplementedError("Subclass must implement _build_ui()")

    def _load_data(self):
        """
        Load initial data after UI is built.

        Override this method to load data from managers,
        populate lists, etc. Called after _build_ui().

        This is optional - default implementation does nothing.
        """
        pass

    # ==================== Helper Methods ====================

    def update_status(self, message: str):
        """
        Update main window status bar message.

        Args:
            message: Status message to display
        """
        if hasattr(self.main_window, '_update_status'):
            self.main_window._update_status(message)

    def _build_title(self, text: str, font_size: int = 20) -> ctk.CTkLabel:
        """
        Build standardized title label.

        Args:
            text: Title text
            font_size: Font size in points

        Returns:
            CTkLabel widget (already packed)
        """
        title_label = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=font_size, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        return title_label

    def _build_scrollable_frame(
        self,
        height: Optional[int] = None,
        **kwargs
    ) -> ctk.CTkScrollableFrame:
        """
        Build scrollable frame with mousewheel binding.

        Args:
            height: Optional frame height
            **kwargs: Additional arguments for CTkScrollableFrame

        Returns:
            CTkScrollableFrame widget (already packed with mousewheel)
        """
        if height:
            kwargs['height'] = height

        frame = ctk.CTkScrollableFrame(self, **kwargs)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Automatically bind mousewheel
        self._bind_mousewheel(frame)

        return frame

    def _create_item_frame(
        self,
        parent,
        height: int = 80
    ) -> ctk.CTkFrame:
        """
        Create standardized item frame for lists.

        Args:
            parent: Parent widget
            height: Frame height

        Returns:
            CTkFrame widget (already configured)
        """
        frame = ctk.CTkFrame(parent, height=height)
        frame.pack(fill="x", pady=5, padx=5)
        frame.pack_propagate(False)
        return frame

    def _bind_mousewheel(self, widget: ctk.CTkScrollableFrame):
        """
        Bind mouse wheel scrolling to a scrollable widget.

        Handles cross-platform mousewheel events (Windows, macOS, Linux)
        and recursively binds to all child widgets.

        Args:
            widget: CTkScrollableFrame to bind mouse wheel events
        """
        # CTkScrollableFrame has _parent_canvas attribute for internal canvas
        def on_mousewheel(event):
            try:
                # Windows and MacOS
                if event.delta:
                    widget._parent_canvas.yview_scroll(
                        int(-1 * (event.delta / 120)),
                        "units"
                    )
            except Exception:
                pass

        def on_mousewheel_linux_up(event):
            try:
                widget._parent_canvas.yview_scroll(-1, "units")
            except Exception:
                pass

        def on_mousewheel_linux_down(event):
            try:
                widget._parent_canvas.yview_scroll(1, "units")
            except Exception:
                pass

        def bind_to_widget(w):
            """Recursively bind mouse wheel to widget and all its children."""
            try:
                w.bind("<MouseWheel>", on_mousewheel, add="+")
                w.bind("<Button-4>", on_mousewheel_linux_up, add="+")
                w.bind("<Button-5>", on_mousewheel_linux_down, add="+")
            except Exception:
                pass

            # Bind to all children recursively
            try:
                for child in w.winfo_children():
                    bind_to_widget(child)
            except Exception:
                pass

        # Bind to the scrollable frame and all its children
        bind_to_widget(widget)

        # Also bind to the internal canvas
        try:
            widget._parent_canvas.bind("<MouseWheel>", on_mousewheel, add="+")
            widget._parent_canvas.bind("<Button-4>", on_mousewheel_linux_up, add="+")
            widget._parent_canvas.bind("<Button-5>", on_mousewheel_linux_down, add="+")
        except Exception:
            pass

    def rebind_mousewheel(self, widget: ctk.CTkScrollableFrame):
        """
        Rebind mousewheel after adding new widgets.

        Call this after dynamically adding widgets to a scrollable frame.

        Args:
            widget: CTkScrollableFrame to rebind
        """
        self._bind_mousewheel(widget)
