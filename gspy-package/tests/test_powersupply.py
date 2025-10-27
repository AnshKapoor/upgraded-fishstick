"""Unit tests for the PowerSupply hardware module."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the package under test is importable without installation.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


import types
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Sequence, Tuple

# Provide lightweight stand-ins for optional GUI dependencies used by the module under test.
sys.modules.setdefault("pyqtgraph", types.SimpleNamespace())
sys.modules.setdefault("qtawesome", types.SimpleNamespace())


@dataclass
class ExternalEvent:
    """Representation of a recorded event used by the stub module."""

    ts: float
    direction: str
    kind: str
    payload: Any


class RecorderProxy:
    """Minimal stub mirroring the recorder API required by the PowerSupply module."""

    def __init__(self) -> None:
        """Initialise the stub with bookkeeping containers."""

        self.is_replaying: bool = False
        self.recorded_events: List[Any] = []
        self.handlers: List[Tuple[str, Callable[[Any], None]]] = []

    def register_handler(self, kind: str, handler: Callable[[Any], None]) -> None:
        """Track handler registrations for later assertions when necessary."""

        self.handlers.append((kind, handler))

    def unregister_handler(self, kind: str, handler: Callable[[Any], None]) -> None:
        """Unregister a previously stored handler."""

        self.handlers = [entry for entry in self.handlers if entry != (kind, handler)]

    def record(self, event: Any) -> None:
        """Collect events forwarded through the recorder API."""

        self.recorded_events.append(event)


# Stub out the heavy external recorder module so the hardware driver can import without Qt.
_external_recorder_module = types.ModuleType("gspy_egse.gui.utils.externalRecorder")
_external_recorder_module.ExternalEvent = ExternalEvent
_external_recorder_module.external_recorder = RecorderProxy()
sys.modules.setdefault("gspy_egse.gui.utils.externalRecorder", _external_recorder_module)

import pytest
import serial

from gspy_egse.gui.hardware_modules import powersupply


class DummyMessageHandler:
    """Collects GUI messages so the tests can assert on them."""

    def __init__(self) -> None:
        self.messages: List[Tuple[str, str]] = []

    def success(self, message: str) -> None:
        """Record a success level message."""

        self.messages.append(("success", message))

    def error(self, message: str) -> None:
        """Record an error level message."""

        self.messages.append(("error", message))

    def warning(self, message: str) -> None:
        """Record a warning level message."""

        self.messages.append(("warning", message))

    def info(self, message: str) -> None:
        """Record an info level message."""

        self.messages.append(("info", message))


class DummyRecorder:
    """Minimal substitute for the global external_recorder dependency."""

    def __init__(self) -> None:
        self.is_replaying: bool = False
        self.recorded_events: List[Any] = []
        self.handlers: List[Tuple[str, Callable[[Any], None]]] = []

    def register_handler(self, kind: str, handler: Callable[[Any], None]) -> None:
        """Store handler registrations for later assertions if required."""

        self.handlers.append((kind, handler))

    def unregister_handler(self, kind: str, handler: Callable[[Any], None]) -> None:
        """Remove a registered handler when asked by the PowerSupply."""

        self.handlers = [entry for entry in self.handlers if entry != (kind, handler)]

    def record(self, event: Any) -> None:
        """Capture recorded events so the tests can assert on them."""

        self.recorded_events.append(event)


class DummyThread:
    """Simple thread stub that does not spawn real worker threads."""

    def __init__(self, target: Optional[Callable[..., None]] = None, *, daemon: bool = False) -> None:
        self.target = target
        self.daemon = daemon
        self.started: bool = False

    def start(self) -> None:
        """Mark the thread as started without executing the target."""

        self.started = True


class DummySerial:
    """In-memory serial port stub used for successful connection tests."""

    def __init__(self, *args: Sequence[Any], **kwargs: Any) -> None:
        self.port = kwargs.get("port")
        self.baudrate = kwargs.get("baudrate")
        self.is_open: bool = False
        self._buffer: bytearray = bytearray()

    def close(self) -> None:
        """Simulate closing the serial port."""

        self.is_open = False

    def open(self) -> None:
        """Simulate opening the serial port and clear the buffer."""

        self.is_open = True
        self._buffer.clear()

    def isOpen(self) -> bool:
        """Return the legacy PySerial truthy state flag."""

        return self.is_open

    def inWaiting(self) -> int:
        """Return the number of bytes waiting to be read from the buffer."""

        return len(self._buffer)

    def read(self, size: int = 1) -> bytes:
        """Pop bytes from the buffer to simulate a blocking serial read."""

        if size <= 0:
            size = 1
        data = bytes(self._buffer[:size])
        del self._buffer[:size]
        return data

    def write(self, payload: bytes) -> int:
        """Echo a dummy response back into the buffer and report bytes written."""

        # Append a newline-terminated token so send_command() can consume it.
        self._buffer.extend(b"0.0\n")
        return len(payload)


@pytest.fixture(autouse=True)
def _patch_external_recorder(monkeypatch: pytest.MonkeyPatch) -> DummyRecorder:
    """Replace the module-level external recorder with a controllable stub."""

    recorder = DummyRecorder()
    monkeypatch.setattr(powersupply, "external_recorder", recorder)
    return recorder


@pytest.fixture(autouse=True)
def _patch_threading(monkeypatch: pytest.MonkeyPatch) -> List[DummyThread]:
    """Ensure new threads created by PowerSupply are deterministic in tests."""

    created_threads: List[DummyThread] = []

    def _factory(*args: Any, **kwargs: Any) -> DummyThread:
        thread = DummyThread(*args, **kwargs)
        created_threads.append(thread)
        return thread

    monkeypatch.setattr(powersupply.threading, "Thread", _factory)
    return created_threads


def test_connect_failure_leaves_serial_disconnected(monkeypatch: pytest.MonkeyPatch) -> None:
    """A SerialException should leave the PowerSupply disconnected and warn the user."""

    def _raise_serial(*_args: Any, **_kwargs: Any) -> None:
        raise serial.serialutil.SerialException("port missing")

    monkeypatch.setattr(powersupply.serial, "Serial", _raise_serial)

    handler = DummyMessageHandler()
    supply = powersupply.PowerSupply(port="FAKE", polling=False, message_handler=handler)

    assert supply.ser is None, "Serial handle must stay None on connection failure."
    assert not supply.is_connected(), "is_connected() should reflect the failed connection state."
    assert any(level == "error" and "Serial Connection failed." in message for level, message in handler.messages), "User should be notified about the failure."

    supply.flush_inbuffer()  # Should be a no-op without raising.


def test_successful_connect_sets_up_serial(monkeypatch: pytest.MonkeyPatch) -> None:
    """A successful connect() call should store the serial object and allow buffer flushing."""

    monkeypatch.setattr(powersupply.serial, "Serial", DummySerial)

    handler = DummyMessageHandler()
    supply = powersupply.PowerSupply(port="COM1", polling=False, message_handler=handler)

    assert supply.is_connected(), "Connection should be reported as established."
    assert supply.ser is not None, "Serial handle must be stored after a successful connection."

    assert handler.messages[0][0] == "success", "Successful connections should emit a success message."

    # Prime the fake buffer and verify that flush_inbuffer empties it safely.
    supply.ser._buffer.extend(b"123")  # type: ignore[attr-defined]
    supply.flush_inbuffer()
    assert supply.ser.inWaiting() == 0, "flush_inbuffer() should clear any pending bytes."


def test_start_polling_without_connection_is_guarded(monkeypatch: pytest.MonkeyPatch) -> None:
    """start_polling() must refuse to create polling threads when disconnected."""

    def _raise_serial(*_args: Any, **_kwargs: Any) -> None:
        raise serial.serialutil.SerialException("port missing")

    monkeypatch.setattr(powersupply.serial, "Serial", _raise_serial)

    handler = DummyMessageHandler()
    supply = powersupply.PowerSupply(port="FAKE", polling=False, message_handler=handler)

    supply.start_polling()

    assert not supply.polling, "Polling flag should remain false when no connection is available."
    assert any(level == "warning" and "Cannot start polling" in message for level, message in handler.messages)

