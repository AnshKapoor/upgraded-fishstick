try:
    from ...plugins.juice.BrickMk4_Plugin_Transmit import BrickMk4Widget as Widget
except (ValueError, ImportError):
    from plugins.juice.BrickMk4_Plugin_Transmit import BrickMk4Widget  as Widget

VERSION = 1
SCREEN_NAME = "SpaceWire Testing"
MAIN_WIDGET = Widget
