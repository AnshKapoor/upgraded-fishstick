import time
import qtawesome as qta

import gspy_egse.gui.globalvars as glob

import copy
import pickle
import gzip
import os
from typing import *
from datetime import datetime
from PyQt6.uic import loadUi
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from functools import wraps
from contextlib import suppress
from gspy_egse.gui.utils.misc import WrappedMessageHandler, call_async
import logging
RECORDING_FILTER = "GSpy Recording (*.gspy)"

logger = logging.getLogger(__name__)
class StolenObject:
    def __init__(self, original, intercept, replacement):
        self.original = original
        self.intercept = intercept
        self.replacement = replacement

    def __getattr__(self, item):
        if item in self.intercept:
            return self.replacement
        return object.__getattribute__(self.original, item)


class RecorderWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .widget import select_file

        self.ui = loadUi("gspy_egse/gui/ui/recorder.ui", self)
        self.list_record: QListView = self.list_record
        self.list_play: QListView = self.list_play
        self.play.setIcon(qta.icon("fa6s.play", color="green"))
        self.play.setText("")
        self.play.clicked.connect(self.play_click)
        self.f_forward.setIcon(qta.icon("fa6s.forward-fast", color="green"))
        self.f_forward.setText("")
        self.f_forward.clicked.connect(self.f_forward_click)
        self.record.setIcon(qta.icon("fa6s.circle", color="red"))
        self.record.setText("")
        self.record.clicked.connect(self.record_click)
        self.stop.setIcon(qta.icon("fa6s.stop"))
        self.stop.setText("")
        self.stop.clicked.connect(self.stop_click)
        self.stop.setEnabled(False)
        self.step.setIcon(qta.icon("fa6s.forward-step", color="orange"))
        self.step.setText("")
        self.step.clicked.connect(self.step_click)

        glob.Recorder.finished.connect(self.finished)
        glob.Recorder.recording_changed.connect(self.on_new_recording)

        self.action_save.triggered.connect(lambda: select_file(
            self.save_file,
            type_filter=RECORDING_FILTER,
            path=glob.Settings.value("record_path", "."),
            create_new=True
        ))
        self.action_load.triggered.connect(lambda: select_file(
            self.load_file,
            type_filter=RECORDING_FILTER,
            path=glob.Settings.value("record_path", ".")
        ))

        self.record_name.textChanged.connect(self.update_name)

        self.list_record.setModel(glob.Recorder.record_items_model)
        self.on_new_recording()
        with suppress(Exception):
            self.restoreGeometry(glob.Settings.value("recorder_geometry", None))

        self.status_label = QLabel("Start or Load Recording", self)
        self.statusbar.addPermanentWidget(self.status_label, 1)
        glob.Recorder.m_h = StolenObject(glob.Recorder.m_h, ["info", "success"], self.status_set)

        self.show()

    def status_set(self, message):
        self.status_label.setText(message)

    def update_name(self, *_):
        glob.Recorder.recording.name = self.record_name.text()

    @pyqtSlot(str)
    def save_file(self, file: str):
        # store the object
        with gzip.open(file, 'wb') as f:
            pickle.dump(glob.Recorder.recording.to_dump(), f)

        glob.Settings.setValue("record_path", os.path.dirname(file))
        glob.Recorder.m_h.info("File saved. (%d Steps)" % len(glob.Recorder.recording.recordings))

    @pyqtSlot(str)
    def load_file(self, file: str):
        # restore the object
        with gzip.open(file, 'rb') as f:
            dump = pickle.load(f)
        glob.Recorder.set_recording(Recording.from_dump(dump))

        glob.Settings.setValue("record_path", os.path.dirname(file))
        glob.Recorder.m_h.info("File loaded. (%d Steps)" % len(glob.Recorder.recording.recordings))

    def on_new_recording(self):
        self.list_play.setModel(glob.Recorder.recording.play_items_model)
        self.record_name.setText(glob.Recorder.recording.name)

    @pyqtSlot(QCloseEvent)
    def closeEvent(self, *args, **kwargs):
        if hasattr(glob, "Settings") and glob.Settings is not None:
            logger.debug("Settings present: %s", type(glob.Settings))
        else:
            logger.warning("No Settings object in glob")
        glob.Settings.setValue("recorder_geometry", self.saveGeometry())
        glob.Recorder.m_h = glob.Recorder.m_h.original
        self.deleteLater()
        QMainWindow.closeEvent(self, *args, **kwargs)

    @pyqtSlot()
    def record_click(self):
        if glob.Recorder.is_recording:
            self.record.setIcon(qta.icon("fa6s.circle", color="red"))
            self.play.setEnabled(True)
            self.f_forward.setEnabled(True)
            self.step.setEnabled(True)
            glob.Recorder.stop_recording()
        else:
            self.record.setIcon(qta.icon("fa6s.stop"))
            self.play.setEnabled(False)
            self.f_forward.setEnabled(False)
            self.step.setEnabled(False)
            self.stop.setEnabled(False)
            self.list_play.setEnabled(True)
            glob.Recorder.start_recording()

    def step_click(self):
        self.stop.setEnabled(True)
        self.list_play.setEnabled(False)
        glob.Recorder.step_playback()

    def stop_click(self):
        glob.Recorder.stop_playback()

    @pyqtSlot()
    def finished(self):
        self.play.setIcon(qta.icon("fa6s.play", color="green"))
        self.play.setEnabled(True)
        self.f_forward.setEnabled(True)
        self.step.setEnabled(True)
        self.stop.setEnabled(False)
        self.list_play.setEnabled(True)
        self.record.setEnabled(True)

    def f_forward_click(self):
        self.play.setEnabled(False)
        self.f_forward.setEnabled(False)
        self.step.setEnabled(False)
        self.stop.setEnabled(False)
        self.list_play.setEnabled(True)
        glob.Recorder.fast_playback()

    def play_click(self):
        self.stop.setEnabled(True)
        self.list_play.setEnabled(False)
        if glob.Recorder.is_playing_back and not glob.Recorder.is_paused:
            self.play.setIcon(qta.icon("fa6s.play", color="green"))
            self.f_forward.setEnabled(True)
            self.step.setEnabled(True)
            glob.Recorder.pause_playback()
        else:
            self.play.setIcon(qta.icon("fa6s.pause", color="green"))
            self.f_forward.setEnabled(False)
            self.step.setEnabled(False)
            if glob.Recorder.is_paused:
                glob.Recorder.continue_playback()
            else:
                glob.Recorder.start_playback()


