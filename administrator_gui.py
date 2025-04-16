"""Интерфейс администратора"""

import sys
import logging
import tkinter as tk

from tkinter import messagebox

from logic.gui_logic import ask_for_password, AdminMainWindow
from logic.db_logic import (
    LibraryDatabase,
    DatabaseLoadError,
    InvalidDatabaseStructureError,
)
from config import DB_PATH
from logic.gui_utils import resource_path, setup_logging


if __name__ == "__main__":
    setup_logging(resource_path("./admin_log.txt"))
    logging.info("Запуск.")
    libraries_db = LibraryDatabase()
    try:
        libraries_db.load_data(DB_PATH)
        logging.info("Данные загружены. Запрос пароля...")

        if ask_for_password(libraries_db):
            logging.info("Пароль принят. Инициализация корневого окна...")
            root = AdminMainWindow(libraries_db)
            root.mainloop()
        else:
            logging.warning("Диалог закрыт. Прерывание...")
            sys.exit(0)

    except InvalidDatabaseStructureError as e:
        logging.exception("Ошибка структуры базы данных")
        messagebox.showerror(  # type: ignore
            "Ошибка",
            f"Обнаружена неверная структура БД. Приложение будет прервано.\n{e}\n Обратитесь к системному администратору",
        )
        sys.exit(1)

    except DatabaseLoadError as e:
        logging.exception("Ошибка загрузки базы данных")
        messagebox.showerror(  # type: ignore
            "Ошибка",
            f"Не удалось загрузить данные из БД. Приложение будет прервано.\n{e}\n Обратитесь к системному администратору",
        )
        sys.exit(1)

    except Exception as e:
        logging.exception("Произошла критическая непредвиденная ошибка, прерывание...")
        try:
            error_root = tk.Tk()
            error_root.withdraw()

            messagebox.showerror("КРИТИЧЕСКАЯ ОШИБКА", f"Произошла критическая ошибка:\n{e}\n\nПриложение будет прервано\n Обратитесь к системному администратору")  # type: ignore
            error_root.destroy()

        except Exception:
            logging.exception("Не удалось показать окно критической ошибки:")

        sys.exit(1)
