#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/chain_selection_component.py
from __future__ import absolute_import, print_function
from ableton.v2.base import SlotManager, listens, liveobj_valid
from .item_lister_component import ItemListerComponent, ItemProvider

class ChainProvider(SlotManager, ItemProvider):

    def __init__(self, *a, **k):
        super(ChainProvider, self).__init__(*a, **k)
        self._rack = None

    def set_rack(self, rack):
        if rack != self._rack:
            rack_view = rack.view if rack else None
            self._rack = rack
            self.__on_chains_changed.subject = rack
            self.__on_selected_chain_changed.subject = rack_view
            self.notify_items()
            self.notify_selected_item()

    @property
    def items(self):
        chains = self._rack.chains if liveobj_valid(self._rack) else []
        return [ (chain, 0) for chain in chains ]

    @property
    def selected_item(self):
        if liveobj_valid(self._rack):
            return self._rack.view.selected_chain

    def select_chain(self, chain):
        self._rack.view.selected_chain = chain

    @listens('chains')
    def __on_chains_changed(self):
        self.notify_items()

    @listens('selected_chain')
    def __on_selected_chain_changed(self):
        self.notify_selected_item()


class ChainSelectionComponent(ItemListerComponent):

    def __init__(self, *a, **k):
        self._chain_parent = ChainProvider()
        super(ChainSelectionComponent, self).__init__(item_provider=self._chain_parent, *a, **k)
        self.register_disconnectable(self._chain_parent)

    def _on_select_button_pressed(self, button):
        self._chain_parent.select_chain(self.items[button.index].item)

    def set_parent(self, parent):
        raise parent is None or parent.can_have_chains or AssertionError
        self._chain_parent.set_rack(parent)