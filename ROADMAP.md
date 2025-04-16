# Project Roadmap

This roadmap is a plan of developing Library_Management.
Here is functions plans and steps of development.
*Subject to change.*

---

## Contents

1. [Vision](#vision)
2. [Current status](#current-status)
3. [My priorities](#my-priorities)
4. [Immediate plans](#immediate-plans)
5. [Future plans](#future-plans)
6. [How can you help?](#how-can-you-help)

---

## Vision

Library Management System is a GUI-based application that allows users to manage libraries, books, workers of libraries, and clients.
The system will provide a user-friendly interface for users to perform various operations.
Goal is to be simple, and functional on every work step from Installation to working.

---

## Current status

**The project is now frozen (awaiting pyAuth development (i will add link when git repo ready)), contributors are welcome.**

[*latest release*](https://github.com/Shukolza/Library_Management/releases).***It is latest release, but it's recommended to get program from main branch, it is always stable and contains latest features.***

*Functions implemented:*

* Administrator part:

    * Login with safely stored password (PBKDF2-HMAC-SHA256 with salting)
    * Creating libraries (name, city, address)
    * Libraries list showing
    * Deleting libraries
    * Editing libraries info without losing data

* Worker part:

    **Not implemented yet**

* Client part:

    **Not implemented yet**

---

## My priorities

Priorities depend on these factors (in descending order):

1. **Stability** - I want to make sure that the system is stable and works as it must.
2. **Community requests ([Issues](https://github.com/Shukolza/Library_Management/issues))**:
    1. **Bugs reports**.
    2. **Feature requests**.
3. **Code style and quality** - before adding anything new, i always do code review.
4. **Update documentation** - before adding anything new, i always update documentation.
5. **New features according to plan**
6. **Realization complexity** - sometimes, some simple features may be realized before hard ones.

---

## Immediate plans

*Subject to change*

**Finish administrator GUI development**:
    1. ~~Creating libraries~~ <span style="color: green">Done</span>
    2. ~~Safe authentification~~ <span style="color: green">Done</span>
    3. ~~Libraries list showing~~ <span style="color: green">Done</span>
    4. ~~Deleting libraries~~ <span style="color: green">Done</span>
    5. Editing libraries info without losing data <span style="color: green">Done</span>
    6. (After finishing pyAuth development) Create multi-user authentification with my own pyAuth ***FROZEN. See PyAuth (i'll add link when repo is ready)***
    7. (*After developing worker part*) Creating and attaching worker to library (login, password, library)

---

## Future plans

*Subject to change*

**Will be continued, when I finish pyAuth development (i'll add link when repo ready)**

1. **Worker part development:**
    1. Integrate pyAuth for safe authentification
    2. Registering books (author, creating year, ID, desc, etc.)
    3. Books list showing
    4. Deleting books
    5. Editing books info without losing data
    6. Registering and attaching clients to library (login, password, library)

2. **Client part development:**
    1. Integrate pyAuth for safe authentification
    2. Borrowing books
    3. Borrowed books list showing
    4. Returning books
    5. Delete account

---

## How can you help?

1. **Report bugs**.
Open new [Issue](https://github.com/Shukolza/Library_Management/issues) and describe bug you found. Always send logs (for admin part - "admin_log.txt")
2. **Feature requests**.
Open new [Issue](https://github.com/Shukolza/Library_Management/issues) and describe feature you want to see in app.
3. **Contributing**.
    See [CONTRIBUTING](CONTRIBUTING.md)
