"""All project GUI logic"""

import logging
import tkinter as tk
import webbrowser as web
from tkinter import ttk
from tkinter import messagebox

from logic.db_logic import LibraryDatabase, DatabaseSaveError, DatabaseException
from logic.gui_utils import center_window
from config import DB_PATH, ICON_PATH


class AdminMainWindow(tk.Tk):
    """Class for Admin window."""

    def __init__(self, libraries_db: LibraryDatabase) -> None:
        logging.debug("Initializing AdminMainWindow")
        super().__init__()
        self._libraries_db = libraries_db
        self.title("Administrator Interface")
        self.geometry("800x600")
        self.create_widgets()
        center_window(self, width=800, height=600)

    def create_widgets(self):
        """Create all widgets of Admin window and set icon"""
        logging.debug("Calling AdminMainWindow create_widgets()")
        set_icon(self)
        title = ttk.Label(
            self,
            text="Welcome, administrator.\n Please select an option below.",
            font=("Arial", 14),
            anchor="center",
        )
        title.grid(row=0, column=1, columnspan=2, pady=50, sticky="w")

        button_create = ttk.Button(
            self,
            text="Create new library",
            command=lambda: init_create_library_window(self._libraries_db, self),
        )
        button_create.grid(column=0, row=1, pady=10, sticky="e")

        libs_list_button = ttk.Button(
            self,
            text="Libraries list",
            command=lambda: list_libs_window(self._libraries_db, self),
        )
        libs_list_button.grid(column=1, row=1, pady=10, padx=10)

        lib_delete_button = ttk.Button(
            self,
            text="Delete library",
            command=lambda: init_delete_lib_window(self._libraries_db, self),
        )
        lib_delete_button.grid(row=1, column=2, sticky="w")

        update_button = ttk.Button(self, text="Update DB", command=self.update_db)
        update_button.grid(row=0, column=2, padx=10, pady=10, sticky="ne")

        contact_button = ttk.Button(
            self,
            text="Contact developer",
            command=lambda: web.open("https://github.com/Shukolza", new=2),
        )
        contact_button.grid(row=2, column=2, sticky="se", padx=10, pady=10)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)

    def update_db(self) -> None:
        """Reload DB from file (path stored in ./config.py)"""
        logging.debug("Updating DB...")
        self._libraries_db.load_data(DB_PATH)
        messagebox.showinfo("Success", "Database updated successfully")  # type: ignore


def set_icon(window: tk.Tk) -> None:
    """Set window icon from path provided in ./config.py"""
    try:
        logging.info(f"Attempt setting icon from {ICON_PATH}")
        icon = tk.PhotoImage(file=ICON_PATH)
        window.tk.call("wm", "iconphoto", window._w, icon)  # type: ignore # Alternative way to install icon
        window.icon = icon  # type: ignore # Saving link to make it not to be eaten by gc
    except tk.TclError as e:
        logging.error(f"ERROR installing icon\n{e}")


def show_custom_message(
    parent: tk.Toplevel | tk.Tk, title: str, message: str, msg_type: str = "info"
) -> None:
    """
    Shows custom modal messagebox, centralized on parent
    :param msg_type: 'info' and 'error' supported. Only changes icon.
    """
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.resizable(False, False)

    icon_label = None
    if msg_type == "error":
        try:
            # Trying to load tkinter error icon
            icon_label = ttk.Label(dialog, image="::tk::icons::error", padding=(10, 10))
        except tk.TclError:
            logging.warning("Standard error icon not found")
    elif msg_type == "info":
        try:
            # Trying to load tkinter info icon
            icon_label = ttk.Label(
                dialog, image="::tk::icons::information", padding=(10, 10)
            )
        except tk.TclError:
            logging.warning("Standard info icon not found")

    if icon_label:
        icon_label.grid(row=0, column=0, sticky="ns", padx=(10, 0))

    message_label = ttk.Label(dialog, text=message, padding=(10, 10), wraplength=300)

    text_column = 1 if icon_label else 0
    button_columnspan = 2 if icon_label else 1
    message_label.grid(row=0, column=text_column, sticky="nsew", padx=(0, 10))

    ok_button = ttk.Button(dialog, text="OK", command=dialog.destroy, width=10)
    ok_button.grid(row=1, column=0, columnspan=button_columnspan, pady=(0, 10))
    ok_button.focus_set()

    # Centralizing
    center_window(dialog, parent)

    # --- Modality ---
    dialog.grab_set()
    dialog.wait_window()


