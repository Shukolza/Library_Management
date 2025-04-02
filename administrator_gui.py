"""Administrator interface"""

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
    logging.info("Started.")
    libraries_db = LibraryDatabase()
    try:
        libraries_db.load_data(DB_PATH)
        logging.info("Data loaded. Requesting password...")

        if ask_for_password(libraries_db):
            logging.info("Password accepted. Initializing root...")
            root = AdminMainWindow(libraries_db)
            root.mainloop()
        else:
            logging.warning("Dialog closed. Interputting...")
            sys.exit(0)

    except InvalidDatabaseStructureError as e:
        logging.exception("Database structure error")
        messagebox.showerror(  # type: ignore
            "Error",
            f"Wrong DB structure detected. Application will be interputted.\n{e}\n Contact system administrator",
        )
        sys.exit(1)

    except DatabaseLoadError as e:
        logging.exception("Database load error")
        messagebox.showerror(  # type: ignore
            "Error",
            f"Failed to load data from DB. Application will be interputted.\n{e}\n Contact system administrator",
        )
        sys.exit(1)

    except Exception as e:
        logging.exception("A critical unexpected error occured, interputting...")
        try:
            error_root = tk.Tk()
            error_root.withdraw()

            messagebox.showerror("CRITICAL ERROR", f"A critical error occurred:\n{e}\n\nApplication will be interputted\n Contact system administrator")  # type: ignore
            error_root.destroy()

        except:
            pass

        sys.exit(1)
