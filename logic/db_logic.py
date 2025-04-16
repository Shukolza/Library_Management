"""All database logic"""

import os
import json
import hashlib
import logging

from dataclasses import dataclass, asdict
from pathlib import Path

from logic.loading_window import LoadingWindow

# Константы хеширования паролей
_HASH_ALGORITHM = "sha256"
_HASH_ITERATIONS = 600_000

# Константы для хранения данных
_LIBRARIES_DATA_KEY = "libraries_data"
_ADMIN_PASSWORD_DATA_KEY = "administrator_password"
_LIB_NAME_DATA_KEY = "name"
_LIB_CITY_DATA_KEY = "city"
_LIB_ADDRESS_DATA_KEY = "address"

# Константы для редактирования данных
EDIT_TYPE_NAME = "name"
EDIT_TYPE_CITY = "city"
EDIT_TYPE_ADDRESS = "address"
VALID_EDIT_TYPES = {EDIT_TYPE_NAME, EDIT_TYPE_CITY, EDIT_TYPE_ADDRESS}


class DatabaseException(Exception):
    """Базовый класс для всех исключений базы данных"""


class DatabaseLoadError(DatabaseException):
    """Исключение для ошибок загрузки базы данных"""


class DatabaseSaveError(DatabaseException):
    """Исключение для ошибок сохранения базы данных"""


class InvalidDatabaseStructureError(DatabaseException):
    """Исключение для ошибок структуры базы данных"""


@dataclass
class Library:
    """Датакласс для хранения данных о библиотеке"""

    name: str
    city: str
    address: str


class LibraryDatabase:
    """Класс для работы с базой данных библиотек"""

    def __init__(self):
        self._libs_data: list[Library] = []
        self._admin_password: str = ""
        self.password_set: bool = bool(self._admin_password)

    def load_data(self, file_path: Path) -> None:
        """Загрузка данных из файла базы данных с окном загрузки"""
        loading_window = LoadingWindow()
        logging.info(f"Загрузка БД из {file_path}")
        self._libs_data = []

        try:
            # Загружаем данные из файла
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
            logging.exception("Файл базы данных не найден. Вызываем DBLoadError...")
            loading_window.close()
            raise DatabaseLoadError("Файл БД не найден") from e
        except json.JSONDecodeError as e:
            logging.exception("Ошибка декодирования JSON. Вызываем DBLoadError...")
            loading_window.close()
            raise DatabaseLoadError("Ошибка декодирования JSON") from e
        except KeyError as e:
            logging.exception(
                "Неверная структура БД. Вызываем InvalidDatabaseStructureError..."
            )
            loading_window.close()
            raise InvalidDatabaseStructureError("Ошибка структуры БД") from e
        except Exception as e:
            logging.exception(
                "НЕОЖИДАННАЯ ОШИБКА ПРИ ЗАГРУЗКЕ БД, ВЫЗЫВАЕМ DBLoadError..."
            )
            loading_window.close()
            raise DatabaseLoadError(f"Неожиданная ошибка при загрузке БД\n{e}") from e
        finally:
            loading_window.close()

    def save_data(self, file_path: Path) -> None:
        """Записывает все текущие данные в базу данных"""
        logging.info(f"Сохранение БД в {file_path}")
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
            logging.exception(f"Не удалось сохранить БД в {file_path}:")
            raise DatabaseSaveError(f"Не удалось сохранить БД в {file_path}") from e

    def add_library(self, name: str, city: str, address: str) -> None:
        """Добавить новую библиотеку в базу данных."""
        if not name or not city or not address:
            logging.warning("Не все поля заполнены при добавлении библиотеки. Вызываем VE...")
            raise ValueError("Все поля (название, город, адрес) должны быть заполнены.")
        for lib in self._libs_data:
            if lib.name == name:
                raise ValueError(
                    f"Библиотека с названием '{name}' уже существует в городе {lib.city}, по адресу {lib.address}"
                )
            if address == lib.address and city == lib.city:
                raise ValueError(
                    f"Библиотека по адресу '{address}' уже существует в городе {lib.city}, с названием {lib.name}"
                )

        self._libs_data.append(Library(name, city, address))

    def get_readable_libs_info(self) -> list[tuple[str, str, str]]:
        """Получить читаемую информацию о всех библиотеках
        Возвращает:
            список кортежей (название, город, адрес)
        """
        logging.debug("AdminMainWindow: вызван get_readable_libs_info")
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
        """Хеширует и обновляет пароль администратора."""
        if not new_password:
            logging.warning("Пустой пароль при обновлении. Вызываем VE...")
            raise ValueError("Пароль не может быть пустым.")

        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            _HASH_ALGORITHM, new_password.encode("utf-8"), salt, _HASH_ITERATIONS
        )

        self._admin_password = salt.hex() + "$" + key.hex()
        self.password_set = True

    def verify_password(self, password: str) -> bool:
        """Проверить пароль"""
        if not self._admin_password or "$" not in self._admin_password:
            logging.warning(
                "Обнаружена неверная строка пароля при проверке. Возвращаем False..."
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
        """Удалить библиотеку из базы данных по точному названию.

        Параметры:
        library_name (str): Название библиотеки."""
        for lib in self._libs_data:
            if lib.name == library_name:
                self._libs_data.remove(lib)
                return
        raise DatabaseException("Библиотека не найдена при удалении!")

    def edit_library_data(
        self, lib_name: str, type_of_edit: str, new_value: str
    ) -> None:
        """Редактировать данные библиотеки в системе.
        Этот метод позволяет безопасно изменять свойства библиотеки, включая название, город и адрес.
        Аргументы:
            lib_name (str): Текущее название библиотеки для редактирования
            type_of_edit (str): Тип редактирования ('name', 'city' или 'address')
            new_value (str): Новое значение для указанного поля
        Исключения:
            ValueError: Если какие-либо параметры пусты/None
            ValueError: Если type_of_edit не 'name', 'city' или 'address'
            ValueError: Если библиотека с указанным именем не найдена
        Возвращает:
            None
        """
        if not lib_name or not type_of_edit or not new_value:
            logging.warning("Пустые параметры при редактировании. Вызываем ValueError...")
            raise ValueError("Все параметры (название, тип, новое значение) должны быть заполнены.")
        if type_of_edit not in VALID_EDIT_TYPES:
            logging.warning(
                f"Неподдерживаемый тип редактирования: {type_of_edit}. Вызываем ValueError..."
            )
            raise ValueError(
                f"Неверный тип редактирования: {type_of_edit}. Должен быть одним из {VALID_EDIT_TYPES}"
            )
        for lib in self._libs_data:
            if lib.name == lib_name:
                if type_of_edit == EDIT_TYPE_NAME:
                    for other_lib in self._libs_data:
                        if other_lib is not lib and other_lib.name == new_value:
                            raise ValueError(
                                f"Другая библиотека с названием '{new_value}' уже существует."
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
                                f"Другая библиотека с адресом '{new_value}' уже существует в том же городе {lib.city}"
                            )
                    lib.address = new_value
                    break
        else:
            logging.warning("Неверное название библиотеки при редактировании. Вызываем ValueError...")
            raise ValueError(f"Библиотека '{lib_name}' не найдена")