def set_password(
    libraries_db: LibraryDatabase,
    password_window: tk.Toplevel,
    password_entry: ttk.Entry,
) -> bool:
    """Set admin password"""
    password = password_entry.get()
    try:
        libraries_db.update_admin_password(password)
        try:
            libraries_db.save_data(DB_PATH)
        except DatabaseSaveError as e:
            logging.exception("DB Save error")
            messagebox.showerror(  # type: ignore
                "Error",
                f"Failed to save password!\n{e}\n Contact system administrator.\n You can continue working, but it is not recommended",
            )
        password_window.destroy()
        return True
    except ValueError:
        logging.warning("Password empty error occured")
        show_custom_message(
            password_window, "Error", "Password can not be empty", "error"
        )
        password_entry.focus_set()
        return False


def check_password(
    password_entry: ttk.Entry,
    libraries_db: LibraryDatabase,
    password_window: tk.Toplevel,
) -> bool:
    """Check administrator password"""
    password = password_entry.get()
    if libraries_db.verify_password(password):
        password_window.destroy()
        return True

    logging.warning("Wrong password entred")
    show_custom_message(password_window, "Error", "Wrong password, try again", "error")
    password_entry.delete(0, tk.END)
    password_entry.focus_set()
    return False


def create_library(
    name: str,
    city: str,
    address: str,
    window: tk.Toplevel,
    libraries_db: LibraryDatabase,
    entries: list[ttk.Entry],
) -> None:
    """Create new library and add info to DB"""
    try:
        libraries_db.add_library(name, city, address)
        try:
            libraries_db.save_data(DB_PATH)
        except DatabaseSaveError as e:
            logging.exception("DB Save error")
            messagebox.showerror(  # type: ignore
                "Error",
                f"Failed to save library! It will be lost when you close app!\n{e}\n Contact system administrator.\n You can continue working, but it is not recommended",
            )
        window.destroy()
    except ValueError as error:
        show_custom_message(window, "Error", str(error), "error")
        for entry in entries:
            entry.delete(0, tk.END)
        return
    messagebox.showinfo(  # type:ignore
        f"Success", f"Successfully created library '{name}' in {city}, {address}"
    )
    window.destroy()


def init_create_library_window(libraries_db: LibraryDatabase, root: tk.Tk) -> None:
    """Create window for creating library"""
    create_library_window = tk.Toplevel()
    create_library_window.title("Create library")

    library_name_label = ttk.Label(create_library_window, text="New library name")
    library_name_label.grid(column=0, row=0, padx=10, pady=10)

    library_name_entry = ttk.Entry(create_library_window)
    library_name_entry.grid(column=0, row=1, padx=10, pady=10)

    library_city_label = ttk.Label(create_library_window, text="New library city")
    library_city_label.grid(column=1, row=0, padx=10, pady=10)

    library_city_entry = ttk.Entry(create_library_window)
    library_city_entry.grid(column=1, row=1, padx=10, pady=10)

    library_address_label = ttk.Label(create_library_window, text="New library address")
    library_address_label.grid(column=2, row=0, padx=10, pady=10)

    library_address_entry = ttk.Entry(create_library_window)
    library_address_entry.grid(column=2, row=1, padx=10, pady=10)

    submit_button = ttk.Button(
        create_library_window,
        text="CREATE",
        command=lambda: create_library(
            library_name_entry.get(),
            library_city_entry.get(),
            library_address_entry.get(),
            create_library_window,
            libraries_db,
            [library_name_entry, library_city_entry, library_address_entry],
        ),
    )
    submit_button.grid(column=0, row=2, columnspan=3, padx=10)

    center_window(create_library_window, root)

    create_library_window.grab_set()
    create_library_window.wait_window()


