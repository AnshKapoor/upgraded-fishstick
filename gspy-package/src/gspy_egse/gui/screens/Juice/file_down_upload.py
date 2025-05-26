try:
    from ...plugins.juice.file_down_upload import FileDownUploadWidget as Widget
except (ValueError, ImportError):
    from plugins.juice.file_down_upload import FileDownUploadWidget as Widget

VERSION = 1
SCREEN_NAME = "File Down-/Upload"
MAIN_WIDGET = Widget
