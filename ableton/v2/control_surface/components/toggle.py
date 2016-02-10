#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/components/toggle.py
from __future__ import absolute_import, print_function
from ...base import listens
from ..component import Component

class ToggleComponent(Component):
    """
    Maps a toggle button to a boolean property of the Live model.
    """
    is_private = True
    is_momentary = False
    read_only = False

    def __init__(self, property_name = None, subject = None, is_momentary = False, model_transform = None, view_transform = None, read_only = False, *a, **k):
        if not property_name:
            raise AssertionError
            super(ToggleComponent, self).__init__(*a, **k)
            self._property_name = property_name
            self._property_slot = self.register_slot(subject, self._on_property_changed_in_model, property_name)
            self._property_button = None
            if is_momentary:
                self.is_momentary = is_momentary
            if model_transform:
                self.model_transform = model_transform
            if view_transform:
                self.view_transform = view_transform
            self.read_only = read_only and read_only

    def model_transform(self, value):
        return value

    def view_transform(self, value):
        return value

    @property
    def subject(self):
        return self._property_slot.subject

    @subject.setter
    def subject(self, model):
        self._property_slot.subject = model
        self.update()

    @property
    def value(self):
        if self.subject:
            return getattr(self.subject, self._property_name)

    @value.setter
    def value(self, value):
        setattr(self.subject, self._property_name, value)

    def set_toggle_button(self, button):
        raise button is None or not self.is_momentary or button.is_momentary() or AssertionError
        self.__on_button_value.subject = button
        self._update_button()

    def on_enabled_changed(self):
        self.update()

    def update(self):
        super(ToggleComponent, self).update()
        self._update_button()

    def _update_button(self):
        if self.is_enabled():
            button = self.__on_button_value.subject
            if button:
                button.set_light(self.view_transform(self.value))

    def _on_property_changed_in_model(self):
        self._update_button()

    @listens('value')
    def __on_button_value(self, value):
        if self.is_enabled() and not self.read_only:
            if self.is_momentary:
                if value:
                    self.value = self.model_transform(True)
                else:
                    self.value = self.model_transform(False)
            elif value:
                self.value = self.model_transform(not self.value)