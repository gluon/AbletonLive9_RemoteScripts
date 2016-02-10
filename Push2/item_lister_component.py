#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/item_lister_component.py
from __future__ import absolute_import, print_function
from itertools import izip
from ableton.v2.base import forward_property, listens, SlotManager, Subject
from ableton.v2.control_surface import Component, CompoundComponent
from ableton.v2.control_surface.control import control_list, ButtonControl, RadioButtonControl

class SimpleItemSlot(SlotManager, Subject):
    __events__ = ('name',)

    def __init__(self, item = None, name = '', nesting_level = -1, icon = '', *a, **k):
        super(SimpleItemSlot, self).__init__(*a, **k)
        self._item = item
        self._name = name
        self._nesting_level = nesting_level
        self._icon = icon
        self.__on_name_changed.subject = self._item if hasattr(self._item, 'name_has_listener') else None

    @listens('name')
    def __on_name_changed(self):
        self.notify_name()
        self._name = self._item.name

    @property
    def name(self):
        return self._name

    @property
    def item(self):
        return self._item

    @property
    def nesting_level(self):
        return self._nesting_level

    @property
    def icon(self):
        return self._icon


class ItemSlot(SimpleItemSlot):

    def __init__(self, item = None, nesting_level = 0, **k):
        raise item != None or AssertionError
        super(ItemSlot, self).__init__(item=item, name=item.name, nesting_level=nesting_level, **k)

    def __eq__(self, other):
        return id(self) == id(other) or self._item == other

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self._item)

    _live_ptr = forward_property('_item')('_live_ptr')


class ItemProvider(Subject):
    """ General interface to implement for providers used in ItemListerComponent """
    __events__ = ('items', 'selected_item')

    @property
    def items(self):
        """
        Returns a list of tuples, each of which contains an item
        followed by its nesting level
        """
        return []

    @property
    def selected_item(self):
        return None


class ItemListerComponentBase(CompoundComponent):
    __events__ = ('items',)

    def __init__(self, item_provider = ItemProvider(), num_visible_items = 8, *a, **k):
        super(ItemListerComponentBase, self).__init__(*a, **k)
        self._item_offset = 0
        self._item_provider = item_provider
        self._items = []
        self._num_visible_items = num_visible_items
        self.__on_items_changed.subject = item_provider
        self.update_items()

    def reset_offset(self):
        self._item_offset = 0

    @property
    def items(self):
        return self._items

    @property
    def item_provider(self):
        return self._item_provider

    def _get_item_offset(self):
        return self._item_offset

    def _set_item_offset(self, offset):
        self._item_offset = offset
        self.update_items()

    item_offset = property(_get_item_offset, _set_item_offset)

    def can_scroll_left(self):
        return self.item_offset > 0

    def can_scroll_right(self):
        items = self._item_provider.items[self.item_offset:]
        return len(items) > self._num_visible_items

    def scroll_left(self):
        self.item_offset -= 1

    def scroll_right(self):
        self.item_offset += 1

    def _adjust_offset(self):
        num_raw_items = len(self._item_provider.items)
        list_length = self._num_visible_items
        if list_length >= num_raw_items or self._item_offset >= num_raw_items - list_length:
            self._item_offset = max(0, num_raw_items - list_length)

    def update_items(self):
        for item in self._items:
            self.disconnect_disconnectable(item)

        self._adjust_offset()
        items = self._item_provider.items[self.item_offset:]
        num_slots = min(self._num_visible_items, len(items))

        def create_slot(index, item, nesting_level):
            slot = None
            if index == 0 and self.can_scroll_left():
                slot = SimpleItemSlot(icon='page_left.svg')
                slot.is_scrolling_indicator = True
            elif index == num_slots - 1 and self.can_scroll_right():
                slot = SimpleItemSlot(icon='page_right.svg')
                slot.is_scrolling_indicator = True
            else:
                slot = ItemSlot(item=item, nesting_level=nesting_level)
                slot.is_scrolling_indicator = False
            return slot

        new_items = []
        if num_slots > 0:
            new_items = [ create_slot(index, *item) for index, item in enumerate(items[:num_slots]) if item[0] != None ]
        self._items = map(self.register_disconnectable, new_items)
        self.notify_items()

    @listens('items')
    def __on_items_changed(self):
        self.update_items()


