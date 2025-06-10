"""Represents an error in data control.

Brief:\n
    Represents an error in data control.

Copyright:\n
    2021 STAR-Dundee Ltd
"""

from gspy_egse.gui.STAR_system.STAR_enums import STAR_ERROR_IN_DATA_TYPE


class ErrorInData(object):
    """Represents an error in data control.
    
    Not all devices support this item type, and receiving this type is not possible.

    Attributes:\n
        errorType (STAR_system.STAR_enums.STAR_ERROR_IN_DATA_TYPE): The type of error to inject on a following data character.
    """

    def __init__(self, errorType):
        """Constructor:\n
            Initialises an error in data object.

        Args:\n
            errorType (STAR_system.STAR_enums.STAR_ERROR_IN_DATA_TYPE): The type of error to inject on a following data character.

        Raises:\n
            TypeError:\n
                errorType was not a STAR_ERROR_IN_DATA_TYPE.
        """

        if isinstance(errorType, STAR_ERROR_IN_DATA_TYPE) is False:
            raise TypeError("errorType must be STAR_ERROR_IN_DATA_TYPE.")

        self.errorType = errorType
