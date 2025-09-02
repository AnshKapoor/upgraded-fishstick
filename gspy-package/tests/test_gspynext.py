#!/usr/bin/env python

"""Tests for `gspynext` package."""

import pytest


# Assuming getDevice is properly exposed in the utilities module
from gspy_egse.gui.utils.utilities import getDevice

def test_get_device_returns_devices_or_none():
    """
    Test that getDevice() returns a list of devices or None.
    """
    device_list = getDevice

    # If device_list is None, skip test (no hardware connected)
    if device_list is None:
        pytest.skip("No SpaceWire devices connected or STARSystem error.")
    
    # Otherwise, assert it's a non-empty list of strings
    assert isinstance(device_list, list), "getDevice should return a list"
    assert all(isinstance(dev, str) for dev in device_list), "All items should be strings"
    assert len(device_list) > 0, "Device list should not be empty"