#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/device_enabling.py
from __future__ import absolute_import
import Live
from _Tools.multipledispatch import dispatch
from ableton.v2.base import listens, liveobj_valid
from ableton.v2.control_surface.control import ButtonControl, control_list
from ableton.v2.control_surface.component import Component
from .device_navigation import DeviceChainEnabledStateWatcher, is_active_element

def set_enabled(device, is_on):
    device.parameters[0].value = int(is_on)


def is_on(device):
    return bool(device.parameters[0].value)


class DeviceEnablingComponent(Component):
    toggle_buttons = control_list(ButtonControl)

    def __init__(self, device_navigation = None, *a, **k):
        raise device_navigation is not None or AssertionError
        super(DeviceEnablingComponent, self).__init__(*a, **k)
        self._device_navigation = device_navigation
        self.__on_items_changed.subject = device_navigation
        self._watcher = self.register_disconnectable(DeviceChainEnabledStateWatcher(device_navigation=device_navigation))
        self.__on_enabled_state_changed.subject = self._watcher
        self._update_buttons()

    @toggle_buttons.pressed
    def toggle_buttons(self, button):
        item = self._item_for_button(button)
        if item.is_scrolling_indicator:
            if button.index == 0:
                self._device_navigation.scroll_left()
            else:
                self._device_navigation.scroll_right()
        else:
            self._toggle_device(item.item)

    @listens('enabled_state')
    def __on_enabled_state_changed(self):
        self._update_buttons()

    @listens('items')
    def __on_items_changed(self, *a):
        self._update_buttons()

    def _item_for_button(self, button):
        return self._device_navigation.items[button.index]

    def _color_for_device(self, device_or_pad):
        if liveobj_valid(device_or_pad):
            return 'DefaultButton.On' if is_active_element(device_or_pad) else 'DefaultButton.Off'
        else:
            return 'DefaultButton.Disabled'

    @dispatch(Live.DrumPad.DrumPad)
    def _toggle_device(self, drum_pad):
        if liveobj_valid(drum_pad):
            drum_pad.mute = not drum_pad.mute

    @dispatch(object)
    def _toggle_device(self, device):
        if liveobj_valid(device) and device.parameters[0].is_enabled:
            set_enabled(device, not is_on(device))

    def _update_buttons(self):
        self.toggle_buttons.control_count = len(self._device_navigation.items)
        for button in self.toggle_buttons:
            item = self._item_for_button(button)
            if item.is_scrolling_indicator:
                button.color = 'DefaultButton.On'
            else:
                button.color = self._color_for_device(item.item)