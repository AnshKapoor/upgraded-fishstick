"""Represents a SpaceWire time-code.

Brief:\n
    Represents a SpaceWire time-code.

Copyright:\n
    2022 STAR-Dundee Ltd
"""

class TimeCode(object):
    """Represents a SpaceWire time-code.

    Attributes:\n
        numSinceLastTx (int): A count of the number of time-codes since the last time-code was transmitted.
        value (int): Value of the time-code.

    Args:\n
        See `STAR_system.time_code.TimeCode` class attributes.\n
    """

    def __init__(self, value, numSinceLastTx=0):
        """Constructor:\n
            Initialises a `STAR_system.time_code.TimeCode` object.\n

        Raises:\n
            TypeError:\n
                numSinceLastTx or value is not an int.\n
            ValueError:\n
                numSinceLastTx is negative.\n
        """

        if type(numSinceLastTx) != int:
            raise TypeError("numSinceLastTx must be int.")
        if type(value) != int:
            raise TypeError("value must be int.")
        if numSinceLastTx < 0:
            raise ValueError("Invalid numSinceLastTx. Counter cannot be negative.")

        self.numSinceLastTx = numSinceLastTx
        self.value = value