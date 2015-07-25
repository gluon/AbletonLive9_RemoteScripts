#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/UserSettingsComponent.py
from itertools import count
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.SubjectSlot import subject_slot_group, subject_slot, SubjectEvent
from _Framework.Util import forward_property
from ActionWithOptionsComponent import ActionWithSettingsComponent
import Sysex

class UserSettingsComponent(ControlSurfaceComponent):
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

    @subject_slot_group('normalized_value')
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


class UserComponent(ActionWithSettingsComponent):
    __subject_events__ = (SubjectEvent(name='mode', doc=' Called when the mode changes '), SubjectEvent(name='before_mode_sent', doc=' Called before the mode is sent'), SubjectEvent(name='after_mode_sent', doc=' Called after the mode is sent '))
    settings_layer = forward_property('_settings')('layer')
    settings = forward_property('_settings')('settings')

    def __init__(self, value_control = None, *a, **k):
        super(UserComponent, self).__init__(*a, **k)
        raise value_control != None or AssertionError
        self._settings = self.register_component(UserSettingsComponent())
        self._settings.set_enabled(False)
        self._value_control = value_control
        self._on_value.subject = self._value_control
        self._selected_mode = Sysex.LIVE_MODE

    def show_settings(self):
        self._settings.set_enabled(True)
        return True

    def hide_settings(self):
        self._settings.set_enabled(False)

    def set_settings_info_text(self, text):
        self._settings.set_info_text(text)

    def post_trigger_action(self):
        self.mode = Sysex.LIVE_MODE if self.mode == Sysex.USER_MODE else Sysex.USER_MODE

    @subject_slot('value')
    def _on_value(self, value):
        mode = value[0]
        self._selected_mode = mode
        self.notify_mode(mode)

    def _get_mode(self):
        return self._selected_mode

    def _set_mode(self, mode):
        if mode != self._selected_mode:
            self._selected_mode = mode
            if self.is_enabled():
                self._apply_mode(self._selected_mode)

    mode = property(_get_mode, _set_mode)

    def update(self):
        super(UserComponent, self).update()
        if self.is_enabled():
            self._apply_mode(self._selected_mode)

    def _apply_mode(self, mode):
        self.notify_before_mode_sent(mode)
        self._value_control.send_value((mode,))
        self.notify_after_mode_sent(mode)