from typing import Any, Union

from napari.layers.base.base import Layer
from qtpy.QtWidgets import QComboBox


def get_combobox_item_index(
    combobox: QComboBox, item_data: Any
) -> Union[int, list[int], None]:
    """Returns the index of an item based on item data (not text)"""
    item_index = [
        i for i in range(combobox.count()) if combobox.itemData(i) == item_data
    ]
    if len(item_index) == 1:
        return item_index[0]
    elif len(item_index) > 1:
        return item_index
    else:
        return None


def refresh_combobox_layer_name(event, combobox):
    """Update combobox layer name"""
    layer = event.source
    item_index = get_combobox_item_index(combobox, layer)
    combobox.setItemText(item_index, layer.name)


def update_layer_combobox(
    combobox: QComboBox, event_type: str, layer: Layer, text: str
):
    """Update combobox"""
    if event_type == "inserted":
        combobox.addItem(text, layer)
        name_func = (
            lambda event, combobox=combobox: refresh_combobox_layer_name(
                event, combobox
            )
        )
        layer.events.name.connect(name_func)
    elif event_type == "removed":
        item_index = get_combobox_item_index(combobox, layer)
        name_func = (
            lambda event, combobox=combobox: refresh_combobox_layer_name(
                event, combobox
            )
        )
        layer.events.name.disconnect(name_func)
        combobox.removeItem(item_index)
    else:
        pass
