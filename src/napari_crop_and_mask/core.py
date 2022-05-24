"""Cropping image processing"""
import copy
from typing import Any, Iterable, Optional, Sequence, Tuple

import dask.array as da
import numpy as np


def combine_masks(masks: tuple) -> da.Array:
    """Combines multiple masks"""

    combined_mask = da.zeros_like(masks[0])

    for mask in masks:
        combined_mask = da.logical_or(combined_mask, mask)

    return combined_mask


def mask_image(
    image: da.Array,
    mask: da.Array,
    mask_value: Any = np.nan,
    is_invert_selection: bool = False,
) -> da.Array:
    """Mask image based on a mask"""

    masked_image = copy.copy(image)
    if np.isnan(mask_value):
        masked_image = masked_image.astype(float)

    if is_invert_selection is False:
        masked_image[da.logical_not(mask)] = mask_value
    else:
        masked_image[mask] = mask_value

    return masked_image


def mask_irregular(
    image: da.Array,
    masks: Tuple,
    dimension_indicies: Optional[Iterable] = None,
    mask_value: Any = np.nan,
    is_invert_selection: bool = False,
) -> da.Array:
    """Masks image using the provided masks"""

    # Dimension indices
    if dimension_indicies is None:
        dimension_indicies = np.arange(image.ndim)

    mask = combine_masks(masks)

    # Expand dimensions if needed
    all_dimensions = np.arange(image.ndim)
    new_dimensions_selected = [dim not in dimension_indicies for dim in all_dimensions]
    new_dimensions = tuple(all_dimensions[new_dimensions_selected])
    mask = da.expand_dims(mask, axis=new_dimensions)
    mask = da.broadcast_to(mask, shape=image.shape)

    # Mask the image based on selection
    masked_image = mask_image(image, mask=mask, mask_value=mask_value, is_invert_selection=is_invert_selection)
    return masked_image


def crop_hyperrectangle(
    image: da.Array,
    dimension_min: Sequence[int],
    dimension_max: Sequence[int],
    dimension_indicies: Optional[Iterable] = None,
) -> da.Array:
    """Simple rectangle cropping"""
    # Dimension indices
    if dimension_indicies is None:
        dimension_indicies = range(len(dimension_min))

    # Cropping
    cropped_image = image
    for dimension in dimension_indicies:
        indicies = np.arange(dimension_min[dimension], dimension_max[dimension])
        indicies_selected = np.logical_and(indicies >= 0, indicies < image.shape[dimension])
        indicies = indicies[indicies_selected]

        # Apply the crop in the specific dimension
        cropped_image = da.take(cropped_image, indices=indicies, axis=dimension)
    return cropped_image


def mask_hyperrectangle(
    image: da.Array,
    dimension_min: Sequence[int],
    dimension_max: Sequence[int],
    dimension_indicies: Optional[Iterable] = None,
    mask_value: Any = np.nan,
    is_invert_selection: bool = False,
) -> da.Array:
    """Simple rectangle masking"""

    # Dimension indices
    if dimension_indicies is None:
        dimension_indicies = range(len(dimension_min))

    image_shape = image.shape
    meshed_grids = meshgrid_from_size(image_shape)
    mask = da.ones_like(image, dtype=bool)

    print(image_shape, dimension_indicies, dimension_min, dimension_max)

    # Create the mask
    for i, dimension in enumerate(dimension_indicies):
        current_selection = da.logical_and(
            meshed_grids[dimension] >= dimension_min[i],
            meshed_grids[dimension] <= dimension_max[i],
        )
        mask = da.logical_and(mask, current_selection)

    # Mask the image based on selection
    masked_image = mask_image(image, mask=mask, mask_value=mask_value, is_invert_selection=is_invert_selection)

    return masked_image


def infer_demension_indicies(n_dimensions_image: int, n_dimensions_indicies: int = 2, is_rgb: bool = False):
    """
    Try to infer the dimensions to crop based on the image shape and the number of dimensions to
    slice
    """
    # n_dimensions_image = len(image_shape)
    if n_dimensions_indicies == 2:
        if n_dimensions_image >= 5:
            dimension_indicies = (3, 4)
        elif n_dimensions_image == 3 and is_rgb:
            dimension_indicies = (0, 1)
        elif n_dimensions_image == 3 and not is_rgb:
            dimension_indicies = (1, 2)
        elif n_dimensions_image == 2:
            dimension_indicies = (0, 1)

    return dimension_indicies


def meshgrid_from_size(size) -> Tuple[da.Array]:
    """Create meshed grids for the given image size"""

    dimension_indicies = [np.arange(dimension_size) for dimension_size in size]
    meshed_grids = da.meshgrid(*dimension_indicies, indexing="ij")

    return meshed_grids


def get_bounding_box(points: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Returns the dimension minimum and maximum for a set of given points"""
    dimension_min: np.ndarray = np.min(points, axis=0).astype(int)
    dimension_max: np.ndarray = np.max(points, axis=0).astype(int)
    dimension_max[dimension_max == 0] = 1
    return (dimension_min, dimension_max)


def check_rgb(image: da.Array) -> bool:
    """Returns a boolean if the image is rgb"""

    # Normal RGB image
    if image.ndim == 3 and image.shape[2] == 3:
        return True

    # aicsimageio image
    return bool(image.ndim == 6 and image.shape[5] == 3)


def image_size(image: da.Array, is_rgb: bool = False):
    """Returns the image size (x, y)"""
    if is_rgb is True:
        return (image.shape[-3], image.shape[-2])

    return (image.shape[-2], image.shape[-1])


def crop_mask_hyperrectangle(
    image: da.Array,
    dimension_min: Sequence[int],
    dimension_max: Sequence[int],
    dimension_indicies: Optional[Iterable[int]] = None,
    is_mask_only: bool = False,
    mask_value=np.nan,
    is_invert_selection: bool = False,
) -> da.Array:
    """Crops an image given the function"""

    # Attempt automatic detection of dimensions if needed
    if dimension_indicies is None:
        dimension_indicies = list(range(0, len(dimension_min)))

    # Just crop
    if is_mask_only is False and is_invert_selection is False:
        cropped_image = crop_hyperrectangle(
            image,
            dimension_min,
            dimension_max,
            dimension_indicies,
        )

    # masked cropping
    if is_mask_only is True:
        cropped_image = mask_hyperrectangle(
            image,
            dimension_min,
            dimension_max,
            dimension_indicies,
            mask_value=mask_value,
            is_invert_selection=is_invert_selection,
        )

    return cropped_image
