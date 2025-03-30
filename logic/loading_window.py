import tkinter as tk
from tkinter import ttk

from logic.gui_utils import center_window


class LoadingWindow:
    def __init__(self) -> None:
        self._temp_root = tk.Tk()
        self._temp_root.geometry("1x1+-100+-100")
        # Create loading window
        self._loading_window = tk.Toplevel(self._temp_root)
        self._loading_window.title("Loading...")
        self._loading_window.geometry("300x100")
        self._loading_window.overrideredirect(True)
        self._loading_window.resizable(False, False)
        self.loading_label = ttk.Label(
            self._loading_window, text="Loading libraries data..."
        )
        self.loading_label.pack(expand=True, pady=20)

        # Centralizing
        center_window(self._loading_window, width=300, height=100)

        self._loading_window.update()  # Update window to make it display

    def close(self) -> None:
        if self._loading_window.winfo_exists():
            self._loading_window.destroy()

        if self._temp_root.winfo_exists():
            self._temp_root.destroy()
