"""Вся логика графического интерфейса проекта"""

import logging
from abc import ABC, abstractmethod
import tkinter as tk
import webbrowser as web
from tkinter import ttk
from tkinter import messagebox

from logic.db_logic import (
    LibraryDatabase,
    DatabaseSaveError,
    DatabaseException,
    EDIT_TYPE_NAME,
    EDIT_TYPE_CITY,
    EDIT_TYPE_ADDRESS,
    VALID_EDIT_TYPES
)
from logic.gui_utils import center_window
from config import DB_PATH, ICON_PATH


class AdminMainWindow(tk.Tk):
    """Класс для окна администратора."""

    def __init__(self, libraries_db: LibraryDatabase) -> None:
        logging.debug("Инициализация AdminMainWindow")
        super().__init__()
        self._libraries_db = libraries_db
        self.title("Интерфейс администратора")
        self.geometry("800x600")
        self.create_widgets()
        center_window(self, width=800, height=600)

    def create_widgets(self):
        """Создание всех виджетов окна администратора и установка иконки"""
        logging.debug("Вызов AdminMainWindow create_widgets()")
        set_icon(self)
        title = ttk.Label(
            self,
            text="Добро пожаловать, администратор.\nПожалуйста, выберите действие.",
            font=("Arial", 14),
            anchor="center",
        )
        title.grid(row=0, column=0, columnspan=4, pady=50)

        button_create = ttk.Button(
            self,
            text="Создать новую библиотеку",
            command=lambda: init_create_library_window(self._libraries_db, self),
        )
        button_create.grid(column=0, row=1, pady=10)

        libs_list_button = ttk.Button(
            self,
            text="Список библиотек",
            command=lambda: ViewLibrariesWindow(self._libraries_db, self),
        )
        libs_list_button.grid(column=1, row=1, pady=10, padx=10)

        lib_delete_button = ttk.Button(
            self,
            text="Удалить библиотеку",
            command=lambda: DeleteLibraryWindow(self._libraries_db, self),
        )
        lib_delete_button.grid(row=1, column=2)

        lib_edit_button = ttk.Button(
            self,
            text="Редактировать библиотеку",
            command=lambda: EditLibraryWindow(self._libraries_db, self),
        )
        lib_edit_button.grid(row=1, column=3, sticky="w", padx=(30, 0))

        update_button = ttk.Button(self, text="Обновить БД", command=self.update_db)
        update_button.grid(row=0, column=3, padx=10, pady=10, sticky="ne")

        contact_button = ttk.Button(
            self,
            text="Связаться с разработчиком",
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
        """Перезагрузить БД из файла (путь хранится в ./config.py)"""
        logging.debug("Обновление БД...")
        self._libraries_db.load_data(DB_PATH)
        messagebox.showinfo("Успех", "База данных успешно обновлена") # type: ignore


class LibraryListWindow:
    """Базовый класс для окон, отображающих списки библиотек"""

    def __init__(
        self, db: LibraryDatabase, root: tk.Tk, title: str, geometry: str = "400x600"
    ) -> None:
        self._db = db
        self._libs_info = db.get_readable_libs_info()

        if len(self._libs_info) < 1:
            messagebox.showinfo("Нет библиотек", "Нет доступных библиотек!")  # type: ignore
            return

        self._window = tk.Toplevel(root)
        self._window.title(title)
        self._window.geometry(geometry)

        self._create_base_widgets()
        self._populate_list()
        self._configure_grid()
        center_window(self._window, root)

    def _create_base_widgets(self):
        """Создание общих виджетов"""
        self._title = ttk.Label(self._window, text="Библиотеки", font=("Arial", 14))
        self._title.grid(row=0, column=0, pady=50)

        self._v_scrollbar = tk.Scrollbar(self._window, orient=tk.VERTICAL)
        self._v_scrollbar.grid(column=1, row=1, sticky="ns")

        self._info_text = tk.Text(self._window, yscrollcommand=self._v_scrollbar.set)
        self._info_text.grid(row=1, column=0, sticky="nsew")

        self._v_scrollbar.config(command=self._info_text.yview)  # type: ignore

    def _populate_list(self):
        """Заполнение текста информацией о библиотеках"""
        for info_tuple in self._libs_info:
            self._info_text.insert(
                tk.END, f"{info_tuple[0]} - {info_tuple[1]}, {info_tuple[2]}\n"
            )

    def _configure_grid(self):
        """Настройка весов сетки"""
        self._window.columnconfigure(0, weight=1)
        self._window.rowconfigure(1, weight=1)


class LibraryActionWindow(LibraryListWindow, ABC):
    """Абстрактный базовый класс для окон, выполняющих действия с библиотеками"""

    def __init__(
        self, db: LibraryDatabase, root: tk.Tk, title: str, geometry: str = "400x600"
    ) -> None:
        super().__init__(db, root, title, geometry)
        self._create_selection_widgets()
        self._create_action_widgets()

    def _create_selection_widgets(self) -> None:
        """Создание комбобокса для выбора библиотеки"""
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
        """Создание виджетов, специфичных для действия"""
        pass

    @abstractmethod
    def _handle_action(self) -> None:
        """Обработка основного действия окна"""
        pass

    def _get_selected_library(self) -> tuple[str, str, str] | None:
        """Получить информацию о выбранной библиотеке / None, если ничего не выбрано"""
        selected_index = self._lib_combobox.current()
        if selected_index < 0:
            return None
        return self._libs_info[selected_index]


class ViewLibrariesWindow(LibraryListWindow):
    """Окно для просмотра списка библиотек"""

    def __init__(self, db: LibraryDatabase, root: tk.Tk) -> None:
        super().__init__(db, root, "Список библиотек")


class DeleteLibraryWindow(LibraryActionWindow):
    """Окно для удаления библиотек"""

    def __init__(self, db: LibraryDatabase, root: tk.Tk) -> None:
        super().__init__(db, root, "Удаление библиотеки")
        self._window.geometry("600x800")

    def _create_action_widgets(self) -> None:
        """Добавление виджетов, специфичных для удаления"""
        self._delete_button = ttk.Button(
            self._window, text="Удалить", command=self._handle_action
        )
        self._delete_button.grid(row=3, column=0, pady=50)
        self._window.rowconfigure(3, weight=1)

    def _handle_action(self) -> None:
        """Обработка удаления"""
        library = self._get_selected_library()
        if not library:
            show_custom_message(
                self._window, "Ошибка", "Пожалуйста, выберите библиотеку для удаления!", "error"
            )
            return

        name = library[0]
        try:
            self._db.delete_library(name)
            self._db.save_data(DB_PATH)
            show_custom_message(
                self._window,
                "Успех",
                f"Библиотека {self._lib_combobox.get()} успешно удалена",
            )
            self._window.destroy()
        except DatabaseException:
            show_custom_message(
                self._window,
                "Ошибка",
                f"Не удалось удалить библиотеку '{name}'. Возможно, она уже удалена. Пожалуйста, нажмите 'Обновить БД'",
                "error",
            )


class EditLibraryWindow(LibraryActionWindow):
    """Окно для редактирования информации о библиотеках без потери данных"""

    def __init__(self, db: LibraryDatabase, root: tk.Tk) -> None:
        super().__init__(db, root, "Редактирование библиотеки")
        self._window.geometry("600x800")
        messagebox.showinfo("Примечание", "Такое редактирование библиотеки БЕЗОПАСНО. Данные не будут потеряны! \n :)")  # type: ignore

    def _create_action_widgets(self) -> None:
        """Добавление виджетов, специфичных для редактирования"""
        self._edit_button = ttk.Button(
            self._window, text="Редактировать", command=self._handle_action
        )
        self._edit_button.grid(row=3, column=0, pady=50)
        self._window.rowconfigure(3, weight=1)

    def _handle_action(self) -> None:
        """Обработка редактирования библиотек"""
        library = self._get_selected_library()
        if not library:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите библиотеку для редактирования!")  # type: ignore
            return
        old_name, old_city, old_address = library

        self._edit_window = tk.Toplevel(self._window)
        self._edit_window.title("Редактировать")
        self._edit_window.geometry("300x300")

        title = ttk.Label(
            self._edit_window,
            text="Пожалуйста, выберите, что вы хотите редактировать",
            anchor="center",
        )
        title.grid(column=0, row=0, sticky="nsew")

        options_for_display = ["Имя", "Город", "Адрес"]
        self._edit_type_map = {
            "Имя": EDIT_TYPE_NAME,
            "Город": EDIT_TYPE_CITY,
            "Адрес": EDIT_TYPE_ADDRESS,
        }
        chosen_option_display = tk.StringVar(self._window)

        choose_combobox = ttk.Combobox(
            self._edit_window,
            textvariable=chosen_option_display,
            values=options_for_display,
        )
        choose_combobox["state"] = "readonly"
        choose_combobox.grid(column=0, row=1, sticky="nsew")

        new_value_entry_title = ttk.Label(
            self._edit_window,
            text=f"Пожалуйста, введите новое значение",
        )
        new_value_entry_title.grid(column=0, row=2)
        new_value_entry = ttk.Entry(self._edit_window)
        new_value_entry.grid(column=0, row=3)

        choose_button = ttk.Button(
            self._edit_window,
            text="Редактировать",
            command=lambda: self._perform_edit(
                old_name,
                self._edit_type_map.get(chosen_option_display.get()),
                new_value_entry.get(),
                old_address,
                old_city,
            ),
        )
        choose_button.grid(column=0, row=4)

        current_values_label = ttk.Label(
            self._edit_window,
            text=f"Текущие значения:\nИмя: {old_name}\nГород: {old_city}\nАдрес: {old_address}",
        )
        current_values_label.grid(column=0, row=5)

        # Настройка сетки
        self._edit_window.columnconfigure(0, weight=1)

        # Центрирование окна
        center_window(self._edit_window, self._window)

    def _refresh_lib_list(self):
        """Обновить список библиотек в тексте и комбобоксе"""
        logging.debug("Обновление списка библиотек...")
        self._libs_info = self._db.get_readable_libs_info()

        # Обновление текста
        try:
            self._info_text.config(state=tk.NORMAL)
            self._info_text.delete("1.0", tk.END)

            for info_tuple in self._libs_info:
                self._info_text.insert(
                    tk.END, f"{info_tuple[0]} - {info_tuple[1]}, {info_tuple[2]}\n"
                )
            self._info_text.config(state=tk.DISABLED)
        except tk.TclError as e:  # type: ignore
            logging.exception("Ошибка обновления текста:")

        # Обновление комбобокса
        try:
            libraries_to_choose = [
                f"{info[0]} - {info[1]}, {info[2]}" for info in self._libs_info
            ]
            self._lib_combobox.config(values=libraries_to_choose)
            self._lib_combobox.set("")  # Сброс выбранного
            # убедитесь, что он все еще только для чтения
            self._lib_combobox["state"] = "readonly"
        except tk.TclError as e:  # type: ignore
            logging.exception(f"Ошибка обновления виджета Combobox:")

    def _perform_edit(
        self,
        lib_name: str,
        type: str | None,
        new_value: str,
        old_address: str,
        old_city: str,
    ) -> None:
        """Редактировать информацию о библиотеке"""

        def get_old_value(type: str) -> str:
            """Функция для получения старого значения типа"""
            if type == EDIT_TYPE_NAME:
                return lib_name
            if type == EDIT_TYPE_CITY:
                return old_city
            return old_address

        if not type:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите, что редактировать!")  # type: ignore
            return
        if not new_value:
            messagebox.showerror("Ошибка", "Пожалуйста, введите новое значение!")  # type: ignore
            return
        if type not in VALID_EDIT_TYPES:
            messagebox.showerror("Ошибка", f"Недопустимый тип редактирования {type}") # type: ignore
            return
        old_value = get_old_value(type)
        if new_value == old_value:
            show_custom_message(
                self._edit_window, "Ошибка", "Новое значение такое же, как старое!", "error"
            )
            return

        try:
            self._db.edit_library_data(lib_name, type, new_value)
        except ValueError as e:
            show_custom_message(
                self._edit_window,
                "Ошибка",
                f"Произошла ошибка при редактировании:\n{e}\n если вы не знаете, что это и как это исправить, обратитесь к системному администратору",
                "error",
            )
            self._edit_window.destroy()
            return
        show_custom_message(
            self._edit_window, "Успех", "Библиотека успешно отредактирована!"
        )
        try:
            self._db.save_data(DB_PATH)
        except DatabaseSaveError as e:
            logging.exception("Не удалось сохранить данные в _perform_edit")
            show_custom_message(
                self._edit_window,
                "Ошибка",
                f"Не удалось сохранить изменения!\n{e}\nОбратитесь к системному администратору.",
                "error"
            )
            return
        else:
            self._refresh_lib_list()
        self._edit_window.destroy()


def set_icon(window: tk.Tk) -> None:
    """Установка иконки окна из пути, указанного в ./config.py"""
    try:
        logging.info(f"Попытка установки иконки из {ICON_PATH}")
        icon = tk.PhotoImage(file=ICON_PATH)
        window.tk.call("wm", "iconphoto", window._w, icon)  # type: ignore # Альтернативный способ установки иконки
        window.icon = icon  # type: ignore # Сохранение ссылки, чтобы она не была удалена сборщиком мусора
    except tk.TclError as e:
        logging.error(f"ОШИБКА установки иконки\n{e}")


def show_custom_message(
    parent: tk.Toplevel | tk.Tk, title: str, message: str, msg_type: str = "info"
) -> None:
    """
    Показывает пользовательское модальное окно сообщения, центрированное относительно родителя
    :param msg_type: поддерживаются 'info' и 'error'. Влияет только на иконку.
    """
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.transient(parent)
    dialog.resizable(False, False)

    icon_label = None
    if msg_type == "error":
        try:
            # Попытка загрузить иконку ошибки tkinter
            icon_label = ttk.Label(dialog, image="::tk::icons::error", padding=(10, 10))
        except tk.TclError:
            logging.warning("Стандартная иконка ошибки не найдена")
    elif msg_type == "info":
        try:
            # Попытка загрузить иконку информации tkinter
            icon_label = ttk.Label(
                dialog, image="::tk::icons::information", padding=(10, 10)
            )
        except tk.TclError:
            logging.warning("Стандартная иконка информации не найдена")

    if icon_label:
        icon_label.grid(row=0, column=0, sticky="ns", padx=(10, 0))

    message_label = ttk.Label(dialog, text=message, padding=(10, 10), wraplength=300)

    text_column = 1 if icon_label else 0
    button_columnspan = 2 if icon_label else 1
    message_label.grid(row=0, column=text_column, sticky="nsew", padx=(0, 10))

    ok_button = ttk.Button(dialog, text="OK", command=dialog.destroy, width=10)
    ok_button.grid(row=1, column=0, columnspan=button_columnspan, pady=(0, 10))
    ok_button.focus_set()

    # Центрирование
    center_window(dialog, parent)

    # --- Модальность ---
    dialog.grab_set()
    dialog.wait_window()


def set_password(
    libraries_db: LibraryDatabase,
    password_window: tk.Toplevel,
    password_entry: ttk.Entry,
) -> bool:
    """Установить пароль администратора"""
    password = password_entry.get()
    try:
        libraries_db.update_admin_password(password)
        try:
            libraries_db.save_data(DB_PATH)
        except DatabaseSaveError as e:
            logging.exception("Ошибка сохранения БД")
            messagebox.showerror(  # type: ignore
                "Ошибка",
                f"Не удалось сохранить пароль!\n{e}\n Обратитесь к системному администратору.\n Вы можете продолжить работу, но это не рекомендуется",
            )
        password_window.destroy()
        return True
    except ValueError:
        logging.warning("Произошла ошибка пустого пароля")
        show_custom_message(
            password_window, "Ошибка", "Пароль не может быть пустым", "error"
        )
        password_entry.focus_set()
        return False


def check_password(
    password_entry: ttk.Entry,
    libraries_db: LibraryDatabase,
    password_window: tk.Toplevel,
) -> bool:
    """Проверить пароль администратора"""
    password = password_entry.get()
    if libraries_db.verify_password(password):
        password_window.destroy()
        return True

    logging.warning("Введен неправильный пароль")
    show_custom_message(password_window, "Ошибка", "Неправильный пароль, попробуйте еще раз", "error")
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
    """Создать новую библиотеку и добавить информацию в БД"""
    try:
        libraries_db.add_library(name, city, address)
        try:
            libraries_db.save_data(DB_PATH)
        except DatabaseSaveError as e:
            logging.exception("Ошибка сохранения БД")
            messagebox.showerror(  # type: ignore
                "Ошибка",
                f"Не удалось сохранить библиотеку! Она будет потеряна при закрытии приложения!\n{e}\n Обратитесь к системному администратору.\n Вы можете продолжить работу, но это не рекомендуется",
            )
        window.destroy()
    except ValueError as error:
        show_custom_message(window, "Ошибка", str(error), "error")
        for entry in entries:
            entry.delete(0, tk.END)
        return
    messagebox.showinfo(  # type:ignore
        f"Успех", f"Библиотека '{name}' в {city}, {address} успешно создана"
    )
    window.destroy()


def init_create_library_window(libraries_db: LibraryDatabase, root: tk.Tk) -> None:
    """Создать окно для создания библиотеки"""
    create_library_window = tk.Toplevel()
    create_library_window.title("Создание библиотеки")

    library_name_label = ttk.Label(create_library_window, text="Название новой библиотеки")
    library_name_label.grid(column=0, row=0, padx=10, pady=10)

    library_name_entry = ttk.Entry(create_library_window)
    library_name_entry.grid(column=0, row=1, padx=10, pady=10)

    library_city_label = ttk.Label(create_library_window, text="Город новой библиотеки")
    library_city_label.grid(column=1, row=0, padx=10, pady=10)

    library_city_entry = ttk.Entry(create_library_window)
    library_city_entry.grid(column=1, row=1, padx=10, pady=10)

    library_address_label = ttk.Label(create_library_window, text="Адрес новой библиотеки")
    library_address_label.grid(column=2, row=0, padx=10, pady=10)

    library_address_entry = ttk.Entry(create_library_window)
    library_address_entry.grid(column=2, row=1, padx=10, pady=10)

    submit_button = ttk.Button(
        create_library_window,
        text="СОЗДАТЬ",
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
    Показывает модальное окно для ввода пароля
    :return: True если пароль верный, False в противном случае
    """
    logging.debug("ask_for_password: Создание временного корня...")
    dialog_root = tk.Tk()
    dialog_root.geometry("1x1+-100+-100")  # Скрыть, но нельзя использовать withdraw

    logging.debug("ask_for_password: Создание диалогового окна Toplevel...")
    password_dialog = tk.Toplevel(dialog_root)
    password_dialog.title("Аутентификация")
    password_dialog.transient(dialog_root)

    password_ok = False

    def on_submit():
        nonlocal password_ok
        logging.debug("ask_for_password: Нажата кнопка отправки.")
        is_ok = False
        if db.password_set:
            is_ok = check_password(password_entry, db, password_dialog)
        else:
            is_ok = set_password(db, password_dialog, password_entry)

        if is_ok:
            logging.debug("ask_for_password: Пароль верный, установка результата в True.")
            password_ok = True
            # окно уничтожается в check/set _password

    def on_close():
        nonlocal password_ok
        logging.debug("ask_for_password: Диалоговое окно закрыто пользователем.")
        password_ok = False
        password_dialog.destroy()

    password_dialog.protocol("WM_DELETE_WINDOW", on_close)

    logging.debug("ask_for_password: Создание виджетов...")
    password_dialog.geometry("300x150")
    password_label = ttk.Label(
        password_dialog,
        text=(
            "Введите пароль администратора:"
            if db.password_set
            else "Создайте новый пароль администратора"
        ),
    )
    password_label.grid(column=0, row=0, padx=10, pady=10)

    password_entry = ttk.Entry(password_dialog, show="*")
    password_entry.grid(column=0, row=1, padx=10, pady=10, sticky="ew")
    password_entry.focus_set()

    password_button = ttk.Button(password_dialog, text="Ввести", command=on_submit)
    password_button.grid(column=0, row=2, padx=10, pady=20)

    # Центрирование
    center_window(password_dialog, width=300, height=150)

    logging.info("ask_for_password: Установка модальности...")
    logging.debug("ask_for_password: Вызов grab_set()...")
    password_dialog.grab_set()
    logging.debug("ask_for_password: Вызов wait_window()")
    password_dialog.wait_window()
    logging.debug("ask_for_password: wait_window завершен.")

    logging.debug("ask_for_password: уничтожение временного корня...")
    dialog_root.destroy()
    logging.debug(f"ask_for_password: возвращение {password_ok}")

    return password_ok
