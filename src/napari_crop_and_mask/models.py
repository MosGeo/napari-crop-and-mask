from enum import Enum


class CropMode(Enum):
    """An enum to hold the crop modes"""

    RECTANGULAR_CROP = "Rectangular crop"
    RECTANGULAR_MASK_NAN = "Rectangular mask with NaN"
    RECTANGULAR_MASK_ZERO = "Rectangular mask with zeros"
    IRREGULAR_MASK_NAN = "Irregular mask with NaN"
    IRREGULAR_MASK_ZERO = "Irregular mask with zeros"

    def __str__(self):
        return self.value


class InclusionMode(Enum):
    """An enum to hold the crop modes"""

    INCLUDE_SELECTED = "Keep selected shapes"
    EXCLUDE_SELECTED = "Exclude selected shapes"

    def __str__(self):
        return self.value
