from logic.db_logic import resource_path
from pathlib import Path

# CHANGE THIS TO USE CUSTOM DB / ИЗМЕНИТЕ ЭТО ДЛЯ СВОЕЙ БД
DB_PATH: Path = resource_path("./libs_data.json")
# CHANGE THIS TO USE CUSTOM ICON / ИЗМЕНИТЕ ЭТО ДЛЯ СВОЕЙ ИКОНКИ
ICON_PATH: Path = resource_path("./img/book.png")
