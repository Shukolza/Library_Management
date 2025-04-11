"""Configuration file. Contains DB_PATH & ICON_PATH"""

import sys
import shutil
import logging
from pathlib import Path
from platformdirs import user_data_dir

from logic.gui_utils import resource_path

APP_NAME = "LibraryManagement"
APP_AUTHOR = "Shukolza"

BUNDLED_DB_NAME = "libs_data.json"
bundled_db_path = resource_path(BUNDLED_DB_NAME)

persistent_data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
persistent_data_dir.mkdir(parents=True, exist_ok=True)

PERSISTENT_DB_PATH: Path = persistent_data_dir / BUNDLED_DB_NAME

if not PERSISTENT_DB_PATH.exists() and bundled_db_path.exists():
    try:
        logging.info(f"First run or missing persistent DB. Copying default DB from {bundled_db_path} to {PERSISTENT_DB_PATH}")
        shutil.copy2(bundled_db_path, PERSISTENT_DB_PATH)
    except Exception as e:
        logging.exception(f"Failed to copy initial database: {e}")
        sys.exit(1)

DB_PATH: Path = PERSISTENT_DB_PATH
ICON_PATH: Path = resource_path("./img/book.png")