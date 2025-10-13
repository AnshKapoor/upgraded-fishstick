from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional

import qtawesome as qta
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QStyle,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QSpinBox,
)

import gspy_egse.gui.globalvars as glob
from .widget import select_file

EXTERNAL_RECORDING_FILTER = "External Recording (*.gspy)"
DEFAULT_FILENAME_TEMPLATE = "external_%Y%m%d_%H%M%S.gspy"
logger = logging.getLogger(__name__)



@dataclass
class ExternalEvent:
    """Represents an interaction with an external system."""
    ts: float
    direction: Literal["in", "out"]
    kind: str
    payload: Any

Handler = Callable[[ExternalEvent], None]



class ExternalRecorder(QObject):
    """Record and replay external system interactions."""

    event_recorded = pyqtSignal(object)
    event_replayed = pyqtSignal(object)
    playback_started = pyqtSignal()
    playback_stopped = pyqtSignal()
    playback_finished = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.events: List[ExternalEvent] = []
        self._recording = False
        self._replaying = False
        self._idx = 0
        self._pending_delay: Optional[float] = None
        self._replay_limit_idx: Optional[int] = None
        self._handlers: Dict[str, List[Handler]] = {}


    def register_handler(self, kind: str, handler: Handler) -> None:
        """Register a callback invoked when an event of the given kind replays."""
        handlers = self._handlers.setdefault(kind, [])
        if handler not in handlers:
            handlers.append(handler)

    def unregister_handler(self, kind: str, handler: Handler) -> None:
        """Remove a previously registered handler."""
        handlers = self._handlers.get(kind)
        if not handlers:
            return
        try:
            handlers.remove(handler)
        except ValueError:
            return
        if not handlers:
            self._handlers.pop(kind, None)

    def _dispatch_event(self, event: ExternalEvent) -> None:
        handlers = list(self._handlers.get(event.kind, []))
        wildcard = self._handlers.get('*', [])
        if wildcard:
            handlers.extend(wildcard)
        for handler in handlers:
            try:
                handler(event)
            except Exception:
                logger.exception("External recorder handler failed for %s", event.kind)

    @staticmethod
    def _format_byte_sequence(data: List[int], max_items: int = 16) -> str:
        preview = ' '.join(f"{value:02X}" for value in data[:max_items])
        if len(data) > max_items:
            preview += ' ...'
        return preview or '<empty>'

    def _summarize_payload(self, payload: Any, max_items: int = 16, max_chars: int = 120) -> str:
        if isinstance(payload, str):
            text = payload.strip()
        elif isinstance(payload, (bytes, bytearray)):
            text = self._format_byte_sequence(list(payload), max_items)
        elif isinstance(payload, list) and all(isinstance(item, int) for item in payload):
            text = self._format_byte_sequence(payload, max_items)
        else:
            text = repr(payload)
        text = ' '.join(text.split())
        if len(text) > max_chars:
            text = text[: max_chars - 3] + '...'
        return text or '<empty>'

    def _describe_event(self, event: ExternalEvent) -> str:
        return f"{event.direction.upper()} {event.kind}: {self._summarize_payload(event.payload)}"

    def _log_event(self, action: str, event: ExternalEvent) -> None:
        logger.info("[External %s] %s", action, self._describe_event(event))
    # ------------------------------------------------------------------
    # Recording API
    # ------------------------------------------------------------------
    def start(self) -> None:
        """Begin a new recording session."""
        self.events.clear()
        self._idx = 0
        self._pending_delay = 0.0
        self._replaying = False
        self._recording = True
        logger.info("External recorder started a new session.")

    def stop(self) -> None:
        """Stop recording further events."""
        self._recording = False
        logger.info("External recorder stopped recording (%d events).", len(self.events))
    def record(self, event: ExternalEvent) -> None:
        """Append an event if recording and not currently replaying."""
        if self._recording and not self._replaying:
            self.events.append(event)
            self._log_event("recorded", event)
            self.event_recorded.emit(event)

    def save(self, path: str | Path) -> None:
        """Persist events as JSON lines."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as fh:
            for ev in self.events:
                fh.write(
                    json.dumps(
                        {
                            "ts": ev.ts,
                            "direction": ev.direction,
                            "kind": ev.kind,
                            "payload": ev.payload,
                        }
                    )
                    + "\n"
                )
        logger.info("Saved %d external events to %s", len(self.events), p)


    # ------------------------------------------------------------------
    # Replay API
    # ------------------------------------------------------------------
    def load(self, path: str | Path) -> None:
        """Load events from a JSON lines file."""
        p = Path(path)
        self.events.clear()
        self._idx = 0
        self._replaying = False
        self._recording = False
        with p.open("r", encoding="utf-8") as fh:
            for line in fh:
                data = json.loads(line)
                self.events.append(ExternalEvent(**data))
        logger.info("Loaded %d external events from %s", len(self.events), p)
        self._pending_delay = 0.0 if self.events else None


    def start_replay(self, start_index: int = 0, *, single_event: bool = False) -> None:
        if not self.events:
            self._replaying = False
            self._pending_delay = None
            logger.warning("External recorder replay requested with no events.")
            return
        count = len(self.events)
        start_index = max(0, min(start_index, count))
        if start_index >= count:
            logger.warning("External recorder start index %d out of range.", start_index)
            self._replaying = False
            self._pending_delay = None
            return
        if not self._replaying:
            self.playback_started.emit()
        self._replaying = True
        self._recording = False
        self._idx = start_index
        self._replay_limit_idx = start_index + 1 if single_event else None
        self._pending_delay = 0.0 if self._idx < count else None
        logger.info("External recorder starting playback of %d events from index %d.", count, self._idx)

    def stop_replay(self, finished: bool = False) -> None:
        was_replaying = self._replaying
        self._replaying = False
        self._replay_limit_idx = None
        self._idx = 0
        self._pending_delay = None
        if finished:
            logger.info("External recorder playback finished.")
            self.playback_finished.emit()
        else:
            if was_replaying:
                logger.info("External recorder playback stopped before completion.")
            else:
                logger.info("External recorder playback cancelled.")
        if was_replaying or finished:
            self.playback_stopped.emit()


    def jump_to(self, ts: float) -> None:
        """Jump replay pointer to first event >= timestamp."""
        self._replay_limit_idx = None
        for i, ev in enumerate(self.events):
            if ev.ts >= ts:
                self._idx = i
                self._pending_delay = 0.0
                return
        self._idx = len(self.events)
        self._pending_delay = None

    def jump_to_index(self, index: int) -> None:
        """Jump replay pointer to the given event index."""
        count = len(self.events)
        if count == 0:
            self._idx = 0
            self._pending_delay = None
            return
        if index < 0:
            index = 0
        if index >= count:
            self._idx = count
            self._pending_delay = None
            return
        self._idx = index
        self._pending_delay = 0.0
        self._replay_limit_idx = None

    def step(self) -> Optional[ExternalEvent]:
        """Return next event during replay and emit playback signal."""
        if not self.events:
            return None
        if not self._replaying:
            self.start_replay()
            if not self._replaying:
                return None
        if self._idx >= len(self.events):
            self.stop_replay(finished=True)
            return None
        ev = self.events[self._idx]
        self._idx += 1
        if self._idx < len(self.events) and (self._replay_limit_idx is None or self._idx < self._replay_limit_idx):
            next_ev = self.events[self._idx]
            self._pending_delay = max(0.0, next_ev.ts - ev.ts)
        else:
            self._pending_delay = None
        self._dispatch_event(ev)
        self._log_event("replayed", ev)
        self.event_replayed.emit(ev)
        reached_end = self._idx >= len(self.events)
        reached_limit = self._replay_limit_idx is not None and self._idx >= self._replay_limit_idx
        if reached_end or reached_limit:
            self.stop_replay(finished=True)
        return ev


    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def is_recording(self) -> bool:
        return self._recording

    @property
    def is_replaying(self) -> bool:
        return self._replaying

    @property
    def next_delay(self) -> Optional[float]:
        return self._pending_delay


# Global recorder instance used by hardware modules
external_recorder = ExternalRecorder()


class ExternalRecorderWindow(QMainWindow):
    """Window offering controls for the external recorder."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setWindowTitle("External Recorder")

        self._play_timer: Optional[QTimer] = None
        self._auto_play = False
        self._playback_finished_recently = False
        self._played_events = 0
        self._pending_single_play_index: Optional[int] = None
        self._selected_step_index: Optional[int] = None

        central = QWidget(self)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        file_row = QHBoxLayout()
        file_row.setSpacing(8)
        self.file_label = QLabel("Save As:", self)
        file_row.addWidget(self.file_label)
        self.file_edit = QLineEdit(self)
        self.file_edit.setPlaceholderText("Choose where to store the external recording...")
        self.file_edit.setClearButtonEnabled(True)
        file_row.addWidget(self.file_edit, 1)
        self.browse_btn = QToolButton(self)
        self.browse_btn.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
        self.browse_btn.setToolTip("Select output file")
        self.browse_btn.clicked.connect(self.select_save_path)
        file_row.addWidget(self.browse_btn)
        root_layout.addLayout(file_row)

        button_row = QHBoxLayout()
        button_row.setSpacing(12)

        self.load_btn = QPushButton()
        self.load_btn.setIcon(qta.icon("fa6s.folder-open"))
        self.load_btn.setToolTip("Load an external recording")
        self.load_btn.clicked.connect(self.load_click)

        self.record_btn = QPushButton()
        self.record_btn.setIcon(qta.icon("fa6s.circle", color="red"))
        self.record_btn.setToolTip("Start recording external events")
        self.record_btn.clicked.connect(self.record_click)

        self.play_btn = QPushButton()
        self.play_btn.setIcon(qta.icon("fa6s.play", color="green"))
        self.play_btn.setToolTip("Play the recorded events")
        self.play_btn.clicked.connect(self.play_click)

        self.step_btn = QPushButton()
        self.step_btn.setIcon(qta.icon("fa6s.forward-step", color="orange"))
        self.step_btn.setToolTip("Replay the next recorded event")
        self.step_btn.clicked.connect(self.step_click)

        self.stop_btn = QPushButton()
        self.stop_btn.setIcon(qta.icon("fa6s.stop"))
        self.stop_btn.setToolTip("Stop playback")
        self.stop_btn.clicked.connect(self.stop_click)

        button_row.addStretch(1)
        button_row.addWidget(self.load_btn)
        for btn in (self.record_btn, self.play_btn, self.step_btn, self.stop_btn):
            button_row.addWidget(btn)
        button_row.addStretch(1)

        root_layout.addLayout(button_row)

        jump_row = QHBoxLayout()
        jump_row.setSpacing(8)
        self.step_selector_label = QLabel("Step:", self)
        jump_row.addWidget(self.step_selector_label)
        self.step_selector = QSpinBox(self)
        self.step_selector.setRange(1, 1)
        self.step_selector.setEnabled(False)
        jump_row.addWidget(self.step_selector)
        self.goto_btn = QPushButton()
        self.goto_btn.setIcon(qta.icon("fa6s.bullseye", color="orange"))
        self.goto_btn.setToolTip("Select a step for single playback")
        self.goto_btn.setEnabled(False)
        self.goto_btn.clicked.connect(self.jump_to_step)
        jump_row.addWidget(self.goto_btn)
        jump_row.addStretch(1)
        root_layout.addLayout(jump_row)

        self.status_label = QLabel("Ready.", self)
        self.status_label.setWordWrap(True)
        root_layout.addWidget(self.status_label)

        self.log_view = QPlainTextEdit(self)
        self.log_view.setReadOnly(True)
        self.log_view.setObjectName("externalRecorderLogView")
        self.log_view.setPlaceholderText("Playback log will appear here.")
        self.log_view.document().setMaximumBlockCount(2000)
        root_layout.addWidget(self.log_view, 1)

        self.setCentralWidget(central)
        self.resize(720, 420)
        self.setMinimumWidth(600)

        self.file_edit.setText(self._default_filename())

        external_recorder.event_recorded.connect(self._on_event_recorded)
        external_recorder.event_replayed.connect(self._on_event_replayed)
        external_recorder.playback_started.connect(self._on_playback_started)
        external_recorder.playback_finished.connect(self._on_playback_finished)
        external_recorder.playback_stopped.connect(self._on_playback_stopped)

        self._clear_logs()
        self._append_log("Ready to record external interactions.")
        self._refresh_playback_controls()
        self.show()

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------
    def _set_status(self, text: str) -> None:
        self.status_label.setText(text)

    def _update_step_selector(self) -> None:
        count = len(external_recorder.events)
        max_value = max(1, count)
        self.step_selector.setMaximum(max_value)
        if count == 0:
            self.step_selector.setValue(1)
            self._selected_step_index = None
            self._pending_single_play_index = None
        else:
            if self._selected_step_index is not None:
                if self._selected_step_index >= count:
                    self._selected_step_index = count - 1
                target_value = self._selected_step_index + 1
                if target_value != self.step_selector.value():
                    self.step_selector.setValue(target_value)
            elif self.step_selector.value() > count:
                self.step_selector.setValue(count)
        enabled = count > 0 and not external_recorder.is_recording and not external_recorder.is_replaying
        self.step_selector.setEnabled(enabled)
        self.goto_btn.setEnabled(enabled)

    def _refresh_playback_controls(self) -> None:
        has_events = bool(external_recorder.events)
        self.play_btn.setEnabled(has_events)
        self.step_btn.setEnabled(has_events)
        self.stop_btn.setEnabled(False)
        self._update_step_selector()

    def _clear_logs(self) -> None:
        self.log_view.clear()

    def _append_log(self, message: str) -> None:
        if not message:
            return
        self.log_view.appendPlainText(message)
        self.log_view.ensureCursorVisible()

    def _format_byte_sequence(self, data: List[int], max_items: int) -> str:
        preview = ' '.join(f'{value:02X}' for value in data[:max_items])
        if len(data) > max_items:
            preview += ' ...'
        return preview or '<empty>'

    def _summarize_payload(self, payload: Any, max_items: int = 16, max_chars: int = 120) -> str:
        if isinstance(payload, str):
            text = payload.strip()
        elif isinstance(payload, (bytes, bytearray)):
            text = self._format_byte_sequence(list(payload), max_items)
        elif isinstance(payload, list) and all(isinstance(item, int) for item in payload):
            text = self._format_byte_sequence(payload, max_items)
        else:
            text = repr(payload)
        text = ' '.join(text.split())
        if len(text) > max_chars:
            text = text[: max_chars - 3] + '...'
        return text or '<empty>'

    def _describe_event(self, event: ExternalEvent) -> str:
        direction = 'SEND' if event.direction == 'out' else 'RECV'
        detail = self._summarize_payload(event.payload)
        return f"{direction} {event.kind}: {detail}"

    def _settings_value(self, key: str, default: str) -> str:
        try:
            settings = getattr(glob, "Settings")
        except AttributeError:
            return default
        if settings is None:
            return default
        value = settings.value(key, default)
        return str(value) if value is not None else default

    def _store_record_path(self, path: Path) -> None:
        try:
            settings = getattr(glob, "Settings")
        except AttributeError:
            return
        if settings is None:
            return
        settings.setValue("external_record_path", str(path.parent))

    def _current_record_directory(self) -> str:
        text = self.file_edit.text().strip()
        if text:
            p = Path(text)
            if p.is_dir():
                return str(p)
            if p.parent.exists():
                return str(p.parent)
        fallback = self._settings_value("external_record_path", str(Path.cwd()))
        return fallback

    def _default_filename(self) -> str:
        base = Path(self._settings_value("external_record_path", str(Path.cwd())))
        if not base.exists():
            base = Path.cwd()
        timestamp = datetime.now().strftime(DEFAULT_FILENAME_TEMPLATE)
        return str((base if base.is_dir() else base.parent) / timestamp)

    def _resolve_save_path(self) -> Path:
        text = self.file_edit.text().strip()
        if not text:
            text = self._default_filename()
        path = Path(text)
        if path.suffix.lower() != ".gspy":
            path = path.with_suffix(".gspy")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.file_edit.setText(str(path))
        return path

    def _ensure_timer(self) -> None:
        if self._play_timer is None:
            self._play_timer = QTimer(self)
            self._play_timer.setSingleShot(True)
            self._play_timer.timeout.connect(self._advance_playback)

    def _stop_timer(self) -> None:
        if self._play_timer is not None:
            self._play_timer.stop()
            self._play_timer.deleteLater()
            self._play_timer = None

    def _advance_playback(self) -> None:
        event = external_recorder.step()
        if event is None:
            return
        delay = external_recorder.next_delay
        if delay is None or not external_recorder.is_replaying:
            return
        self._ensure_timer()
        self._play_timer.start(max(1, int(delay * 1000)))

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    @pyqtSlot()
    def select_save_path(self) -> None:
        select_file(
            self._on_save_path_selected,
            path=self._current_record_directory(),
            type_filter=EXTERNAL_RECORDING_FILTER,
            create_new=True,
        )

    def _on_save_path_selected(self, file_path: str) -> None:
        path = Path(file_path)
        if path.suffix.lower() != ".gspy":
            path = path.with_suffix(".gspy")
        self.file_edit.setText(str(path))
        self._store_record_path(path)

    @pyqtSlot()
    def jump_to_step(self) -> None:
        if not external_recorder.events:
            self._set_status("No recorded events to select.")
            self._append_log("No recorded events to select.")
            return
        total = len(external_recorder.events)
        index = max(0, min(self.step_selector.value() - 1, total - 1))
        self._selected_step_index = index
        self._pending_single_play_index = index
        self._auto_play = False
        if external_recorder.is_replaying:
            external_recorder.stop_replay()
        self._stop_timer()
        external_recorder.jump_to_index(index)
        event = external_recorder.events[index]
        detail = self._describe_event(event)
        self._set_status(f"Prepared step {index + 1}/{total} for single playback.")
        self._append_log(f"STEP {index + 1}: {detail}")
        self._update_step_selector()

    @pyqtSlot()
    def load_click(self) -> None:
        if external_recorder.is_recording:
            return
        select_file(
            self._on_load_path_selected,
            path=self._current_record_directory(),
            type_filter=EXTERNAL_RECORDING_FILTER,
            create_new=False,
        )

    def _on_load_path_selected(self, file_path: str) -> None:
        if not file_path:
            return
        path = Path(file_path)
        if path.suffix.lower() != ".gspy":
            path = path.with_suffix(".gspy")
        self._load_recording(path)

    def _load_recording(self, path: Path) -> None:
        if external_recorder.is_replaying:
            external_recorder.stop_replay()
        self._stop_timer()
        try:
            external_recorder.load(path)
        except Exception as exc:
            self._set_status(f"Failed to load {path.name}: {exc}")
            self._append_log(f"LOAD ERROR {path}: {exc}")
            return
        self.file_edit.setText(str(path))
        self._store_record_path(path)
        count = len(external_recorder.events)
        suffix = "" if count == 1 else "s"
        self._played_events = 0
        self._auto_play = False
        self._playback_finished_recently = False
        self._refresh_playback_controls()
        self.record_btn.setEnabled(True)
        self.load_btn.setEnabled(True)
        if count:
            self._set_status(f"Loaded {count} event{suffix} from {path.name}.")
        else:
            self._set_status(f"No events found in {path.name}.")
        self._clear_logs()
        self._append_log(f"Loaded {count} event{suffix} from {path.name}")
        self._update_step_selector()
    @pyqtSlot()
    def record_click(self) -> None:
        if external_recorder.is_recording:
            external_recorder.stop()
            self.record_btn.setIcon(qta.icon("fa6s.circle", color="red"))
            self.record_btn.setToolTip("Start recording external events")
            self.file_edit.setEnabled(True)
            self.browse_btn.setEnabled(True)
            self.load_btn.setEnabled(True)
            count = len(external_recorder.events)
            if count:
                path = self._resolve_save_path()
                external_recorder.save(path)
                self._store_record_path(path)
                message = f"Saved {count} event{'s' if count != 1 else ''} to {path.name}."
                self._set_status(message)
                self._append_log(message)
            else:
                self._set_status("Recording stopped. No events captured.")
                self._append_log("Recording stopped. No events captured.")
            self._refresh_playback_controls()
        else:
            if not self.file_edit.text().strip():
                self.file_edit.setText(self._default_filename())
            if external_recorder.is_replaying:
                external_recorder.stop_replay()
            self._stop_timer()
            self._auto_play = False
            self._played_events = 0
            self._clear_logs()
            self._append_log("Recording started.")
            external_recorder.start()
            self._selected_step_index = None
            self._pending_single_play_index = None
            self._update_step_selector()
            self.record_btn.setIcon(qta.icon("fa6s.stop"))
            self.record_btn.setToolTip("Stop recording")
            self.file_edit.setEnabled(False)
            self.browse_btn.setEnabled(False)
            self.load_btn.setEnabled(False)
            self.play_btn.setEnabled(False)
            self.step_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            self._set_status("Recording...")


    @pyqtSlot()
    def play_click(self) -> None:
        if not external_recorder.events:
            self._set_status("No recorded events to play.")
            self._append_log("No recorded events to play.")
            return
        if self._pending_single_play_index is not None:
            total = len(external_recorder.events)
            index = max(0, min(self._pending_single_play_index, total - 1))
            self._pending_single_play_index = None
            if total == 0:
                self._set_status("No recorded events to play.")
                self._append_log("No recorded events to play.")
                return
            self._auto_play = False
            self._stop_timer()
            if external_recorder.is_replaying:
                external_recorder.stop_replay()
            external_recorder.start_replay(start_index=index, single_event=True)
            event = external_recorder.step()
            if event is None:
                self._set_status(f"No event at step {index + 1}.")
                self._append_log(f"Step {index + 1} not available for playback.")
            return
        self._auto_play = True
        if not external_recorder.is_replaying:
            external_recorder.start_replay()
        self._ensure_timer()
        self._advance_playback()

    @pyqtSlot()
    def step_click(self) -> None:
        if not external_recorder.events:
            self._set_status("No recorded events to replay.")
            self._append_log("No recorded events to replay.")
            return
        self._auto_play = False
        self._stop_timer()
        if not external_recorder.is_replaying:
            external_recorder.start_replay()
        external_recorder.step()

    @pyqtSlot()
    def stop_click(self) -> None:
        if external_recorder.is_replaying:
            self._auto_play = False
            external_recorder.stop_replay()

    # ------------------------------------------------------------------
    # Recorder callbacks
    # ------------------------------------------------------------------
    def _on_event_recorded(self, event: object) -> None:
        if external_recorder.is_recording:
            count = len(external_recorder.events)
            self._set_status(
                f"Recording... {count} event{'s' if count != 1 else ''} captured."
            )
            if isinstance(event, ExternalEvent):
                detail = self._describe_event(event)
            else:
                detail = 'Event recorded'
            self._append_log(f"REC {count}: {detail}")
        self._update_step_selector()

    def _on_event_replayed(self, event: object) -> None:
        self._played_events += 1
        total = len(external_recorder.events)
        if isinstance(event, ExternalEvent):
            detail = self._describe_event(event)
        else:
            detail = 'Event'
        self._set_status(
            f"Replayed {self._played_events}/{total}: {detail}"
        )
        self._append_log(
            f"[{self._played_events}/{total}] {detail}"
        )
        if not self._auto_play:
            has_more = self._played_events < total
            self.play_btn.setEnabled(True)
            self.step_btn.setEnabled(has_more)
            self.stop_btn.setEnabled(True)

    def _on_playback_started(self) -> None:
        self._played_events = 0
        self._playback_finished_recently = False
        total = len(external_recorder.events)
        self._clear_logs()
        self._append_log(f"Playback started ({total} event{'s' if total != 1 else ''}).")
        self.record_btn.setEnabled(False)
        self.play_btn.setEnabled(False)
        self.step_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.load_btn.setEnabled(False)
        self._set_status("Playing back recorded events...")
        self._update_step_selector()

    def _on_playback_finished(self) -> None:
        self._playback_finished_recently = True
        self._set_status("Playback finished.")
        self._append_log("Playback finished.")
        self._stop_timer()
        self._update_step_selector()

    def _on_playback_stopped(self) -> None:
        self._stop_timer()
        self.record_btn.setEnabled(True)
        self.load_btn.setEnabled(True)
        self._refresh_playback_controls()
        self._auto_play = False
        if self._playback_finished_recently:
            self._playback_finished_recently = False
        else:
            self._set_status("Playback stopped.")
            self._append_log("Playback stopped by user.")



