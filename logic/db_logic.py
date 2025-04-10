"""All database logic"""

import os
import json
import hashlib
import logging

from dataclasses import dataclass, asdict
from pathlib import Path

from logic.loading_window import LoadingWindow

# Constans for password hashing
_HASH_ALGORITHM = "sha256"
_HASH_ITERATIONS = 600_000

# Constants for libs data keys
_LIBRARIES_DATA_KEY = "libraries_data"
_ADMIN_PASSWORD_DATA_KEY = "administrator_password"
_LIB_NAME_DATA_KEY = "name"
_LIB_CITY_DATA_KEY = "city"
_LIB_ADDRESS_DATA_KEY = "address"

# Constants for editing types
EDIT_TYPE_NAME = "name"
EDIT_TYPE_CITY = "city"
EDIT_TYPE_ADDRESS = "address"
VALID_EDIT_TYPES = {EDIT_TYPE_NAME, EDIT_TYPE_CITY, EDIT_TYPE_ADDRESS}


class DatabaseException(Exception):
    """Base exception for DB operations"""


class DatabaseLoadError(DatabaseException):
    """Exception for DB load error"""


class DatabaseSaveError(DatabaseException):
    """Exception for DB save error"""


class InvalidDatabaseStructureError(DatabaseException):
    """Exception for DB structure error"""


@dataclass
class Library:
    """Library dataclass"""

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
        self._libs_data = []

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
        except FileNotFoundError as e:
            logging.exception("DB file not found while loading. Raising DBLoadError...")
            loading_window.close()
            raise DatabaseLoadError("DB file not found") from e
        except json.JSONDecodeError as e:
            logging.exception("JSON decoding failed. Raising DBLoadError...")
            loading_window.close()
            raise DatabaseLoadError("JSON decoding failed") from e
        except KeyError as e:
            logging.exception(
                "Invalid DB structure. Raising InvalidDatabaseStructureError..."
            )
            loading_window.close()
            raise InvalidDatabaseStructureError("Invalid DB structure error") from e
        except Exception as e:
            logging.exception(
                "UNEXPECTED ERROR WHILE LOADING DB, RAISING DBLoadError..."
            )
            loading_window.close()
            raise DatabaseLoadError(f"Unexpected error while loading DB\n{e}") from e
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
            raise DatabaseSaveError(f"Failed to save DB to {file_path}") from e

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

    def delete_library(self, library_name: str) -> None:
        """Delete library from database by strict name.

        Parameters:
        library_name (str): Library name."""
        for lib in self._libs_data:
            if lib.name == library_name:
                self._libs_data.remove(lib)
                return
        raise DatabaseException("Library not found when deleting!")

    def edit_library_data(
        self, lib_name: str, type_of_edit: str, new_value: str
    ) -> None:
        """Edit library data in the system.
        This method allows safe modification of library properties including name, city, and address.
        Args:
            lib_name (str): Current name of the library to edit
            type_of_edit (str): Type of edit to perform ('name', 'city', or 'address')
            new_value (str): New value to set for the specified field
        Raises:
            ValueError: If any parameters are empty/None
            ValueError: If type_of_edit is not 'name', 'city' or 'address'
            ValueError: If library with given name not found
        Returns:
            None
        """
        if not lib_name or not type_of_edit or not new_value:
            logging.warning("Empty parameters while editing. Raising ValueError...")
            raise ValueError("All parameters (name, type, new value) must be filled.")
        if type_of_edit not in VALID_EDIT_TYPES:
            logging.warning(
                f"Unsupported edit type: {type_of_edit}. Raising ValueError..."
            )
            raise ValueError(
                f"Invalid edit type: {type_of_edit}. Must be one of {VALID_EDIT_TYPES}"
            )
        for lib in self._libs_data:
            if lib.name == lib_name:
                if type_of_edit == EDIT_TYPE_NAME:
                    for other_lib in self._libs_data:
                        if other_lib is not lib and other_lib.name == new_value:
                            raise ValueError(
                                f"Another library with name '{new_value}' already exists."
                            )
                    lib.name = new_value
                    break
                if type_of_edit == EDIT_TYPE_CITY:
                    lib.city = new_value
                    break
                if type_of_edit == EDIT_TYPE_ADDRESS:
                    for other_lib in self._libs_data:
                        if (
                            other_lib is not lib
                            and other_lib.address == new_value
                            and other_lib.city == lib.city
                        ):
                            raise ValueError(
                                f"Another library with address '{new_value}' already exists in the same city {lib.city}"
                            )
                    lib.address = new_value
                    break
        else:
            logging.warning("Invalid lib name while editing. Raising ValueError...")
            raise ValueError(f"Library '{lib_name}' not found")
