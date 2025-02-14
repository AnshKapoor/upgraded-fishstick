try:
    from ..plugins.spi_interface import SpiInterfaceWidget as Widget
except (ValueError, ImportError):
    from plugins.spi_interface import SpiInterfaceWidget  as Widget

VERSION = 1
SCREEN_NAME = "SPI Interface"
MAIN_WIDGET = Widget
