from gspy_egse.gui.plugins.powersupply import PowerSupplyWidget as Widget
from gspy_egse.gui.utils.screen import DoubleScreen


class MyDoubleScreen(DoubleScreen):
    def __init__(self, window, identifier="DoubleWidget1;DoubleWidget2"):
        DoubleScreen.__init__(self, Widget, window, identifier=identifier,
                              kwargs1={'default_channel': 1}, kwargs2={'default_channel': 2})


VERSION = 1
SCREEN_NAME = "Double Channel"
MAIN_WIDGET = MyDoubleScreen
