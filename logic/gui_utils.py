"""Утилиты графического интерфейса"""

import sys
import logging
import tkinter as tk
from pathlib import Path


def center_window(
    window_to_center: tk.Tk | tk.Toplevel,
    parent: tk.Tk | tk.Toplevel | None = None,
    width: int | None = None,
    height: int | None = None,
) -> None:
    """Центрирует окно Tk или Toplevel относительно родителя или экрана."""
    logging.info(f"Центрирование {window_to_center}...")
    logging.debug(
        f"Центрирование с параметрами:\n{window_to_center}\n{parent}\n{width}\n{height}"
    )
    window_to_center.update_idletasks()

    win_width = width if width else window_to_center.winfo_reqwidth()
    win_height = height if height else window_to_center.winfo_reqheight()

    if parent:
        # Центрирование относительно родителя
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        ref_x = parent_x
        ref_y = parent_y
        ref_width = parent_width
        ref_height = parent_height
    else:
        # Центрирование относительно экрана
        ref_x = 0
        ref_y = 0
        ref_width = window_to_center.winfo_screenwidth()
        ref_height = window_to_center.winfo_screenheight()

    x = ref_x + (ref_width // 2) - (win_width // 2)
    y = ref_y + (ref_height // 2) - (win_height // 2)

    # Проверка, чтобы окно не вышло за пределы экрана
    screen_width = window_to_center.winfo_screenwidth()
    screen_height = window_to_center.winfo_screenheight()
    if x + win_width > screen_width:
        x = screen_width - win_width
    if y + win_height > screen_height:
        y = screen_height - win_height
    if x < 0:
        x = 0
    if y < 0:
        y = 0

    window_to_center.geometry(f"{win_width}x{win_height}+{x}+{y}")


def setup_logging(log_file: Path) -> None:
    """Настройка логирования"""
    log_level = logging.DEBUG
    log_format = "%(asctime)s - %(levelname)s - %(module)s - %(message)s"

    logging.basicConfig(
        filename=log_file, level=log_level, format=log_format, filemode="w"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler)


def resource_path(relative_path: str) -> Path:
    """Получить корректный путь к файлу для разработки и скомпилированного EXE."""
    try:
        # Если скомпилировано (PyInstaller)
        base_path: Path = Path(sys._MEIPASS)  # type: ignore
    except AttributeError:
        # Если запущено через Python
        base_path: Path = Path(__file__).parent.parent

    full_path = base_path / relative_path
    return full_path.resolve()
