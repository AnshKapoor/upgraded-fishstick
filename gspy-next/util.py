from typing import Optional

from STAR_system.STAR_system import STARSystem
from STAR_system.STAR_exceptions import STARAPIError
from STAR_system.device import Device


def getFirstDevice() -> Optional[Device]:
    """
    Gets the first device if there is one. Returns the first device available.
    Returns None if no devices are available.
    """

    # Get the list of available SpaceWire devices.
    starSystem = STARSystem()

    try:
        devices = starSystem.getDeviceList()
    except (STARAPIError, TypeError, ValueError):
        raise

    # If at least one device is present ...
    if len(devices) > 0:
        # Get first device.
        firstDevice = devices[0]

        # Return first device
        return firstDevice

    return None
