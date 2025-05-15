"""Various Exceptions which can occur during use of the API.

Brief:\n
    Various Exceptions which can occur during use of the STAR-System Python API.

Copyright:\n
    2021 STAR-Dundee Ltd
"""

class StatusCode(object):
    """Contains the different status codes and corresponding feedback (text) messages that
       functions in STAR-System can return."""

    def __init__(self):
        self.statusCodes = {
            0: "Success",
            -256: "Failure",
            -257: "The API call is not compatible with this device type.",
            -258: "The API call is not compatible with this device's FPGA version."
                  "The FPGA can be updated to allow this additional functionality.",
            -259: "Failed to get 'Device Information' for this device.",
            -260: "The time-code distribution port mask is invalid.",
            -261: "The time-code flag mode is invalid.",
            -262: "The time-code period is invalid.",
            -263: "The time-code port is invalid.",
            -264: "The identify source port is invalid.",
            -265: "The interface mode port is invalid.",
            -266: "The port is invalid",
            -267: "The logical address is invalid.",
            -268: "The SpaceWire link is invalid.",
            -269: "The measured speed port is invalid.",
            -270: "The speed change events port is invalid.",
            -271: "The state change events port is invalid.",
            -272: "The port routing port is invalid.",
            -273: "The inject error port is invalid.",
            -374: "The precision transmit rate is invalid.",
            -275: "The periodic action port is invalid.",
            -276: "The timestamp events port is invalid.",
            -277: "The clock link is invalid.",
            -278: "The link rate divider is invalid.",
            -279: "The transmit clock link is invalid.",
            -280: "The bit rate is invalid.",
            -281: "The router timeout mode is invalid.",
            -282: "The router timeout period is invalid.",
            -283: "The router disable on silence is invalid.",
            -284: "The router start on request is invalid.",
            -285: "The router enable self addressing is invalid.",
            -286: "The group adaptive routing port mask is invalid.",
            -287: "The group adaptive routing priority is invalid.",
            -288: "The group adaptive routing delete header is invalid.",
            -289: "The group adaptive routing invalid address is invalid.",
            -290: "The SpaceWire link tristate is invalid",
            -291: "SpaceWire link disable is invalid.",
            -292: "SpaceWire link start is invalid.",
            -293: "SpaceWire link autostart is invalid.",
            -294: "The SpaceWire link running is invalid.",
            -295: "The SpaceWire link state is invalid.",
            -296: "The port routing address is invalid.",
            -297: "The inject error error is invalid.",
            -298: "The inject errors parity error is invalid.",
            -299: "The inject errors escape error is invalid.",
            -300: "The inject errors insert FCT error is invalid.",
            -301: "The inject errors suppress FCT error is invalid.",
            -302: "The inject errors increment credit error is invalid.",
            -303: "The inject errors decrement credit error is invalid.",
            -304: "The inject errors disconnect error is invalid.",
            -305: "The periodic action is invalid.",
            -306: "The timestamp method is invalid.",
            -307: "The pulse generator frequency is invalid.",
            -308: "The clock rate multiplier is invalid.",
            -308: "The clock rate divisor is invalid.",
            -310: "The clock rate parameters are invalid.",
            -311: "Can't get clock rate parameters from bit rate.",
            -312: "A pointer parameter is null.",
            -313: "The transmit bit rate is invalid.",
        }

    def getMessage(self, code):
        """Gets the (text) message corresponding to the status code."""
        return self.statusCodes.get(code)


class STARAPIError(Exception):
    """Raised when the C API returns a failing status code."""
    pass