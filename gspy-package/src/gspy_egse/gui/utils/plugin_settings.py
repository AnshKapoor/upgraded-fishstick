import json
from datetime import datetime
from PyQt6 import QtCore
from threading import Lock
from contextlib import suppress


class PluginSettingsSyncWrite:
    def __init__(self, path):
        self.path = path
        self.json = path  # type: str
        if self.json.endswith(".py"):
            self.json = self.json[:-3]
        self.json += ".config.json"

    def _write(self, data, key, value):
        if isinstance(key, list):
            data_cp, key_cp = data, key
            while len(key_cp) > 1:
                try:
                    data_cp_tmp = data_cp[key_cp[0]]
                    assert isinstance(data_cp_tmp, dict)
                    key_cp = key_cp[1:]
                    data_cp = data_cp_tmp
                except KeyError:
                    data_cp[key_cp[0]] = dict()
                    data_cp = data_cp[key_cp[0]]
                    key_cp = key_cp[1:]
            data_cp[key_cp[0]] = value
        else:
            data[key] = value
        with open(self.json, 'w') as file:
            json.dump(data, file, indent=2)

        return value

    @staticmethod
    def setting_to_string(setting):
        if isinstance(setting, list):
            setting = [str(s) for s in setting]
        else:
            setting = str(setting)
        return setting

    def get(self, setting, default=None):
        setting = setting_to_string(setting)
        try:
            with open(self.json) as file:
                data = json.load(file)
        except FileNotFoundError:
            return self._write(dict(), setting, default)

        try:
            if isinstance(setting, list):
                data_cp, setting_cp = data, setting
                while len(setting_cp) > 1:
                    data_cp = data_cp[setting_cp[0]]
                    setting_cp = setting_cp[1:]
                return data_cp[setting_cp[0]]
            return data[setting]
        except KeyError:
            return self._write(data, setting, default)

    def set(self, setting, value):
        setting = setting_to_string(setting)
        try:
            with open(self.json) as file:
                data = json.load(file)
        except FileNotFoundError:
            data = dict()

        return self._write(data, setting, value)


def setting_to_string(setting):
    if isinstance(setting, list):
        setting = [str(s) for s in setting]
    else:
        setting = str(setting)
    return setting


class PluginSettings(QtCore.QObject):
    def __init__(self, path, write_null=False):
        QtCore.QObject.__init__(self)
        self.write_null = write_null
        self.path = path
        self.json = path  # type: str
        if self.json.endswith(".py"):
            self.json = self.json[:-3]
        self.json += ".config.json"
        self.data = None
        self.timer = None
        self.write_time = None
        self.write_lock = Lock()

    def get(self, setting, default=None):
        setting = setting_to_string(setting)

        if self._load_if_none():
            return self.set(setting, default)

        try:
            if isinstance(setting, list):
                data, setting_cp = self.data, setting
                while len(setting_cp) > 1:
                    data = data[setting_cp[0]]
                    setting_cp = setting_cp[1:]
                return data[setting_cp[0]]
            return self.data[setting]
        except KeyError:
            return self.set(setting, default)

    def set(self, setting, value):
        if value is None and not self.write_null:
            return value  # we dont need to write 'null'
        setting = setting_to_string(setting)

        self.data = self.data if self.data is not None else dict()
        if isinstance(setting, list):
            data, key_cp = self.data, setting
            while len(key_cp) > 1:
                try:
                    data_cp_tmp = data[key_cp[0]]
                    assert isinstance(data_cp_tmp, dict)
                    key_cp = key_cp[1:]
                    data = data_cp_tmp
                except KeyError:
                    data[key_cp[0]] = dict()
                    data = data[key_cp[0]]
                    key_cp = key_cp[1:]
            data[key_cp[0]] = value
        else:
            self.data[setting] = value
        self.write_later()

        return value

    def rm(self, setting):
        setting = setting_to_string(setting)

        if isinstance(setting, list):
            data, setting_cp = self.data, setting
            while len(setting_cp) > 1:
                data = data[setting_cp[0]]
                setting_cp = setting_cp[1:]
            val = data.pop(setting_cp[0], None)
            if len(setting) > 1:
                sub = self.get(setting[:-1])
                if (isinstance(sub, list) or isinstance(sub, dict)) and len(sub) == 0:
                    self.rm(setting[:-1])  # also clear empty parents
        else:
            val = self.data.pop(setting, None)

        self.write_later()

        return val

    @QtCore.pyqtSlot()
    def write(self):
        with self.write_lock:
            with suppress(Exception):
                if isinstance(self.sender(), QtCore.QTimer):
                    del self.timer
                    self.timer = None

            self.write_time = datetime.now()
            with open(self.json, 'w') as file:
                json.dump(self.data, file, indent=2)

    def write_later(self, timeout=100):
        with self.write_lock:
            if self.timer is not None and self.timer.isActive():
                return  # Timer is running
            if self.write_time is None or (datetime.now() - self.write_time).total_seconds() * 1000 > timeout:
                timeout = 1
            self.timer = QtCore.QTimer(self)
            self.timer.timeout.connect(self.write)
            self.timer.setSingleShot(True)
            self.timer.start(timeout)

    def _load_if_none(self):
        if self.data is not None:
            return False
        try:
            with open(self.json) as file:
                self.data = json.load(file)
            return False
        except FileNotFoundError:
            return True