class PlayAction:
    def __init__(self, action: Union[str, dict, list], *args, copy_action=True, **kwargs):
        super().__init__(*args, **kwargs)
        if copy_action:
            action = copy.deepcopy(action)
        self.action = action


class Recordable:
    @staticmethod
    def record_method():
        def _wrapper(func):
            def _decorator(self: Recordable, *args, **kwargs):
                if kwargs.get("play_back", False):
                    return func(self, *args, **kwargs)
                kwargs["play_back"] = True
                action = PlayAction({
                    "method": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                })
                glob.Recorder.record(self.cls_name, self.instance_name, action)
                kwargs["play_back"] = False
                return func(self, *args, **kwargs)

            return _decorator

        return _wrapper

    @staticmethod
    def intercept_on_playback():
        def _wrapper(func):
            def _decorator(self: Recordable, *args, **kwargs):
                if self.playing_back and not kwargs.get("play_back", False):
                    return

                return func(self, *args, **kwargs)

            return _decorator

        return _wrapper

    def __init__(self, *args, instance_name=None, cls_name=None, singleton: Optional[bool] = None, register=True,
                 **kwargs):
        super().__init__(*args, **kwargs)
        if instance_name is None:
            instance_name = "STATIC"
        if cls_name is None:
            cls_name = self.__module__ + "." + self.__class__.__name__
        if singleton is None:
            singleton = cls_name == "STATIC"

        self.cls_name = cls_name
        self.instance_name = instance_name
        self.singleton = singleton
        if register:
            self.recorder_register()

    def recorder_register(self):
        glob.Recorder.register_instance(self.__class__, self.cls_name, self, self.instance_name, self.singleton)

    @property
    def playing_back(self) -> bool:
        return glob.Recorder.is_playing_back

    def play_back(self, action: PlayAction):
        if isinstance(action.action, dict):
            method = action.action.get("method", None)
            try:
                if method is not None:
                    method = self.__getattribute__(method)
            except AttributeError:
                method = None
            args = action.action.get("args", tuple())
            kwargs = action.action.get("kwargs", dict())
            if callable(method) and isinstance(args, tuple) and isinstance(kwargs, dict):
                if len(args) > 0:
                    if len(kwargs) > 0:
                        return method(*args, **kwargs)
                    return method(*args)
                if len(kwargs) > 0:
                    return method(**kwargs)
                return method()
        raise NotImplementedError()


