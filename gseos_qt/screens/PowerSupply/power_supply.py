try:
    from ...plugins.powersupply import PowerSupplyWidget as Widget
except (ValueError, ImportError):
    from plugins.powersupply import PowerSupplyWidget as Widget

VERSION = 1
SCREEN_NAME = "Single Channel"
MAIN_WIDGET = Widget
