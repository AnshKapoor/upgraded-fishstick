from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any, List, Literal, Optional

import qtawesome as qta
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QWidget,
)


@dataclass
class ExternalEvent:
    """Represents an interaction with an external system."""
    ts: float
    direction: Literal["in", "out"]
    kind: str
    payload: Any


class ExternalRecorder:
    """Record and replay external system interactions.

    This implementation is intentionally lightweight and acts as an
    in-memory logger that can be flushed to/from a JSON lines file.
    It is designed to be a drop-in utility for hardware modules which
    simply call :func:`record` with a filled :class:`ExternalEvent`.
    """

    def __init__(self) -> None:
        self.events: List[ExternalEvent] = []
        self._recording = False
        self._replaying = False
        self._idx = 0

    # ------------------------------------------------------------------
    # Recording API
    # ------------------------------------------------------------------
    def start(self) -> None:
        """Begin a new recording session."""
        self.events.clear()
        self._idx = 0
        self._replaying = False
        self._recording = True

    def stop(self) -> None:
        """Stop recording further events."""
        self._recording = False

    def record(self, event: ExternalEvent) -> None:
        """Append an event if recording and not currently replaying."""
        if self._recording and not self._replaying:
            self.events.append(event)

    def save(self, path: str | Path) -> None:
        """Persist events as JSON lines."""
        p = Path(path)
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

    def start_replay(self) -> None:
        self._replaying = True
        self._recording = False
        self._idx = 0

    def stop_replay(self) -> None:
        self._replaying = False
        self._idx = 0

    def jump_to(self, ts: float) -> None:
        """Jump replay pointer to first event >= timestamp."""
        for i, ev in enumerate(self.events):
            if ev.ts >= ts:
                self._idx = i
                return
        self._idx = len(self.events)

    def step(self) -> Optional[ExternalEvent]:
        """Return next event during replay."""
        if self._idx >= len(self.events):
            return None
        ev = self.events[self._idx]
        self._idx += 1
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


# Global recorder instance used by hardware modules
external_recorder = ExternalRecorder()


class ExternalRecorderWindow(QMainWindow):
    """Simple window offering controls for the external recorder."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setWindowTitle("External Recorder")

        central = QWidget(self)
        layout = QHBoxLayout(central)
        self.record_btn = QPushButton()
        self.play_btn = QPushButton()
        self.step_btn = QPushButton()
        self.stop_btn = QPushButton()

        self.record_btn.setIcon(qta.icon("fa6s.circle", color="red"))
        self.play_btn.setIcon(qta.icon("fa6s.play", color="green"))
        self.step_btn.setIcon(qta.icon("fa6s.forward-step", color="orange"))
        self.stop_btn.setIcon(qta.icon("fa6s.stop"))

        self.play_btn.setEnabled(False)
        self.step_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        self.record_btn.clicked.connect(self.record_click)
        self.play_btn.clicked.connect(self.play_click)
        self.step_btn.clicked.connect(self.step_click)
        self.stop_btn.clicked.connect(self.stop_click)

        for btn in (self.record_btn, self.play_btn, self.step_btn, self.stop_btn):
            layout.addWidget(btn)

        self.setCentralWidget(central)
        self.show()

    @pyqtSlot()
    def record_click(self) -> None:
        if external_recorder.is_recording:
            external_recorder.stop()
            self.record_btn.setIcon(qta.icon("fa6s.circle", color="red"))
            self.play_btn.setEnabled(True)
            self.step_btn.setEnabled(True)
            external_recorder.save("external_recorder.gspy")
        else:
            external_recorder.start()
            self.record_btn.setIcon(qta.icon("fa6s.stop"))
            self.play_btn.setEnabled(False)
            self.step_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)

    @pyqtSlot()
    def play_click(self) -> None:
        external_recorder.start_replay()
        self.play_btn.setEnabled(False)
        self.step_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    @pyqtSlot()
    def step_click(self) -> None:
        if not external_recorder.is_replaying:
            external_recorder.start_replay()
        external_recorder.step()
        self.stop_btn.setEnabled(True)

    @pyqtSlot()
    def stop_click(self) -> None:
        external_recorder.stop_replay()
        self.play_btn.setEnabled(True)
        self.step_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.record_btn.setIcon(qta.icon("fa6s.circle", color="red"))
