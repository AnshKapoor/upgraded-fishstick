try:
    from ...plugins.juice.housekeeping import HousekeepingWidget as Widget
except (ValueError, ImportError):
    from plugins.juice.housekeeping import HousekeepingWidget as Widget

VERSION = 1
SCREEN_NAME = "Housekeeping"
MAIN_WIDGET = Widget
