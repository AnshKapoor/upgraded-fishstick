from PyQt6 import QtCore, QtWidgets, QtGui, uic
from pathlib import Path
from contextlib import suppress
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from typing import *

from gspy_egse.gui.plugins.juice.spacewire import SpaceWireConnection
from gspy_egse.gui.utils.plugin import WidgetWithExtension, Setting
from gspy_egse.gui.utils.misc import Extendable
from gspy_egse.gui.utils.widget import (
    call_in_main_thread, delay_in_main_thread, async_in_main_thread,
    select_file, ActivationListener
)
from gspy_egse.gui.utils.recorder import Recordable
from gspy_egse.gui.hardware_modules.spacewire import SpaceWire
from gspy_egse.gui.hardware_modules.juice_lib.ramfs import RamFs

with suppress(Exception):
    from PIL import Image



from importlib.resources import files, as_file  # stdlib, Python ≥3.9

pkg = "gspy_egse.gui.ui"
ui_name = "fileDownUp.ui"

class RequirePlugins(WidgetWithExtension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, ext_cls=SpaceWireConnection, identifier="_", sub_exts=[
            RamFs
        ], **kwargs)


class FileDownUploadWidget(WidgetWithExtension, Recordable):
    """
    :type spw: SpaceWire | RamFs
    :type connection: SpaceWireConnection
    """

    def __init__(self, *args, filename_down="file.img", filename_down_dpu="file.img", filename_up="file.img",
                 filename_up_dpu="file.img", **kwargs):
        self.spw, self.connection = (None,) * 2

        self._params = (filename_down, filename_down_dpu, filename_up, filename_up_dpu)
        super().__init__(*args, plugin_name="SpaceWire", ext_cls=SpaceWireConnection, singleton=False, **kwargs)

    @property
    def filename_down(self):
        return self.filepath_down.name

    @property
    def filepath_down(self):
        return Path(self._filename_down.value)

    def set_filepath_down(self, filepath: Path):
        self._filename_down.set(filepath.absolute())

    @property
    def filename_up(self):
        return self.filepath_up.name

    @property
    def filepath_up(self):
        return Path(self._filename_up.value)

    def set_filepath_up(self, filepath: Path):
        self._filename_up.set(filepath.absolute())

    def _delay_init(self, extension=None, _=False):
        self.inherit_settings_from_parent(extension)
        self.connection = extension
        print(f"connection for filedownload is: {self.connection}")
        self.spw = self.connection.hardware #hardware = RecordableSpaceWire-> SpaceWire

        ui_res = files(pkg).joinpath(ui_name)
        with as_file(ui_res) as ui_path:
            self.ui = uic.loadUi(str(ui_path), self)
        # self.ui = uic.loadUi("gspy_egse/gui/ui/fileDownUp.ui", self)
        self._filename_down = self.add_setting(
            name="filename_down_local",
            default=self._params[0],
            in_settings=False,
            listener=self.update_inputs,
            type_=Setting.STRING,
            widget_id=self.identifier
        )
        self.filename_down_dpu = self.add_setting(
            name="filename_down_dpu",
            default=self._params[1],
            in_settings=False,
            listener=self.update_inputs,
            type_=Setting.STRING,
            widget_id=self.identifier
        )
        self._filename_up = self.add_setting(
            name="filename_up_local",
            default=self._params[2],
            in_settings=False,
            listener=self.update_inputs,
            type_=Setting.STRING,
            widget_id=self.identifier
        )
        self.filename_up_dpu = self.add_setting(
            name="filename_up_dpu",
            default=self._params[3],
            in_settings=False,
            listener=self.update_inputs,
            type_=Setting.STRING,
            widget_id=self.identifier
        )
        self.update_inputs()

        self.make_settings_btn(self.settingsButton)

        self.down_file_select_button.clicked.connect(
            lambda: select_file(self._filename_down.set, self.filepath_down.parent.absolute, create_new=True)
        )
        self.up_file_select_button.clicked.connect(
            lambda: select_file(self._filename_up.set, self.filepath_up.parent.absolute)
        )

        self.down_button.clicked.connect(self.start_download)
        self.up_button.clicked.connect(self.start_upload)

        self.table = self.table  # type: QtWidgets.QTableWidget
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().hide()
        self.table.setColumnCount(32)
        self.table.setRowCount(32)
        for i in range(self.table.columnCount()):
            self.table.setColumnWidth(i, int(25 * self.logicalDpiX() / 96.0))
        self.fill_table(bytes())  # (bytes(range(256)))

        self.text_browser.setFont(QtGui.QFont("Source Code Pro", 12))

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.tab_img.layout().addWidget(self.canvas)

        self.spw.file_list()

    def fill_table(self, data: bytes):
        self.table.hide()
        n = self.table.columnCount()
        m = self.table.rowCount()
        if len(data) < n * m:
            data += b'\x00' * (n * m - len(data))
        for i in range(n):
            for j in range(m):
                item = QtWidgets.QTableWidgetItem("%02X" % data[i * n + j])
                item.setFont(QtGui.QFont("Source Code Pro", 11))
                self.table.setItem(i, j, item)
        self.table.show()

    def start_upload(self):
        self.spw.file_upload(self.filename_up_dpu.value, self.filepath_up, wait=False, listener=self.upload_listener)

        self.up_button.setText("Uploading...")
        self.up_button.setEnabled(False)

    def start_download(self, button=None):
        self._start_download(button is None, self.filename_down_dpu.value, self.filepath_down)

    @Recordable.intercept_on_playback()
    @Recordable.record_method()
    def _start_download(self, button_none, remotefile, localfile, play_back=False):
        _ = play_back  # unused

        r = self.spw.file_download(remotefile, localfile, listener=self.download_listener)

        if button_none:
            return

        if r is None:
            self.down_button.setText("Error")
        else:
            self.down_button.setText("Downloading...")
        self.down_button.setEnabled(False)

    def update_inputs(self, *args, **kwargs):
        delay_in_main_thread(1, self._update_inputs, args=args, kwargs=kwargs)

    def _update_inputs(self, *_, **kwargs):
        if kwargs.get('init', False):
            return
        # TODO Check why File Selection Dialog keeps reappearing
        # TODO Check why filename down is reset when filename_up is set to new value
        # TODO Check why clicking on right field in UP to DPU sets the left fields value
        self.down_local_input.setText(".../" + self.filename_down)
        self.up_local_input.setText(".../" + self.filename_up) # Up to DPU / Down from GSE left
        self.down_remote_input.setText(self.filename_down_dpu.value)
        self.up_remote_input.setText(self.filename_up_dpu.value)

    def upload_listener(self):
        self.up_button.setText("Upload")
        self.up_button.setEnabled(True)

    def download_listener(self, downdata: bytes = None, downfile: Optional[Path] = None):
        self.down_button.setText("Download")
        self.down_button.setEnabled(True)
        if downdata is not None:
            async_in_main_thread(self.fill_table,
                                 args=(downdata[:self.table.columnCount() * self.table.rowCount()],))
            async_in_main_thread(self.text_browser.setText, (downdata,))

            self.figure.clear()
            ax = self.figure.add_subplot(111)

            # plot data
            ax.imshow(downdata)
            ax.axis('off')

            # refresh canvas
            self.canvas.draw()
        elif downfile is not None:
            with open(downfile, 'r') as f:
                try:
                    d = f.read()
                    async_in_main_thread(self.text_browser.setText, (d,))
                except UnicodeDecodeError:
                    async_in_main_thread(self.text_browser.setText, ("Binary File",))
            with open(downfile, 'rb') as f:
                async_in_main_thread(self.fill_table, args=(f.read(
                    self.table.columnCount() * self.table.rowCount()),))
            with suppress(OSError):
                img = mpimg.imread(str(downfile.absolute()))

                self.figure.clear()
                ax = self.figure.add_subplot(111)

                # plot data
                ax.imshow(img)
                ax.axis('off')

                # refresh canvas
                self.canvas.draw()


VERSION = 1
NAME = "File Down-/Upload"
BACKGROUND_TASKS = [RequirePlugins]
