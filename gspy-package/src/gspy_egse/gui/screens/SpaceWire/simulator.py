"""
DHU Simulator Screen
--------------------

This module registers the DHU Simulator screen in the GUI.
It links the screen entry point to its corresponding widget
implementation (`BrickMk4Service1Widget`) located in
`plugins/juice/BrickMk4_Plugin_service1.py`.

Attributes:
    SCREEN_NAME (str): Display name of the screen in the GUI.
    VERSION (int): Screen version tag.
    MAIN_WIDGET (QWidget): Main widget class implementing the GUI and logic.
"""

from gspy_egse.gui.plugins.juice.BrickMk4_Plugin_service1 import BrickMk4Service1Widget as Widget

SCREEN_NAME = ("Simulator")
VERSION = 1
MAIN_WIDGET = Widget
