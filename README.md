# Library Management GUI System

[![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/Shukolza/Library_Management?style=flat-square)](https://github.com/Shukolza/Library_Management/tags)

![GitHub License](https://img.shields.io/github/license/Shukolza/Library_Management)

![app logo](/img/book.png)

## Short description

This is a simple GUI system for a library management system. It includes several interfaces:

* *Administrator* - for creating and managing **libraries**
* *Worker* - for managing **books** and **clients** inside library
* *Client* - for borrowing and returning **books**

---

## Contents

### 1. [About The Project](#about-the-project)

### 2. [Installation](#installation)

### 3. [Usage](#usage)

### 4. [Configuration](#configuration)

### 5. [Project roadmap](#roadmap)

### 6. [Contribution](#contribution)

### 7. [License](#license)

---

## About The Project

This project is a desktop application designed to provide a basic system for managing library information. Currently, it features the Administrator Graphical User Interface (GUI), built using Python and the standard Tkinter library, allowing for a native look and feel without external dependencies for the UI.

The core idea is to offer a straightforward tool for administrators to manage library records (such as adding new library locations). Key aspects of the current implementation include:

* **Secure Authentication:** Administrator access is protected using a hashed password mechanism (PBKDF2-HMAC-SHA256 with salting) to prevent unauthorized access.
* **Simple Data Storage:** Library information and the administrator password hash are stored locally in a `libs_data.json` file, making the application self-contained and easy to set up for basic use cases.
* **Activity Logging:** Key actions and potential errors are logged to a `(part_name)_log.txt` file for monitoring and debugging purposes.

As a pet project, it serves as a practical exercise in GUI development with Tkinter, data persistence using JSON, implementing basic security practices, OOP with inheritance and abstract classes, and structuring a multi-component Python application (with planned Client and Worker modules). It aims to solve the simple problem of needing a dedicated interface for basic library data management without requiring a complex database setup.

---

## Installation

To run the application, you'll need Python 3 installed on your system. No external dependencies needed!

### From source code

**Clone repository:**

``` bash
git clone https://github.com/Shukolza/Library_Management.git && cd Library_Management
```

### From executable (only admin part)

**Go to latest release page**

[latest release](https://github.com/Shukolza/Library_Management/releases/tag/v0.4.0-admin-beta)

**Download executable for your OS**

*To launch on linux*: ```./LINUX-EXECUTABLE```

---

## Usage (if installed from source code)

### Run interface you need

**For administrator:** (Mostly implemented)

``` bash
python3 administrator_gui.py
```

**For worker:** (Not implemented yet)

``` bash
python3 worker.py
```

**For client:** (Not implemented yet)

``` bash
python3 client.py
```

---

## Configuration

* **DB and icon paths configuration**
All paths for external files of application are stored in (config.py). The default content:

``` python
"""Configuration file. Contains DB_PATH & ICON_PATH"""

from logic.db_logic import resource_path
from pathlib import Path

# CHANGE THIS TO USE CUSTOM DB / ИЗМЕНИТЕ ЭТО ДЛЯ СВОЕЙ БД
DB_PATH: Path = resource_path("./libs_data.json")

# CHANGE THIS TO USE CUSTOM ICON / ИЗМЕНИТЕ ЭТО ДЛЯ СВОЕЙ ИКОНКИ
ICON_PATH: Path = resource_path("./img/book.png")

```

* **The database file**
Database file is libs_data.json
All instruments you need to manage it is in GUI, but you can also change it manually.
The default contents:

``` JSON
{
    "libraries_data": [],
    "administrator_password": ""
}
```

---

## Roadmap

See the [ROADMAP](ROADMAP.md) file

---

## Contribution

Contributors are always welcome - see the [CONTRIBUTING](CONTRIBUTING.md) file for details.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
