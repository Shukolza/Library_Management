"""Administrator interface"""

import sys
import logging
import tkinter as tk

from logic.gui_logic import ask_for_password, AdminMainWindow
from logic.db_logic import LibraryDatabase, resource_path
from config import DB_PATH


if __name__ == "__main__":
    # Logging setup
    log_file = resource_path("./log.txt")
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

    except Exception as e:
        logging.exception("A critical error occured, interputting:")
        try:
            error_root = tk.Tk()
            error_root.withdraw()
            from tkinter import messagebox

            messagebox.showerror("CRITICAL ERROR", f"An critical error occurred:\n{e}\n\nApplication will be interputted\n Contact system administrator")  # type: ignore
            error_root.destroy()

        except:
            pass

        sys.exit(1)