def ask_for_password(db: LibraryDatabase) -> bool:
    """
    Shows modal window for password entry
    :return: True if password is correct, False otherwise
    """
    logging.debug("ask_for_password: Creating temp root...")
    dialog_root = tk.Tk()
    dialog_root.geometry("1x1+-100+-100")  # Hide, but cannot use withdraw

    logging.debug("ask_for_password: Creating Toplevel dialog...")
    password_dialog = tk.Toplevel(dialog_root)
    password_dialog.title("Authentication")
    password_dialog.transient(dialog_root)

    password_ok = False

    def on_submit():
        nonlocal password_ok
        logging.debug("ask_for_password: Submit button clicked.")
        is_ok = False
        if db.password_set:
            is_ok = check_password(password_entry, db, password_dialog)
        else:
            is_ok = set_password(db, password_dialog, password_entry)

        if is_ok:
            logging.debug("ask_for_password: Password OK, setting result to True.")
            password_ok = True
            # window destroys in check/set _password

    def on_close():
        nonlocal password_ok
        logging.debug("ask_for_password: Dialog closed by user.")
        password_ok = False
        password_dialog.destroy()

    password_dialog.protocol("WM_DELETE_WINDOW", on_close)

    logging.debug("ask_for_password: Creating widgets...")
    password_dialog.geometry("300x150")
    password_label = ttk.Label(
        password_dialog,
        text=(
            "Enter administrator password:"
            if db.password_set
            else "Create new admin password"
        ),
    )
    password_label.grid(column=0, row=0, padx=10, pady=10)

    password_entry = ttk.Entry(password_dialog, show="*")
    password_entry.grid(column=0, row=1, padx=10, pady=10, sticky="ew")
    password_entry.focus_set()

    password_button = ttk.Button(password_dialog, text="Enter", command=on_submit)
    password_button.grid(column=0, row=2, padx=10, pady=20)

    # Centralizing
    center_window(password_dialog, width=300, height=150)

    logging.info("ask_for_password: Setting modality up...")
    logging.debug("ask_for_password: Calling grab_set()...")
    password_dialog.grab_set()
    logging.debug("ask_for_password: Calling wait_window()")
    password_dialog.wait_window()
    logging.debug("ask_for_password: wait_window finished.")

    logging.debug("ask_for_password: destroying temp root...")
    dialog_root.destroy()
    logging.debug(f"ask_for_password: returning {password_ok}")

    return password_ok


def list_libs_window(db: LibraryDatabase, root: tk.Tk) -> None:
    """Create a window to list all libraries in the database."""
    logging.info("list_libs_window: Called, getting libs info...")
    libs_info = db.get_readable_libs_info()
    logging.debug(f"list_libs_window: libs_info: {libs_info}")
    if len(libs_info) < 1:
        logging.info("list_libs_window: No libraries found.")
        messagebox.showinfo("No libs found", "No libraries to show!")  # type: ignore
        return
    logging.debug("list_libs_window: Creating toplevel...")
    list_window = tk.Toplevel(root)
    list_window.title("Library List")
    list_window.geometry("400x600")
    logging.info("list_libs_window: Creating widgets...")

    title = ttk.Label(list_window, text="Libraries", font=("Arial", 14))
    title.grid(row=0, column=0, pady=50)

    v_scrollbar = tk.Scrollbar(list_window, orient=tk.VERTICAL)
    v_scrollbar.grid(column=1, row=1, sticky="ns")

    info_text = tk.Text(list_window, yscrollcommand=v_scrollbar.set)
    info_text.grid(row=1, column=0, sticky="nsew")

    logging.info("list_libs_window: Filling text with info...")
    for info_tuple in libs_info:
        info_text.insert(
            tk.END, f"{info_tuple[0]} - {info_tuple[1]}, {info_tuple[2]}\n"
        )

    v_scrollbar.config(command=info_text.yview)  # type: ignore

    logging.debug("list_libs_window: Configuring grid...")
    list_window.columnconfigure(0, weight=1)
    list_window.rowconfigure(1, weight=1)

    logging.debug("list_libs_window: centralizing...")
    center_window(list_window, root)


