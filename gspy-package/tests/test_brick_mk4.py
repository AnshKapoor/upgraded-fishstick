#!/usr/bin/env python3
# tests/test_star_channels.py

import os
import pytest

from gspy_egse.gui.STAR_system.STAR_system import STARSystem
from gspy_egse.gui.STAR_system.STAR_exceptions import STARAPIError
from gspy_egse.gui.STAR_system.common import STARCommon
from gspy_egse.gui.STAR_system.channel_listener import ChannelListener
from gspy_egse.gui.STAR_system.STAR_enums import STAR_CHANNEL_DIRECTION


# ---- Helpers / callback ----

class ChannelListenerUserData:
    def __init__(self, dummy_value: int):
        self.int_member = dummy_value


def channel_callback(channelListenerIdentifier, driverIdentifier, deviceIdentifier,
                     channelIdentifier, channelOpened, channelNumber, pContextObject):
    # Minimal callback to satisfy the API; no printing in tests
    _ = (
        channelListenerIdentifier,
        driverIdentifier,
        deviceIdentifier,
        channelIdentifier,
        channelOpened,
        channelNumber,
    )
    # If a context object was passed, ensure it can be restored
    STARCommon.restoreContextObject(pContextObject)


def _pick_first_channel(channel_collection):
    """
    Return the first Channel object from whatever structure getChannels() returns.
    Works if it's a list/tuple/dict/iterable.
    """
    if isinstance(channel_collection, dict):
        # Prefer the lowest channel number if keys are numbers
        try:
            first_key = sorted(channel_collection.keys())[0]
            return channel_collection[first_key]
        except Exception:
            return next(iter(channel_collection.values()))
    else:
        # Assume iterable of Channel objects
        return next(iter(channel_collection))


# ---- Fixtures ----

@pytest.fixture(scope="module")
def star_system():
    return STARSystem()


@pytest.fixture(scope="module")
def first_device(star_system):
    try:
        devices = star_system.getDeviceList()
    except (STARAPIError, TypeError, ValueError):
        pytest.skip("Could not retrieve list of available devices from STARSystem.")

    if not devices:
        pytest.skip("No devices found.")

    return devices[0]


@pytest.fixture(scope="module")
def first_channel(first_device):
    try:
        device_channels = first_device.getChannels()
    except STARAPIError:
        pytest.skip("Could not get channels for the first device.")

    try:
        ch = _pick_first_channel(device_channels)
    except StopIteration:
        pytest.skip("Device has no channels.")

    return ch


# ---- Tests ----

def test_star_system_detects_device(first_device):
    # Basic sanity: we got a device object
    assert first_device is not None


def test_can_list_channels(first_device):
    try:
        device_channels = first_device.getChannels()
    except STARAPIError:
        pytest.skip("Could not get channels.")

    # Ensure we can iterate and channels look sane
    channels = list(device_channels.values()) if isinstance(device_channels, dict) else list(device_channels)
    assert len(channels) > 0, "Expected at least one channel on the device."
    assert hasattr(channels[0], "channelNumber")


def test_can_create_channel_listener(first_device):
    # Creating a listener should not raise
    user_data = ChannelListenerUserData(100)
    listener = ChannelListener(channel_callback, first_device.deviceID, None, user_data)
    assert listener is not None


def test_open_and_close_first_channel(first_channel):
    """
    This test actually opens/closes a channel.
    It is SKIPPED by default to avoid altering device state.
    Enable by setting STAR_ALLOW_CHANNEL_OPEN=1 in the environment.
    """
    if os.environ.get("STAR_ALLOW_CHANNEL_OPEN") != "1":
        pytest.skip("Set STAR_ALLOW_CHANNEL_OPEN=1 to enable open/close test.")

    # Try to open INOUT and then close
    try:
        first_channel.openChannelToDevice(STAR_CHANNEL_DIRECTION.INOUT)
    except (STARAPIError, TypeError) as e:
        pytest.fail(f"Could not open channel: {e}")
    finally:
        try:
            first_channel.close()
        except (STARAPIError, TypeError) as e:
            pytest.fail(f"Could not close channel: {e}")
