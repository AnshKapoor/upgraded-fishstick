# GSpy

## Requirements
- Windows OS
- Python Modules as listed in main.py
- Python 3.6 to 3.11
  - Update regarding module loading for 3.12ff pending
- Python Windows Embeddable package may be used to avoid systemwide installation
- Qt development environment

## Installation into venv
- Create a venv for the project based on Python 3.11
- open windows cmd in venv: gspy\venv\Scripts
- update pip: python.exe -m pip install --upgrade pip
- install dependencies into venv: pip install pyserial pyqtgraph qtawesome matplotlib pympler pygit2 dill numpy pythonnet
  - It is important to install pyserial and not serial

## Dummy and Device Mode
At startup, the software decides to either use a dummy mode, or connect to a SpaceWire Brick Mk4 depending on if it finds a connection to the brick.
In dummy mode, some features are inaccessible.