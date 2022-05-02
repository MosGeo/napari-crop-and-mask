"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/plugins/guides.html?#widgets
"""
from napari.layers.image.image import Image
from napari.layers.shapes.shapes import Shapes
from napari.utils.events.event import Event
from napari.viewer import Viewer
from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from superqt import QEnumComboBox

from napari_crop_and_mask.models import CropMode, InclusionMode
from napari_crop_and_mask.widget_utils import update_layer_combobox


class ExampleQWidget(QWidget):
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
        self.setFixedHeight(300)
        self.viewer.layers.events.inserted.connect(self.update_lists)
        self.viewer.layers.events.removed.connect(self.update_lists)

        # Label for the tool
        label = QLabel(
            "Select the layer you want to crop, "
            + "the shape layer used in cropping and get going.",
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
        self.image_combobox.currentIndexChanged.connect(
            self.image_selection_changed
        )
        options_form_layout.addRow("Image to crop", self.image_combobox)

        # Add shape layer selection
        self.shape_combobox = QComboBox(parent=self)
        options_form_layout.addRow("Shape to crop", self.shape_combobox)

        # Crop Mode selection
        self.crop_mode_combobox = QEnumComboBox(
            enum_class=CropMode, parent=self
        )
        self.crop_mode_combobox.currentIndexChanged.connect(
            self.crop_mode_changed
        )
        options_form_layout.addRow("Crop-mask mode", self.crop_mode_combobox)

        # # Add include exclude mode selection
        self.inclusion_mode_combobox = QEnumComboBox(
            enum_class=InclusionMode, parent=self
        )
        options_form_layout.addRow(
            "Inclusion mode", self.inclusion_mode_combobox
        )

        # Treat as RGB
        self.is_rgb_checkbox = QCheckBox("Is RGB image", parent=self)
        layout.addWidget(self.is_rgb_checkbox)

        # Apply cropping on the same layer
        self.inplace_crop_checkbox = QCheckBox(
            text="Inplace crop", parent=self
        )
        layout.addWidget(self.inplace_crop_checkbox)

        # Delete shape layer after cropping
        self.delete_shape_layer_checkbox = QCheckBox(
            text="Delete shape layer upon completion", parent=self
        )
        self.delete_shape_layer_checkbox.setChecked(True)
        layout.addWidget(self.delete_shape_layer_checkbox)

        # Add crop button
        layout.addStretch()
        crop_button = QPushButton("Crop!")
        # crop_button.clicked.connect(self.crop_button_click)
        layout.addWidget(crop_button)

        self.initialize_lists()
        self.crop_mode_changed()

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

    def crop_mode_changed(self):
        """Enables the inclusions masking option based on crop mode"""
        is_crop = (
            self.crop_mode_combobox.currentData() == CropMode.RECTANGULAR_CROP
        )
        self.inclusion_mode_combobox.setEnabled(not is_crop)

    def initialize_lists(self):
        """Updates the UI of the widget based on viewer data"""
        layers = self.viewer.layers
        for layer in layers:
            if isinstance(layer, Image):
                self.image_combobox.addItem(layer.name, userData=layer)
            elif isinstance(layer, Shapes):
                self.shape_combobox.addItem(layer.name, userData=layer)

    def update_lists(self, event: Event):
        """Updates the layer lists"""
        value = event.value
        if isinstance(event.value, Image):
            update_layer_combobox(
                self.image_combobox, event.type, value, value.name
            )
        elif isinstance(event.value, Shapes):
            update_layer_combobox(
                self.shape_combobox, event.type, value, value.name
            )
        else:
            pass
