"""Файл конфигурации для приложения. Содержит путь к базе данных и путь к иконке приложения."""

from logic.gui_utils import resource_path
from pathlib import Path

# ИЗМЕНИТЕ ЭТО ДЛЯ СВОЕЙ БД
DB_PATH: Path = resource_path("./libs_data.json")

# ИЗМЕНИТЕ ЭТО ДЛЯ СВОЕЙ ИКОНКИ
ICON_PATH: Path = resource_path("./img/book.png")
