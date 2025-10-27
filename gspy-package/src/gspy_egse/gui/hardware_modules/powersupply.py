import time
import serial
import logging
from collections import deque
from contextlib import suppress
import threading
from typing import Optional

try:
    from ..utils.misc import WrappedMessageHandler
except (ValueError, ImportError):
    from ..utils.misc import WrappedMessageHandler

from ..utils.externalRecorder import external_recorder, ExternalEvent

logger = logging.getLogger(__name__)

def is_float_try(s_str):
    try:
        float(s_str)
        return True
    except ValueError:
        return False


class PowerSupply:
    """Call close() when you're done. Threads need to be killed!"""

    def __init__(self, channels: int = 1, polling: bool = False, polling_interval: int = 500,
                 port: str = 'COM4', baudrate: int = 19200, message_handler=None) -> None:
        """Initialize a power supply connection and optional polling behaviour."""

        message_handler = WrappedMessageHandler(message_handler, "PowerSupply")
        self.message_handler = message_handler
        self.channels = channels
        self.polling = polling
        self.polling_interval = polling_interval
        self.state = [-1] * channels
        self.voltage = [-1] * channels
        self.intensity = [-1] * channels
        self.voltage_out = [-1] * channels
        self.intensity_out = [-1] * channels

        self.send_lock = threading.Lock()
        self.poll_lock = threading.Lock()

        self.state_listeners = [[] for _ in range(channels)]
        self.voltage_listeners = [[] for _ in range(channels)]
        self.intensity_listeners = [[] for _ in range(channels)]
        self.voltage_out_listeners = [[] for _ in range(channels)]
        self.intensity_out_listeners = [[] for _ in range(channels)]

        self._external_handler_registered = False
        self._replay_expected_replies = deque()
        self._replay_queue_lock = threading.Lock()
        external_recorder.register_handler("power", self._handle_external_event)
        self._external_handler_registered = True

        self.ser: Optional[serial.Serial] = None

        connected = self.connect(port=port, baudrate=baudrate)

        if connected:
            self.flush_inbuffer()
            threading.Thread(target=self.get_all_values_from_device, daemon=True).start()
            if polling:
                self.start_polling()
        else:
            self.polling = False

    def connect(self, port: str, baudrate: int) -> bool:
        """Attempt to connect to the serial power supply.

        Args:
            port: Serial device path or port name.
            baudrate: Communication baud rate to be used.

        Returns:
            True when the serial connection has been established successfully, otherwise False.
        """

        if self.ser is not None:
            with suppress(Exception):
                if self.ser.is_open:
                    self.ser.close()
            self.ser = None

        try:
            serial_device = serial.Serial(
                port=port,
                baudrate=baudrate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                xonxoff=True,
                dsrdtr=False,
                rtscts=False,
                timeout=5
            )
            if serial_device.is_open:
                serial_device.close()
            serial_device.open()
            if not serial_device.isOpen():
                raise serial.serialutil.SerialException("Serial port failed to open.")
        except serial.serialutil.SerialException as exc:
            self.message_handler.error("Serial Connection failed.")
            logger.exception("Failed to establish serial connection to power supply: %s", exc)
            self.ser = None
            return False

        self.ser = serial_device
        self.message_handler.success("Serial Connection established.")
        return True

    def is_connected(self) -> bool:
        """Return True when the underlying serial device is ready for communication."""

        if self.ser is None:
            return False
        is_open_attr = getattr(self.ser, "is_open", None)
        if isinstance(is_open_attr, bool):
            return is_open_attr
        is_open_callable = getattr(self.ser, "isOpen", None)
        if callable(is_open_callable):
            return bool(is_open_callable())
        return False

    def close(self):
        self.polling = False
        self.polling_interval = 1
        if getattr(self, "_external_handler_registered", False):
            external_recorder.unregister_handler("power", self._handle_external_event)
            self._external_handler_registered = False
        threading.Thread(target=self.free_and_close, daemon=True).start()
        self.message_handler.info("Closing connection.")

    def free_and_close(self):
        with self.poll_lock:
            try:
                self.send_command("local", expected_lines=0)
                time.sleep(.050)
            except Exception:
                logger.exception("Failed to return power supply to local mode during shutdown.")
        try:
            self.ser.close()
        except Exception:
            logger.exception("Failed to close serial connection to power supply.")
        self.ser = None

    def add_listeners(self, s=list(), v=list(), i=list(), v_o=list(), i_o=list()):
        for j in range(0, self.channels):
            self.state_listeners[j].append(s[j])
            self.voltage_listeners[j].append(v[j])
            self.intensity_listeners[j].append(i[j])
            self.voltage_out_listeners[j].append(v_o[j])
            self.intensity_out_listeners[j].append(i_o[j])

    def start_polling(self) -> None:
        """Start polling the power supply if a serial connection is available."""

        if not self.is_connected():
            self.message_handler.warning("Cannot start polling: connection not established.")
            self.polling = False
            return

        self.message_handler.info("Polling started.")
        self.polling = True
        threading.Thread(target=self.poll, daemon=True).start()

    def stop_polling(self):
        self.message_handler.info("Polling stopped.")
        self.polling = False

    def set_polling_interval(self, intv):
        self.polling_interval = intv

    def set_state(self, channel, value):
        if isinstance(value, int):
            value = value > 0
        if isinstance(value, float):
            value = value > 0

        if self.state[channel - 1] == value:
            return value

        for listener in [l for l in self.state_listeners[channel - 1] if l is not None]:
            listener(value, channel)

        self.state[channel - 1] = value
        return value

    def set_voltage(self, channel, value):
        if self.voltage[channel - 1] == value:
            return value

        for listener in [l for l in self.voltage_listeners[channel - 1] if l is not None]:
            listener(value, channel)

        self.voltage[channel - 1] = value
        return value

    def set_intensity(self, channel, value):
        if self.intensity[channel - 1] == value:
            return value

        for listener in [l for l in self.intensity_listeners[channel - 1] if l is not None]:
            listener(value, channel)

        self.intensity[channel - 1] = value
        return value

    def set_voltage_out(self, channel, value):
        for listener in [l for l in self.voltage_out_listeners[channel - 1] if l is not None]:
            listener(value, channel)

        self.voltage_out[channel - 1] = value
        return value

    def set_intensity_out(self, channel, value):
        for listener in [l for l in self.intensity_out_listeners[channel - 1] if l is not None]:
            listener(value, channel)

        self.intensity_out[channel - 1] = value
        return value

    def send_command(self, command: str, timeout: int = 200, execute: bool = True,
                     wait_reply: bool = True, expected_lines: int = 1):
        """Send a command to the power supply and optionally return its reply."""

        # t = time.time()
        r = self._send_command(command, 1000, execute, wait_reply, expected_lines)
        if external_recorder.is_replaying:
            return r or ""
        if not isinstance(r, str):
            return r
        if self.is_connected() and len(r.splitlines()) != expected_lines:
            self.message_handler.error("Command error: %s expected %d lines but got %s" % (command, expected_lines, r))

        return r

    def _send_command(self, command: str, timeout: int = 200, execute: bool = True,
                      wait_reply: bool = True, expected_lines: int = 1):
        """Low level command execution helper that interacts with the serial port."""

        if not self.is_connected():
            self.message_handler.warning("Cannot send command: not connected.")
            return ""
        if external_recorder.is_replaying:
            logger.info("Skipping power command during replay: %s", command.strip())
            return ""
        with self.send_lock:
            timeout /= 1000
            if execute:
                command += '\n'
            else:
                command += ';'
            self.ser.write(command.encode('utf-8'))
            # record outgoing power-supply command
            external_recorder.record(
                ExternalEvent(time.time(), "out", "power", command.strip())
            )
            if not execute or not wait_reply:
                return
            start = time.time()
            out = bytes()

            while expected_lines > 0 \
                    and self.ser is not None \
                    and time.time() - start < timeout \
                    and self.ser.inWaiting() == 0:
                time.sleep(.005)

            if self.ser is not None and self.ser.inWaiting() > 0:
                while self.ser.inWaiting() > 0 or (time.time() - start < timeout and expected_lines > 0):
                    try:
                        out += self.ser.read()
                        if out[-1] == 10:
                            expected_lines -= 1
                    except (serial.SerialException, IndexError):
                        return ''
            else:
                return ''

            reply = out[:-1].decode()
            external_recorder.record(
                ExternalEvent(time.time(), "in", "power", reply)
            )
            return reply

    def set_state_to_device(self, value, channel=1):
        self.send_command("op%d %d" % (channel, value), expected_lines=0)

        # if self.voltage[channel - 1] == 0:
        #    return self.set_state(channel, 0)
        return self.set_state(channel, value)

    def set_voltage_to_device(self, value, channel=1):
        self.send_command("v%d %06.3f" % (channel, value), expected_lines=0)

        return self.set_voltage(channel, value)

    def set_intensity_to_device(self, value, channel=1):
        self.send_command("i%d %05.3f" % (channel, value), expected_lines=0)

        return self.set_intensity(channel, value)

    def _get_value_from_device(self, value, channel, out, timeout, setter):
        if external_recorder.is_replaying:
            with self._replay_queue_lock:
                self._replay_expected_replies.append((setter, channel, out))

        reply = self.send_command("%s%d%s?" % (value, channel, "o" if out else ""), timeout=timeout)

        if external_recorder.is_replaying and not reply:
            return None

        return self._apply_numeric_reply(setter, channel, out, reply)

    def _apply_numeric_reply(self, setter, channel, out, reply, *, allow_missing=False):
        if not reply:
            if allow_missing:
                return None
            return setter(channel, -1)

        tokens = reply.replace(",", " ").split()
        values = []
        for token in tokens:
            candidate = token
            if out and not is_float_try(candidate) and len(candidate) > 1:
                candidate = candidate[:-1]
            if is_float_try(candidate):
                values.append(float(candidate))

        if len(values) != 1:
            if allow_missing:
                return None
            return setter(channel, -1)

        return setter(channel, values[0])

    def get_state_from_device(self, channel=1, timeout=100):
        return self._get_value_from_device("v", channel, True, timeout, self.set_state)

    def get_voltage_from_device(self, channel=1, timeout=100):
        return self._get_value_from_device("v", channel, False, timeout, self.set_voltage)

    def get_intensity_from_device(self, channel=1, timeout=100):
        return self._get_value_from_device("i", channel, False, timeout, self.set_intensity)

    def get_voltage_out_from_device(self, channel=1, timeout=100):
        return self._get_value_from_device("v", channel, True, timeout, self.set_voltage_out)

    def get_intensity_out_from_device(self, channel=1, timeout=100):
        return self._get_value_from_device("i", channel, True, timeout, self.set_intensity_out)

    def get_all_values_from_device(self, out_only=False):
        if self.poll_lock.locked():
            return
        with self.poll_lock:
            for i in range(1, self.channels + 1):
                if not out_only:
                    self.get_state_from_device(i)
                    self.get_voltage_from_device(i)
                    self.get_intensity_from_device(i)
                self.get_voltage_out_from_device(i)
                self.get_intensity_out_from_device(i)

    def poll(self) -> None:
        """Continuously poll the device while connected and polling is enabled."""

        sleep_minus = 0.0
        warn_no_connection = True
        while self.polling:
            if sleep_minus < self.polling_interval / 1000:
                time.sleep(self.polling_interval / 1000 - sleep_minus)
            elif self.is_connected():
                self.message_handler.warning("Cannot keep up with polling!")
            start = time.time()
            if self.polling and self.is_connected():
                self.get_all_values_from_device(out_only=True)
                self.flush_inbuffer()
                warn_no_connection = True
            elif not self.is_connected():
                if warn_no_connection:
                    warn_no_connection = False
                    self.message_handler.warning("Cannot poll, connection not established.")
                time.sleep(.5)
            sleep_minus = time.time() - start

    def flush_inbuffer(self) -> None:
        """Clear any pending bytes from the serial input buffer when connected."""

        if not self.is_connected():
            return

        with self.send_lock:
            try:
                while self.ser is not None and self.ser.inWaiting() > 0:
                    print("flushing inbuffer")
                    self.ser.read(self.ser.inWaiting())
            except Exception:
                logger.exception("Failed to flush power supply input buffer.")


    def _handle_external_event(self, event: ExternalEvent) -> None:
        if event.kind != "power":
            return
        if not external_recorder.is_replaying:
            with self._replay_queue_lock:
                self._replay_expected_replies.clear()
            return
        if event.direction == "out":
            command = str(event.payload)
            threading.Thread(target=self._replay_outgoing_command, args=(command,), daemon=True).start()
        else:
            reply = str(event.payload)
            threading.Thread(target=self._apply_replay_reply, args=(reply,), daemon=True).start()

    def _replay_outgoing_command(self, command: str) -> None:
        command = command.strip()
        if not command:
            return
        logger.info("Replaying power command: %s", command)
        self.message_handler.info(f"[Replay] {command}")
        try:
            self._send_command(command, execute=True, wait_reply=False, expected_lines=0)
        except Exception:
            logger.exception("Failed to replay power command: %s", command)

    def _apply_replay_reply(self, reply: str) -> None:
        reply = reply.strip()
        if not reply:
            return
        logger.info("Replaying power reply: %s", reply)
        self.message_handler.info(f"[Replay] {reply}")
        expected = None
        with self._replay_queue_lock:
            if self._replay_expected_replies:
                expected = self._replay_expected_replies.popleft()
        if expected:
            setter, channel, out = expected
            result = self._apply_numeric_reply(setter, channel, out, reply, allow_missing=True)
            if result is not None:
                return
        tokens = reply.replace(',', ' ').split()
        if not tokens:
            return
        try:
            channel = 1
            head = tokens[0]
            digits = ''.join(ch for ch in head if ch.isdigit())
            if digits:
                channel = int(digits)
            upper_head = head.upper()
            if upper_head.startswith('STAT'):
                if len(tokens) > 1:
                    state_token = tokens[1].upper()
                    self.set_state(channel, state_token in ('ON', '1', 'TRUE'))
                for token in tokens[2:]:
                    upper = token.upper()
                    if upper.endswith('V'):
                        with suppress(Exception):
                            self.set_voltage_out(channel, float(token[:-1]))
                    elif upper.endswith('A'):
                        with suppress(Exception):
                            self.set_intensity_out(channel, float(token[:-1]))
                return
            for token in tokens:
                upper = token.upper()
                if upper.endswith('V'):
                    with suppress(Exception):
                        self.set_voltage_out(channel, float(token[:-1]))
                elif upper.endswith('A'):
                    with suppress(Exception):
                        self.set_intensity_out(channel, float(token[:-1]))
        except Exception:
            logger.exception("Failed to process replayed power reply: %s", reply)

class MockupPowerSupply(PowerSupply):
    def connect(self, port: str, baudrate: int) -> bool:
        """Pretend to establish a serial connection for the mock device."""

        class _MockSerial:
            def __init__(self) -> None:
                self.is_open = True

            def isOpen(self) -> bool:
                return True

            def inWaiting(self) -> int:
                return 0

            def read(self, *_args, **_kwargs):
                return b""

            def write(self, *_args, **_kwargs):
                return 0

        self.ser = _MockSerial()
        return True

    def __init__(self, *args, **kwargs):
        """Initialise the mock power supply and trigger the parent setup."""

        PowerSupply.__init__(self, *args, **kwargs)

        self.message_handler.success("Mockup values running.")

    def is_connected(self) -> bool:
        """Mockup supplies are always considered connected for UI purposes."""

        return True

    def send_command(self, command: str, timeout=100, execute=True, wait_reply=True, expected_lines=1):
        import random

        if command.find("?") < 0:
            self.message_handler.info("Mockup command: %s" % command)

        if expected_lines == 0:
            time.sleep(.01)
            return ""
        time.sleep(.040 + .010 * expected_lines)
        returns = [str(round(random.random() + 1, 3)) for _ in range(0, expected_lines)]
        return "\n".join(returns)
