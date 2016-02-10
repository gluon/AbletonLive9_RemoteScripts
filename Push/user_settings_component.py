#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push/user_settings_component.py
from __future__ import absolute_import, print_function
from itertools import count
from ableton.v2.base import forward_property, listens_group
from ableton.v2.control_surface import Component, CompoundComponent
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.control_surface.elements import DisplayDataSource
from pushbase.user_component import UserComponentBase
from pushbase import consts

class UserSettingsComponent(Component):
    """ Component for changing a list of settings """

    def __init__(self, *a, **k):
        super(UserSettingsComponent, self).__init__(*a, **k)
        self._name_sources = [ DisplayDataSource() for _ in xrange(4) ]
        self._value_sources = [ DisplayDataSource() for _ in xrange(4) ]
        self._info_source = DisplayDataSource()
        self._settings = []
        self._encoders = []

    def set_display_line1(self, display):
        if display:
            display.set_data_sources(self._value_sources)

    def set_display_line2(self, display):
        if display:
            display.set_data_sources(self._name_sources)

    def set_display_line3(self, display):
        if display:
            display.reset()

    def set_display_line4(self, display):
        if display:
            display.set_data_sources([self._info_source])

    def set_encoders(self, encoders):
        self._encoders = encoders or []
        self._on_encoder_value.replace_subjects(self._encoders[::2], count())

    def _set_settings(self, settings):
        self._settings = settings.values()
        self._update_display()

    def _get_settings(self):
        return self._settings

    settings = property(_get_settings, _set_settings)

    def set_info_text(self, info_text):
        self._info_source.set_display_string(info_text)

    @listens_group('normalized_value')
    def _on_encoder_value(self, value, index):
        if index >= 0 and index < len(self._settings) and self._settings[index].change_relative(value):
            self._update_display()

    def _update_display(self):
        for index, setting in enumerate(self._settings):
            self._name_sources[index].set_display_string(setting.name)
            self._value_sources[index].set_display_string(str(setting))

    def update(self):
        super(UserSettingsComponent, self).update()
        if self.is_enabled():
            self._update_display()


class UserComponent(UserComponentBase, CompoundComponent):
    action_button = ButtonControl(**consts.SIDE_BUTTON_COLORS)
    settings_layer = forward_property('_settings')('layer')
    settings = forward_property('_settings')('settings')

    def __init__(self, *a, **k):
        super(UserComponent, self).__init__(*a, **k)
        self._settings = self.register_component(UserSettingsComponent())
        self._settings.set_enabled(False)

    @action_button.pressed_delayed
    def action_button(self, button):
        self._settings.set_enabled(True)

    @action_button.released_delayed
    def hide_settings(self, button):
        self._settings.set_enabled(False)

    def set_settings_info_text(self, text):
        self._settings.set_info_text(text)

    @action_button.released_immediately
    def post_trigger_action(self, button):
        self.toggle_mode()