"""All database logic"""

import os
import sys
import json
import hashlib
import logging

from dataclasses import dataclass, asdict
from pathlib import Path
from tkinter import messagebox

from logic.loading_window import LoadingWindow

_HASH_ALGORITHM = "sha256"
_HASH_ITERATIONS = 600_000

_LIBRARIES_DATA_KEY = "libraries_data"
_ADMIN_PASSWORD_DATA_KEY = "administrator_password"
_LIB_NAME_DATA_KEY = "name"
_LIB_CITY_DATA_KEY = "city"
_LIB_ADDRESS_DATA_KEY = "address"


@dataclass
class Library:
    name: str
    city: str
    address: str


class LibraryDatabase:
    """Class for database with libraries data"""

    def __init__(self):
        self._libs_data: list[Library] = []
        self._admin_password: str = ""
        self.password_set: bool = bool(self._admin_password)

    def load_data(self, file_path: Path) -> None:
        """Load data from a JSON file with a loading window."""
        loading_window = LoadingWindow()
        logging.info(f"Loading DB from {file_path}")

        try:
            # Load data from file
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                for lib in data[_LIBRARIES_DATA_KEY]:
                    self._libs_data.append(
                        Library(
                            lib[_LIB_NAME_DATA_KEY],
                            lib[_LIB_CITY_DATA_KEY],
                            lib[_LIB_ADDRESS_DATA_KEY],
                        )
                    )
                self._admin_password = data[_ADMIN_PASSWORD_DATA_KEY]
                self.password_set = bool(self._admin_password)
        except FileNotFoundError:
            logging.error("DB file not found while loading. Interputting...")
            loading_window.close()
            messagebox.showerror("Error", "The specified database file was not found.\n Contact system administrator")  # type: ignore
            sys.exit(1)
        except json.JSONDecodeError:
            logging.error("JSON decoding failed. Interputting...")
            loading_window.close()
            messagebox.showerror(  # type:ignore
                "Error",
                "Failed to decode JSON from the database file.\n Contact system administrator",
            )
            sys.exit(1)
        except KeyError:
            logging.error("Invalid DB structure. Interputting...")
            loading_window.close()
            messagebox.showerror(  # type:ignore
                "Error", "Invalid database structure!\n Contact system administrator"
            )
            sys.exit(1)
        except Exception as e:
            logging.exception("UNEXPECTED ERROR WHILE LOADING DB, INTERPUTTING: ")
            loading_window.close()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}\n Contact system administrator")  # type: ignore
            sys.exit(1)
        finally:
            loading_window.close()

    def save_data(self, file_path: Path) -> None:
        """writes all current data to database"""
        logging.info(f"saving DB to {file_path}")
        try:
            with open(file_path, "w") as file:
                json.dump(
                    {
                        _LIBRARIES_DATA_KEY: [asdict(lib) for lib in self._libs_data],
                        _ADMIN_PASSWORD_DATA_KEY: self._admin_password,
                    },
                    file,
                    indent=4,
                )
        except OSError as e:
            logging.exception(f"Failed to save DB to {file_path}:")
            messagebox.showerror("Error", f"Failed to save database file:\n{e}\n Contact system administrator")  # type: ignore
            sys.exit(1)

    def add_library(self, name: str, city: str, address: str) -> None:
        """Add a new library to the database."""
        if not name or not city or not address:
            logging.warning("Not all fields filled while adding lb. Raising VE...")
            raise ValueError("All fields (name, city, address) must be filled.")
        for lib in self._libs_data:
            if lib.name == name:
                raise ValueError(
                    f"Library with name '{name}' already exists in city {lib.city}, on {lib.address}"
                )
            if address == lib.address and city == lib.city:
                raise ValueError(
                    f"Library with address '{address}' already exists in city {lib.city}, with name {lib.name}"
                )

        self._libs_data.append(Library(name, city, address))

    def get_readable_libs_info(self) -> list[tuple[str, str, str]]:
        """Get readable info of all libraries
        Returns:
            list of tuples (name, city, address)
        """
        logging.debug("AdminMainWindow: called get_readable_libs_info")
        libs_info: list[tuple[str, str, str]] = []

        for lib in self._libs_data:
            libs_info.append(
                (
                    lib.name,
                    lib.city,
                    lib.address,
                )
            )

        return libs_info

    def update_admin_password(self, new_password: str) -> None:
        """Hash and update the administrator password."""
        if not new_password:
            logging.warning("Empty password while updating. Raising VE...")
            raise ValueError("Password cannot be empty.")

        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            _HASH_ALGORITHM, new_password.encode("utf-8"), salt, _HASH_ITERATIONS
        )

        self._admin_password = salt.hex() + "$" + key.hex()
        self.password_set = True

    def verify_password(self, password: str) -> bool:
        """Verify password"""
        if not self._admin_password or "$" not in self._admin_password:
            logging.warning(
                "Wrong password string detected while verifying password. Returning False..."
            )
            return False

        salt_hex, key_hex = self._admin_password.split("$")
        salt = bytes.fromhex(salt_hex)
        stored_key = bytes.fromhex(key_hex)

        new_key = hashlib.pbkdf2_hmac(
            _HASH_ALGORITHM, password.encode("utf-8"), salt, _HASH_ITERATIONS
        )
        return new_key == stored_key

    def delete_library(self, library_readable: str, db_path: Path) -> None:
        """Delete library from database by readable name.

        Parameters:
        library_readable (str): Library readable in format {name} - {city}, {address}.
        db_path (Path): Path to save DB in."""
        if not library_readable:
            logging.warning("Empty library name while deleting. Raising VE...")
            raise ValueError("No library provided")
        lib_name = library_readable[: library_readable.index("-")].rstrip()
        for lib in self._libs_data:
            if lib.name == lib_name:
                self._libs_data.remove(lib)
                self.save_data(db_path)
                break


def resource_path(relative_path: str) -> Path:
    """Get the correct file path for both development and compiled EXE."""
    try:
        # If compiled (PyInstaller)
        base_path: Path = Path(sys._MEIPASS)  # type: ignore
    except AttributeError:
        # If launched via Python
        base_path: Path = Path(__file__).parent.parent

    full_path = base_path / relative_path
    return full_path.resolve()
