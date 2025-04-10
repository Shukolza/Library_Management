"""All project GUI logic"""

import logging
from abc import ABC, abstractmethod
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
        title.grid(row=0, column=0, columnspan=4, pady=50)

        button_create = ttk.Button(
            self,
            text="Create new library",
            command=lambda: init_create_library_window(self._libraries_db, self),
        )
        button_create.grid(column=0, row=1, pady=10)

        libs_list_button = ttk.Button(
            self,
            text="Libraries list",
            command=lambda: ViewLibrariesWindow(self._libraries_db, self),
        )
        libs_list_button.grid(column=1, row=1, pady=10, padx=10)

        lib_delete_button = ttk.Button(
            self,
            text="Delete library",
            command=lambda: DeleteLibraryWindow(self._libraries_db, self),
        )
        lib_delete_button.grid(row=1, column=2)

        lib_edit_button = ttk.Button(
            self,
            text="Edit library",
            command=lambda: EditLibraryWindow(self._libraries_db, self),
        )
        lib_edit_button.grid(row=1, column=3, sticky="w", padx=(30, 0))

        update_button = ttk.Button(self, text="Update DB", command=self.update_db)
        update_button.grid(row=0, column=3, padx=10, pady=10, sticky="ne")

        contact_button = ttk.Button(
            self,
            text="Contact developer",
            command=lambda: web.open("https://github.com/Shukolza", new=2),
        )
        contact_button.grid(row=2, column=3, sticky="se", padx=10, pady=10)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)

    def update_db(self) -> None:
        """Reload DB from file (path stored in ./config.py)"""
        logging.debug("Updating DB...")
        self._libraries_db.load_data(DB_PATH)
        messagebox.showinfo("Success", "Database updated successfully")  # type: ignore


class LibraryListWindow:
    """Base class for windows that display library lists"""

    def __init__(
        self, db: LibraryDatabase, root: tk.Tk, title: str, geometry: str = "400x600"
    ) -> None:
        self._db = db
        self._libs_info = db.get_readable_libs_info()

        if len(self._libs_info) < 1:
            messagebox.showinfo("No libraries", "No libraries avalible!")  # type: ignore
            return

        self._window = tk.Toplevel(root)
        self._window.title(title)
        self._window.geometry(geometry)

        self._create_base_widgets()
        self._populate_list()
        self._configure_grid()
        center_window(self._window, root)

    def _create_base_widgets(self):
        """Create common widgets"""
        self._title = ttk.Label(self._window, text="Libraries", font=("Arial", 14))
        self._title.grid(row=0, column=0, pady=50)

        self._v_scrollbar = tk.Scrollbar(self._window, orient=tk.VERTICAL)
        self._v_scrollbar.grid(column=1, row=1, sticky="ns")

        self._info_text = tk.Text(self._window, yscrollcommand=self._v_scrollbar.set)
        self._info_text.grid(row=1, column=0, sticky="nsew")

        self._v_scrollbar.config(command=self._info_text.yview)  # type: ignore

    def _populate_list(self):
        """Fill Text with libs info"""
        for info_tuple in self._libs_info:
            self._info_text.insert(
                tk.END, f"{info_tuple[0]} - {info_tuple[1]}, {info_tuple[2]}\n"
            )

    def _configure_grid(self):
        """Configure grid weights"""
        self._window.columnconfigure(0, weight=1)
        self._window.rowconfigure(1, weight=1)


class LibraryActionWindow(LibraryListWindow, ABC):
    """Abstract base for windows that preform actions on libraries"""

    def __init__(
        self, db: LibraryDatabase, root: tk.Tk, title: str, geometry: str = "400x600"
    ) -> None:
        super().__init__(db, root, title, geometry)
        self._create_selection_widgets()
        self._create_action_widgets()

    def _create_selection_widgets(self) -> None:
        """Create combobox for lib selection"""
        libraries_to_choose = [
            f"{info[0]} - {info[1]}, {info[2]}" for info in self._libs_info
        ]

        self._selected_library = tk.StringVar(self._window)
        self._lib_combobox = ttk.Combobox(
            self._window,
            textvariable=self._selected_library,
            values=libraries_to_choose,
        )
        self._lib_combobox["state"] = "readonly"
        self._lib_combobox.grid(row=2, column=0)

        self._window.rowconfigure(2, weight=1)

    @abstractmethod
    def _create_action_widgets(self) -> None:
        """Create widgets specific to the action"""
        pass

    @abstractmethod
    def _handle_action(self) -> None:
        """Handle main action of the window"""
        pass

    def _get_selected_library(self) -> tuple[str, str, str] | None:
        """Get selected library info / None if nothing selected"""
        selected_index = self._lib_combobox.current()
        if selected_index < 0:
            return None
        return self._libs_info[selected_index]


