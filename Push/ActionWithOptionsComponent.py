#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/ActionWithOptionsComponent.py
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.Util import in_range
from _Framework import Task
from _Framework import Defaults
import consts

class ActionWithSettingsComponent(CompoundComponent):
    SETTINGS_DELAY = Defaults.MOMENTARY_DELAY

    def __init__(self, *a, **k):
        super(ActionWithSettingsComponent, self).__init__(*a, **k)
        self._is_showing_settings = False
        self._action_button = None
        self._settings_task = Task.Task()

    def set_action_button(self, action_button):
        raise not action_button or action_button.is_momentary() or AssertionError
        self._action_button = action_button
        self._on_action_button_value.subject = action_button
        self._update_action_button()

    def show_settings(self):
        """ Please override. Returns True if succeeded to show settings """
        return True

    def hide_settings(self):
        """ Please override """
        pass

    def trigger_action(self):
        """ Called whenever action button is pressed. """
        pass

    def post_trigger_action(self):
        """ Called whenever action button is released. Unless settings
        are shown."""
        pass

    def _do_show_settings(self):
        self._is_showing_settings = self.show_settings()

    def _do_hide_settings(self):
        self.hide_settings()
        self._is_showing_settings = False

    @subject_slot('value')
    def _on_action_button_value(self, value):
        if self.is_enabled():
            self._settings_task.kill()
            if value:
                self._settings_task = self._tasks.add(Task.sequence(Task.wait(self.SETTINGS_DELAY), Task.run(self._do_show_settings)))
                self.trigger_action()
            elif self._is_showing_settings:
                self.hide_settings()
                self._is_showing_settings = False
            else:
                self.post_trigger_action()
            self._update_action_button()

    def update(self):
        self._update_action_button()

    def _update_action_button(self):
        """ Can be overridden """
        if self.is_enabled() and self._action_button:
            self._action_button.set_light(self._action_button.is_pressed())


class OptionsComponent(ControlSurfaceComponent):
    __subject_events__ = ('selected_option',)
    unselected_color = 'Option.Unselected'
    selected_color = 'Option.Selected'
    default_option_names = []
    _selected_option = None

    def __init__(self, num_options = 8, num_labels = 4, *a, **k):
        super(OptionsComponent, self).__init__(*a, **k)
        self._data_sources = [ DisplayDataSource() for _ in xrange(num_options) ]
        self._label_data_sources = [ DisplayDataSource() for _ in xrange(num_labels) ]
        self._select_buttons = None

    @property
    def option_names(self):
        return self.default_option_names

    def _get_selected_option(self):
        return self._selected_option

    def _set_selected_option(self, selected_option):
        raise in_range(selected_option, 0, len(self.option_names)) or selected_option is None or AssertionError
        self._selected_option = selected_option
        self._update_select_buttons()
        self._update_data_sources()

    selected_option = property(_get_selected_option, _set_selected_option)

    def update(self):
        self._update_select_buttons()

    def set_display_line(self, line):
        if line:
            self._update_data_sources()
            line.set_num_segments(len(self._data_sources))
            for segment in xrange(len(self._data_sources)):
                line.segment(segment).set_data_source(self._data_sources[segment])

    def set_label_display_line(self, line):
        if line:
            line.set_num_segments(len(self._label_data_sources))
            for segment in xrange(len(self._label_data_sources)):
                line.segment(segment).set_data_source(self._label_data_sources[segment])

    def _get_labels(self):
        return map(lambda segment: segment.display_string(), self._label_data_sources)

    def _set_labels(self, labels):
        for segment, label in map(None, self._label_data_sources, labels or []):
            segment.set_display_string(label)

    labels = property(_get_labels, _set_labels)

    def set_blank_display_line1(self, line):
        if line:
            line.reset()

    def set_blank_display_line2(self, line):
        if line:
            line.reset()

    def set_select_buttons(self, buttons):
        buttons = buttons or []
        self._select_buttons = buttons
        self._on_select_value.replace_subjects(buttons)
        self._update_select_buttons()

    def set_state_buttons(self, buttons):
        if buttons:
            buttons.reset()

    @subject_slot_group('value')
    def _on_select_value(self, value, sender):
        if value:
            index = list(self._select_buttons).index(sender)
            if in_range(index, 0, len(self.option_names)):
                self.selected_option = index
                self.notify_selected_option(self.selected_option)

    def _update_select_buttons(self):
        if self.is_enabled() and self._select_buttons:
            for index, button in enumerate(self._select_buttons):
                if button:
                    if index == self._selected_option:
                        button.set_light(self.selected_color)
                    elif in_range(index, 0, len(self.option_names)):
                        button.set_light(self.unselected_color)
                    else:
                        button.set_light('DefaultButton.Disabled')

    def _update_data_sources(self):
        for index, (source, name) in enumerate(zip(self._data_sources, self.option_names)):
            source.set_display_string((consts.CHAR_SELECT if index == self._selected_option else '') + name)


class ActionWithOptionsComponent(ActionWithSettingsComponent):

    def __init__(self, num_options = 8, *a, **k):
        super(ActionWithOptionsComponent, self).__init__(*a, **k)
        self._options = self.register_component(OptionsComponent(num_options=num_options))
        self._options.set_enabled(False)

    @property
    def options(self):
        return self._options

    def show_settings(self):
        self._options.set_enabled(True)
        return True

    def hide_settings(self):
        self._options.set_enabled(False)


class ToggleWithOptionsComponent(ActionWithOptionsComponent):
    __subject_events__ = ('toggle_option',)
    _is_active = False
    _just_activated = False

    def _get_is_active(self):
        return self._is_active

    def _set_is_active(self, value):
        if value != self._is_active:
            self._is_active = value
            self._update_action_button()

    is_active = property(_get_is_active, _set_is_active)

    def trigger_action(self):
        if self._is_active:
            self._just_activated = False
        else:
            self._is_active = True
            self._just_activated = True
            self.notify_toggle_option(True)
            self._update_action_button()

    def post_trigger_action(self):
        if not self._just_activated:
            self._is_active = False
            self.notify_toggle_option(False)
            self._update_action_button()

    def _update_action_button(self):
        if self.is_enabled() and self._action_button:
            self._action_button.set_light(self._is_active)