class ScrollComponent(Component):
    __events__ = ('scroll',)
    button = ButtonControl(color='ItemNavigation.ItemNotSelected', repeat=True)

    @button.pressed
    def button(self, button):
        self.notify_scroll()


class ScrollOverlayComponent(CompoundComponent):

    def __init__(self, *a, **k):
        super(ScrollOverlayComponent, self).__init__(*a, **k)
        self._scroll_left_component, self._scroll_right_component = self.register_components(ScrollComponent(is_enabled=False), ScrollComponent(is_enabled=False))
        self.__on_scroll_left.subject = self._scroll_left_component
        self.__on_scroll_right.subject = self._scroll_right_component

    scroll_left_layer = forward_property('_scroll_left_component')('layer')
    scroll_right_layer = forward_property('_scroll_right_component')('layer')

    def can_scroll_left(self):
        raise NotImplementedError

    def can_scroll_right(self):
        raise NotImplementedError

    def scroll_left(self):
        raise NotImplementedError

    def scroll_right(self):
        raise NotImplementedError

    def update_scroll_buttons(self):
        if self.is_enabled():
            self._scroll_left_component.set_enabled(self.can_scroll_left())
            self._scroll_right_component.set_enabled(self.can_scroll_right())

    @listens('scroll')
    def __on_scroll_left(self):
        self.scroll_left()

    @listens('scroll')
    def __on_scroll_right(self):
        self.scroll_right()

    def update(self):
        super(ScrollOverlayComponent, self).update()
        if self.is_enabled():
            self.update_scroll_buttons()


class ItemListerComponent(ItemListerComponentBase):
    select_buttons = control_list(ButtonControl, unavailable_color='ItemNavigation.NoItem')

    def __init__(self, *a, **k):
        super(ItemListerComponent, self).__init__(*a, **k)
        self._scroll_overlay = self.register_component(ScrollOverlayComponent(is_enabled=True))
        self._scroll_overlay.can_scroll_left = self.can_scroll_left
        self._scroll_overlay.can_scroll_right = self.can_scroll_right
        self._scroll_overlay.scroll_left = self.scroll_left
        self._scroll_overlay.scroll_right = self.scroll_right
        self.__on_items_changed.subject = self
        self.__on_selection_changed.subject = self._item_provider

    scroll_left_layer = forward_property('_scroll_overlay')('scroll_left_layer')
    scroll_right_layer = forward_property('_scroll_overlay')('scroll_right_layer')

    @listens('items')
    def __on_items_changed(self):
        self.select_buttons.control_count = len(self.items)
        self._update_button_colors()
        self._scroll_overlay.update_scroll_buttons()

    @listens('selected_item')
    def __on_selection_changed(self):
        self._update_button_colors()

    def _update_button_colors(self):
        selected_item = self._item_provider.selected_item
        for button, item in izip(self.select_buttons, self.items):
            is_selected = item == selected_item
            button.color = self._color_for_button(button.index, is_selected)

    def _color_for_button(self, button_index, is_selected):
        if is_selected:
            return 'ItemNavigation.ItemSelected'
        return 'ItemNavigation.ItemNotSelected'

    @select_buttons.pressed
    def select_buttons(self, button):
        self._on_select_button_pressed(button)

    @select_buttons.pressed_delayed
    def select_buttons(self, button):
        self._on_select_button_pressed_delayed(button)

    @select_buttons.released
    def select_buttons(self, button):
        self._on_select_button_released(button)

    @select_buttons.released_immediately
    def select_buttons(self, button):
        self._on_select_button_released_immediately(button)

    def _on_select_button_pressed(self, button):
        pass

    def _on_select_button_pressed_delayed(self, button):
        pass

    def _on_select_button_released(self, button):
        pass

    def _on_select_button_released_immediately(self, button):
        pass