class ViewLibrariesWindow(LibraryListWindow):
    """Window for viewing libraries list"""

    def __init__(self, db: LibraryDatabase, root: tk.Tk) -> None:
        super().__init__(db, root, "Libraries list")


class DeleteLibraryWindow(LibraryActionWindow):
    """Window for deleting libraries"""

    def __init__(self, db: LibraryDatabase, root: tk.Tk) -> None:
        super().__init__(db, root, "Delete Library")
        self._window.geometry("600x800")

    def _create_action_widgets(self) -> None:
        """Add deletion-specific widgets"""
        self._delete_button = ttk.Button(
            self._window, text="Delete", command=self._handle_action
        )
        self._delete_button.grid(row=3, column=0, pady=50)
        self._window.rowconfigure(3, weight=1)

    def _handle_action(self) -> None:
        """Handle deletion"""
        library = self._get_selected_library()
        if not library:
            show_custom_message(
                self._window, "Error", "Please select a library to delete!", "error"
            )
            return

        name = library[0]
        try:
            self._db.delete_library(name)
            self._db.save_data(DB_PATH)
            show_custom_message(
                self._window,
                "Success",
                f"Successfully deleted library {self._lib_combobox.get()}",
            )
            self._window.destroy()
        except DatabaseException:
            show_custom_message(
                self._window,
                "Error",
                f"Could not delete library '{name}'. It might have been already deleted. Please use 'Update DB' button",
                "error",
            )


class EditLibraryWindow(LibraryActionWindow):
    """Window for editing libs info without losing data"""

    def __init__(self, db: LibraryDatabase, root: tk.Tk) -> None:
        super().__init__(db, root, "Edit library")
        self._window.geometry("600x800")
        messagebox.showinfo("Note", "Such library editing is SAFE. No data will be lost! \n :)")  # type: ignore

    def _create_action_widgets(self) -> None:
        """Add editing-specific widgets"""
        self._edit_button = ttk.Button(
            self._window, text="Edit", command=self._handle_action
        )
        self._edit_button.grid(row=3, column=0, pady=50)
        self._window.rowconfigure(3, weight=1)

    def _handle_action(self) -> None:
        """Handle editing libs"""
        library = self._get_selected_library()
        if not library:
            messagebox.showerror("Error", "Please select a library to edit!")  # type: ignore
            return
        old_name, old_city, old_address = library

        self._edit_window = tk.Toplevel(self._window)
        self._edit_window.title("Edit")
        self._edit_window.geometry("300x300")

        title = ttk.Label(
            self._edit_window,
            text="Please select what do you want to edit",
            anchor="center",
        )
        title.grid(column=0, row=0, sticky="nsew")

        options_for_edit = ["Name", "City", "Address"]
        chosen_option = tk.StringVar(self._window)

        choose_combobox = ttk.Combobox(
            self._edit_window, textvariable=chosen_option, values=options_for_edit
        )
        choose_combobox["state"] = "readonly"
        choose_combobox.grid(column=0, row=1, sticky="nsew")

        new_value_entry_title = ttk.Label(
            self._edit_window,
            text=f"Please enter new value",
        )
        new_value_entry_title.grid(column=0, row=2)
        new_value_entry = ttk.Entry(self._edit_window)
        new_value_entry.grid(column=0, row=3)

        choose_button = ttk.Button(
            self._edit_window,
            text="Edit",
            command=lambda: edit(
                old_name, choose_combobox.get().lower(), new_value_entry.get()
            ),
        )
        choose_button.grid(column=0, row=4)

        current_values_label = ttk.Label(
            self._edit_window,
            text=f"Current values:\nName: {old_name}\nCity: {old_city}\nAddress: {old_address}",
        )
        current_values_label.grid(column=0, row=5)

        # Configure grid
        self._edit_window.columnconfigure(0, weight=1)

        def edit(lib_name: str, type: str, new_value: str) -> None:
            """Edit lib info"""

            def get_old_value(type: str) -> str:
                """Function to get old value of type"""
                if type == "name":
                    return old_name
                if type == "city":
                    return old_city
                return old_address

            old_value = get_old_value(type)
            if not type:
                messagebox.showerror("Error", "Please choose what to edit!")  # type: ignore
                return
            if not new_value:
                messagebox.showerror("Error", "Please enter new value!")  # type: ignore
                return
            if new_value == old_value:
                show_custom_message(
                    self._edit_window, "Error", "New value is same as old one!", "error"
                )
                return
            
            #TODO. I need to develop DB method first.
            


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
