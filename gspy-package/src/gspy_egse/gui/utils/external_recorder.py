from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Any, List, Literal, Optional


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

    def record(self, event: ExternalEvent) -> None:
        """Append an event if not currently replaying."""
        if not self._replaying:
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
        self.start()
        with p.open("r", encoding="utf-8") as fh:
            for line in fh:
                data = json.loads(line)
                self.events.append(ExternalEvent(**data))

    def start_replay(self) -> None:
        self._replaying = True
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


# Global recorder instance used by hardware modules
external_recorder = ExternalRecorder()
