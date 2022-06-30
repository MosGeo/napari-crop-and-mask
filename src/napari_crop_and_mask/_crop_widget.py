"""
This module is the main widget for the plugin

It implements the Widget specification.
see: https://napari.org/plugins/guides.html?#widgets
"""
import warnings

import dask.array as da
import numpy as np
from napari.layers.image.image import Image
from napari.layers.shapes.shapes import Shapes
from napari.utils.events.event import Event
from napari.viewer import Viewer
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QCheckBox, QComboBox, QFormLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from superqt import QCollapsible

from napari_crop_and_mask import core
from napari_crop_and_mask._widget_utils import update_layer_combobox


class CropWidget(QWidget):
    """Crop-Mask Widget"""

    def __init__(self, napari_viewer: Viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.setLayout(QVBoxLayout())
        self.initialize_ui()

    def initialize_ui(self):
        """Initlizes the ui"""

        # initialize layout
        layout: QVBoxLayout = self.layout()
        layout.setAlignment(Qt.AlignTop)
        self.setMinimumWidth(350)
        self.setMaximumWidth(500)
        # self.setMaximumHeight(310)
        # self.setFixedHeight(300)
        self.viewer.layers.events.inserted.connect(self.update_lists)
        self.viewer.layers.events.removed.connect(self.update_lists)

        # Label for the tool
        label = QLabel(
            "Select the layer you want to crop, " + "the shape layer used in cropping and get going.",
            self,
        )
        label.setWordWrap(True)
        layout.addWidget(label)

        options_form_widget = QWidget()
        options_form_layout = QFormLayout()
        options_form_widget.setLayout(options_form_layout)
        layout.addWidget(options_form_widget)

        # Add image layer selection
        self.image_combobox = QComboBox(parent=self)
        self.image_combobox.currentIndexChanged.connect(self.image_selection_changed)
        options_form_layout.addRow("Image to crop", self.image_combobox)

        # Add shape layer selection
        self.shape_combobox = QComboBox(parent=self)
        options_form_layout.addRow("Shape to crop", self.shape_combobox)

        # Add advanced option
        options_collapsible = QCollapsible()
        options_collapsible.setText("Advanced options")
        layout.addWidget(options_collapsible)

        # Treat as RGB
        self.is_rgb_checkbox = QCheckBox("Is RGB image", parent=self)
        options_collapsible.addWidget(self.is_rgb_checkbox)

        # Apply cropping on the same layer
        self.overwrite_orginal_checkbox = QCheckBox(text="Overwrite original image", parent=self)
        options_collapsible.addWidget(self.overwrite_orginal_checkbox)

        # Apply cropping on the same layer
        self.inplace_crop_checkbox = QCheckBox(text="Inplace crop (translate layer)", parent=self)
        options_collapsible.addWidget(self.inplace_crop_checkbox)

        # Delete shape layer after cropping
        self.delete_shape_layer_checkbox = QCheckBox(text="Delete shape layer upon completion", parent=self)
        self.delete_shape_layer_checkbox.setChecked(True)
        options_collapsible.addWidget(self.delete_shape_layer_checkbox)

        # Add crop button
        # layout.addStretch()
        crop_button = QPushButton("Crop")
        crop_button.clicked.connect(self.crop_button_clicked)
        layout.addWidget(crop_button)

        self.initialize_lists()

    def image_selection_changed(self):
        """Updates the settings based on selection"""
        if self.image_combobox.currentData() is not None:
            image_layer: Image = self.image_combobox.currentData()
            is_rgb = image_layer.rgb
            # image:da.Array = image_layer.data
            # is_rgb = crop_mask.check_rgb(image)
            self.is_rgb_checkbox.setChecked(is_rgb)
        else:
            self.is_rgb_checkbox.setChecked(False)

    def initialize_lists(self):
        """Updates the UI of the widget based on viewer data"""
        layers = self.viewer.layers
        for layer in layers:
            if isinstance(layer, Image):
                update_layer_combobox(self.image_combobox, "inserted", layer, layer.name)
            elif isinstance(layer, Shapes):
                update_layer_combobox(self.shape_combobox, "inserted", layer, layer.name)
            else:
                pass

    def update_lists(self, event: Event):
        """Updates the layer lists"""
        value = event.value
        if isinstance(event.value, Image):
            update_layer_combobox(self.image_combobox, event.type, value, value.name)
        elif isinstance(event.value, Shapes):
            update_layer_combobox(self.shape_combobox, event.type, value, value.name)
        else:
            pass

    def crop_button_clicked(self):
        """Start cropping"""

        # Get settings from UI
        image_layer: Image = self.image_combobox.currentData()
        shape_layer: Shapes = self.shape_combobox.currentData()
        is_rgb = self.is_rgb_checkbox.isChecked()
        is_overwrite_orginal = self.overwrite_orginal_checkbox.isChecked()
        is_delete_shape_layer = self.delete_shape_layer_checkbox.isChecked()
        is_inplace_crop = self.inplace_crop_checkbox.isChecked()

        # Stopping condition 1
        if image_layer is None:
            warnings.warn("Please select an image to use")
            return

        # Retrive data used
        image_data = image_layer.data
        if not isinstance(image_data, da.Array):
            image_data = da.from_array(image_data)
        is_rgb = image_layer.rgb
        ndim = image_data.ndim
        if is_rgb:
            ndim = ndim - 1

        # Stopping condition 2
        if shape_layer is None:
            shape_layer = self.viewer.add_shapes(data=None, ndim=ndim)
            shape_layer.mode = "add_rectangle"
            shape_layer.name = "cropping mask"
            warnings.warn("Please draw shapes to crop")
            return

        # Get shape layer
        shape_data = shape_layer.data

        # Stopping condition
        if len(shape_data) == 0:
            warnings.warn("no shapes in the selected shapes layer")
            return

        # Attempt to figure out the dimensions of indices
        dimension_indicies = core.infer_demension_indicies(len(image_data.shape), 2, is_rgb)

        # Begin crop and mask
        shape_points = np.vstack(shape_data)
        dimension_min, dimension_max = core.get_bounding_box(shape_points)
        cropped_image = core.crop_mask_hyperrectangle(
            image=image_data,
            dimension_max=dimension_max,
            dimension_min=dimension_min,
            dimension_indicies=dimension_indicies,
            is_mask_only=False,
            mask_value=None,
            is_invert_selection=False,
        )

        # Add/update layer
        if is_overwrite_orginal is False:
            cropped_image_layer = self.add_similar_image_layer(
                data=cropped_image,
                name=image_layer.name + "(cropped)",
                reference_layer=image_layer,
            )
        else:
            cropped_image_layer = image_layer
            cropped_image_layer.data = cropped_image

        # Transform layer if required
        if is_inplace_crop:
            translation = np.zeros_like(dimension_min)
            for ind in dimension_indicies:
                translation[ind] = dimension_min[ind]
            cropped_image_layer.translate = translation
            # print(type(cropped_image_layer))

        # Delete shape layer if required
        if is_delete_shape_layer is True:
            self.viewer.layers.remove(shape_layer)

    def add_similar_image_layer(self, data, name: str, reference_layer: Image) -> Image:
        """Adds a new image layer similar to a reference layer"""
        layer = self.viewer.add_image(
            data,
            name=name,
            opacity=reference_layer.opacity,
            gamma=reference_layer.gamma,
            contrast_limits=reference_layer.contrast_limits,
            colormap=reference_layer.colormap,
            blending=reference_layer.blending,
            interpolation=reference_layer.interpolation,
        )

        return layer