class RecordAction:
    @staticmethod
    def delay_only(delay_s):
        return RecordAction("", "", None, delay_s)

    def __init__(self, classname: str, instancename: str, action: Optional[PlayAction], delay_s=-1.):
        self.classname = classname
        self.instancename = instancename
        self.action = action
        self.delay = delay_s

    def clone(self):
        return RecordAction(self.classname, self.instancename, self.action, self.delay)

    def __str__(self):
        return "A<%s,%s,%s>" % (self.classname, self.instancename, str(self.action.action))


class Recording:
    def __init__(self, *args, name=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Recording %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S") if name is None else name
        self.recordings: List[RecordAction] = []
        self.play_items_model: QStandardItemModel = QStandardItemModel()
        self.play_items_dict = dict()
        self.check_states_restore: List[bool] = []

    @property
    def check_states(self) -> List[bool]:
        states = []
        for i in range(self.play_items_model.rowCount()):
            states.append(self.play_items_model.item(i).checkState() == Qt.Checked)

        return states

    @property
    def recordings_cleaned(self) -> List[RecordAction]:
        recordings = []
        delay_add = 0
        for r in self.recordings:
            try:
                if self.play_items_dict[r.classname][r.instancename].checkState() == Qt.Checked:
                    if delay_add > 0:
                        r = r.clone()
                        if r.delay > 0:
                            r.delay += delay_add
                        else:
                            r.delay = delay_add
                        delay_add = 0
                    recordings.append(r)
                else:
                    raise KeyError()
            except (KeyError, AttributeError):
                if r.delay > 0:
                    delay_add += r.delay

        return recordings

    def update_model(self):
        self.play_items_model.clear()
        self.play_items_dict.clear()
        for r in self.recordings:
            checked = True
            if len(self.check_states_restore) > 0:
                checked = self.check_states_restore.pop(0)
            add_model_entry(self.play_items_model, self.play_items_dict, r.classname, r.instancename, checked)

    def to_dump(self):
        return [
            self.name,
            self.recordings,
            self.check_states
        ]

    @staticmethod
    def from_dump(d) -> "Recording":
        r = Recording(name=d[0])
        r.recordings = d[1]
        r.check_states_restore = d[2]
        r.update_model()

        return r


def make_item(cls, instance, dic, checked=True):
    cls_short = cls.split(".")[-1]
    if instance.upper() in ["", "_", "STATIC"]:
        item = QStandardItem(cls_short)
    else:
        item = QStandardItem("%s.%s" % (cls_short, instance))
    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
    item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
    if dic.get(cls, None) is None:
        dic[cls] = dict()
    dic[cls][instance] = item

    return item


def add_model_entry(model, dict_, cls, instance, checked=True):
    if dict_.get(cls, dict()).get(instance, None) is None:
        model.appendRow(make_item(cls, instance, dict_, checked))


class Recorder(QObject):
    def __init__(self, *args, message_handler=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.classes: Dict[str, type] = {}
        self.instances: Dict[str, Dict[str, List[Recordable]]] = {}
        self.recording = None
        self.set_recording(Recording())
        self.actions_playing: List[RecordAction] = []
        self.last_time: datetime = None
        self.is_recording: bool = False
        self.is_playing_back = False
        self.is_paused = False
        self.actions_count = -1
        self.m_h = WrappedMessageHandler(message_handler, "Recorder")

        self.record_items_model: QStandardItemModel = QStandardItemModel()
        self.record_items_dict = dict()

    finished = pyqtSignal()
    recording_changed = pyqtSignal()

    @property
    def progress(self) -> str:
        return "%d/%d" % (self.actions_count-len(self.actions_playing), self.actions_count)

    def set_recording(self, recording):
        self.recording = recording
        self.recording_changed.emit()

    def set_message_handler(self, message_handler):
        self.m_h = WrappedMessageHandler(message_handler, "Recorder")

    def register_instance(self, cls: type, cls_name: str, instance: Recordable, instance_name: str, singleton: bool):
        if self.classes.get(cls_name, None) is None:
            self.classes[cls_name] = cls

        if self.instances.get(cls_name, None) is None:
            self.instances[cls_name]: Dict[str, List[Recordable]] = dict()

        if self.instances[cls_name].get(instance_name) is None:
            self.instances[cls_name][instance_name]: List[Recordable] = list()
        elif singleton:
            raise ValueError("Instance %s <%s> already defined!" % (instance_name, cls_name))

        add_model_entry(self.record_items_model, self.record_items_dict, cls_name, instance_name)

        self.instances[cls_name][instance_name].append(instance)

    def record(self, classname, instancename, action):
        if not self.is_recording:
            return

        try:
            if self.record_items_dict[classname][instancename].checkState() != Qt.Checked:
                return
        except (AttributeError, KeyError):
            return

        now_time = datetime.now()
        self.recording.recordings.append(
            RecordAction(classname, instancename, action, (now_time - self.last_time).total_seconds()))
        self.last_time = now_time
        self.m_h.info("Recording... %d" % len(self.recording.recordings))

    @pyqtSlot()
    def stop_recording(self):
        from pympler import asizeof
        self.is_recording = False
        self.recording.update_model()
        self.m_h.info("%d Action%s recorded. (%s Bytes)" % (
            len(self.recording.recordings), "s" if len(self.recording.recordings) != 1 else "",
            asizeof.asizeof(self.recording.recordings)))

    @pyqtSlot()
    def start_recording(self):
        self.is_recording = True
        self.last_time = datetime.now()
        self.set_recording(Recording())
        self.m_h.info("Recording...")

    @pyqtSlot()
    def stop_playback(self, finished=False):  # TODO
        if finished:
            self.m_h.info("Playback finished. [%s]" % self.progress)
        else:
            self.m_h.info("Playback aborted.")
        self.is_paused = False
        self.is_playing_back = False
        self.finished.emit()

    @pyqtSlot()
    def pause_playback(self):  # TODO
        self.is_paused = True
        self.m_h.info("Paused. [%s]" % self.progress)

    @pyqtSlot()
    def continue_playback(self):
        self.is_paused = False
        self.queue_step()

    @pyqtSlot()
    def step_playback(self):
        if not self.is_playing_back:
            self.is_playing_back = True
            self.set_actions()
        self.is_paused = True
        self.make_step(True, False)

    @pyqtSlot()
    def fast_playback(self):
        self.is_playing_back = True
        self.is_paused = False
        self.set_actions()
        self.queue_step(instant=True)

    @pyqtSlot()
    def start_playback(self):
        self.is_playing_back = True
        self.is_paused = False
        self.set_actions()
        self.queue_step()
        self.m_h.info("Playing.. [%s]" % self.progress)

    def set_actions(self):
        self.actions_playing = self.recording.recordings_cleaned
        self.actions_count = len(self.actions_playing)

    def queue_step(self, instant=False):
        if len(self.actions_playing) == 0:
            self.stop_playback(finished=True)
            return
        call_async(self.make_step, (instant,))

    def make_step(self, instant=False, queue_next=True):
        start_time = datetime.now()
        step: RecordAction = self.actions_playing[0]
        while not instant and step.delay > (datetime.now() - start_time).total_seconds():
            time.sleep(.005)
            if not self.is_playing_back or self.is_paused:
                return

        self.actions_playing = self.actions_playing[1:]
        self.play_back(step)
        if len(self.actions_playing) == 0:
            return self.stop_playback(finished=True)
        if queue_next:
            self.queue_step(instant)
        if not instant or not queue_next:
            if queue_next:
                self.m_h.info("Playing.. [%s]" % self.progress)
            else:
                self.m_h.info("Paused. [%s]" % self.progress)

    @staticmethod
    def sync_play_back(instances: List[Recordable], instance: Recordable, action):
        try:
            instance.play_back(action)
        except (Exception,):
            instances.remove(instance)

    def play_back(self, recording: RecordAction):
        if recording.action is None:
            return
        instances = self.instances.get(recording.classname, dict()).get(recording.instancename, list())
        if len(instances) == 0:
            self.m_h.warning(
                "No instance of %s <%s> to play back action!" % (recording.instancename, recording.classname))
        for i in instances:
            from .widget import async_in_main_thread
            async_in_main_thread(Recorder.sync_play_back, (instances, i, recording.action))

glob.Recorder = Recorder()