def init_delete_lib_window(db: LibraryDatabase, root: tk.Tk) -> None:
    """Create GUI window to admin choose library to delete"""
    logging.info("init_delete_lib_window: Called, getting libs info...")
    libs_info = db.get_readable_libs_info()
    logging.debug(f"init_delete_lib_window: libs_info = {libs_info}")
    if len(libs_info) < 1:
        logging.info("init_delete_lib_window: No libraries found.")
        messagebox.showinfo("No libs found", "No libraries to delete!")  # type: ignore
        return
    logging.debug("init_delete_lib_window: Creating toplevel...")
    delete_window = tk.Toplevel(root)
    delete_window.title("Delete library")
    delete_window.geometry("600x800")
    logging.info("init_delete_lib_window: Creating widgets...")
    title = ttk.Label(delete_window, text="Libraries", font=("Arial", 14))
    title.grid(row=0, column=0, pady=50)

    v_scrollbar = tk.Scrollbar(delete_window, orient=tk.VERTICAL)
    v_scrollbar.grid(column=1, row=1, sticky="ns")

    info_text = tk.Text(delete_window, yscrollcommand=v_scrollbar.set)
    info_text.grid(row=1, column=0, sticky="nsew")

    logging.info("init_delete_lib_window: Filling text with info...")
    for info_tuple in libs_info:
        info_text.insert(
            tk.END, f"{info_tuple[0]} - {info_tuple[1]}, {info_tuple[2]}\n"
        )

    v_scrollbar.config(command=info_text.yview)  # type: ignore

    libraries_to_choose = [
        f"{info_tuple[0]} - {info_tuple[1]}, {info_tuple[2]}"
        for info_tuple in libs_info
    ]

    selected_library = tk.StringVar(delete_window)

    library_to_delete_combobox = ttk.Combobox(
        delete_window, textvariable=selected_library, values=libraries_to_choose
    )
    library_to_delete_combobox["state"] = "readonly"
    library_to_delete_combobox.grid(row=2, column=0)

    def on_delete():
        """Function for delete button. Gets library name and calls db.delete_library"""
        selected_index = library_to_delete_combobox.current()
        if selected_index < 0:
            logging.warning("init_delete_lib_window: on_delete: Library not selected")
            messagebox.showerror("Error", "Please select a library to delete!")  # type: ignore
            return
        selected_name = libs_info[selected_index][0]
        try:
            db.delete_library(selected_name)
            messagebox.showinfo("Success", f"Successfully deleted library {libraries_to_choose[selected_index]}")  # type: ignore
            delete_window.destroy()
        except DatabaseException:
            logging.exception(
                f"init_delete_lib_window: on_delete: Could not find library {selected_name}"
            )
            messagebox.showerror("Error", f"Could not delete library '{selected_name}'. It might have been already deleted. Please use 'Update DB' button")  # type: ignore

    delete_button = ttk.Button(delete_window, text="Delete", command=on_delete)
    delete_button.grid(row=3, column=0, pady=50)

    logging.debug("init_delete_lib_window: Configuring grid...")
    delete_window.columnconfigure(0, weight=1)
    delete_window.rowconfigure(1, weight=1)
    delete_window.rowconfigure(2, weight=1)
    delete_window.rowconfigure(3, weight=1)

    logging.debug("init_delete_lib_window: centralizing...")
    center_window(delete_window, root)
