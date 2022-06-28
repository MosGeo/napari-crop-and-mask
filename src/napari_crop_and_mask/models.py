from enum import Enum

from numpy import nan


class MaskMode(Enum):
    """An enum to hold the mask modes"""

    RECTANGULAR_MASK_NAN = "Rectangular mask with NaN"
    RECTANGULAR_MASK_ZERO = "Rectangular mask with zeros"
    IRREGULAR_MASK_NAN = "Irregular mask with NaN"
    IRREGULAR_MASK_ZERO = "Irregular mask with zeros"

    def __str__(self) -> str:
        return self.value

    def is_rectangular(self) -> bool:
        """Returns boolean fro rectangular cropping"""
        is_rectangular = self in [
            MaskMode.RECTANGULAR_MASK_NAN,
            MaskMode.RECTANGULAR_MASK_ZERO,
        ]
        return is_rectangular

    def is_mask_only(self) -> bool:
        return True

    @property
    def mask_value(self) -> float:
        """Returns the mask value"""
        if self == MaskMode.RECTANGULAR_MASK_NAN or self == MaskMode.IRREGULAR_MASK_NAN:
            mask_value = nan
        else:
            mask_value = 0

        return mask_value


class InclusionMode(Enum):
    """An enum to hold the crop modes"""

    INCLUDE_SELECTED = "Keep selected shapes"
    EXCLUDE_SELECTED = "Exclude selected shapes"

    def __str__(self) -> str:
        """Returns the string representation"""
        return self.value

    def is_invert_selection(self) -> bool:
        if self == InclusionMode.EXCLUDE_SELECTED:
            return True
        return False
