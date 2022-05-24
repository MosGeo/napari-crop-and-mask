"""Widget Utilites"""
from typing import Any

from napari.layers.base.base import Layer
from napari.utils.events.event import Event
from qtpy.QtWidgets import QComboBox


def get_combobox_item_index(combobox: QComboBox, item_data: Any) -> list[int]:
    """Returns the index of an item based on item data (not text)"""
    item_indecies = [i for i in range(combobox.count()) if combobox.itemData(i) == item_data]
    return item_indecies


def refresh_combobox_layer_name(event: Event, combobox: QComboBox):
    """Update combobox layer name"""
    layer: Layer = event.source
    item_indecies = get_combobox_item_index(combobox, layer)
    for item_index in item_indecies:
        combobox.setItemText(item_index, layer.name)


def update_layer_combobox(combobox: QComboBox, event_type: str, layer: Layer, text: str):
    """Update combobox"""
    if event_type == "inserted":
        combobox.addItem(text, layer)
        layer.events.name.connect(lambda event, combobox=combobox: refresh_combobox_layer_name(event, combobox))
    elif event_type == "removed":
        item_indecies = get_combobox_item_index(combobox, layer)
        layer.events.name.disconnect(lambda event, combobox=combobox: refresh_combobox_layer_name(event, combobox))
        for item_index in item_indecies:
            combobox.removeItem(item_index)
    else:
        pass
