#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/note_settings_component.py
from __future__ import absolute_import, print_function
import math
from functools import partial
from itertools import imap, chain, izip_longest
from ableton.v2.base import clamp, find_if, forward_property, listens, listens_group, Subject, task
from ableton.v2.control_surface import defaults, Component
from ableton.v2.control_surface.control import ButtonControl, ControlManager, EncoderControl, StepEncoderControl
from ableton.v2.control_surface.elements import DisplayDataSource
from ableton.v2.control_surface.mode import ModesComponent, Mode, AddLayerMode
from .action_with_options_component import OptionsComponent
from .consts import CHAR_ELLIPSIS, GRAPH_VOL

class NoteSettingBase(ControlManager, Subject):
    __events__ = ('setting_changed',)
    attribute_index = -1
    encoder = EncoderControl()

    def __init__(self, grid_resolution = None, *a, **k):
        super(NoteSettingBase, self).__init__(*a, **k)
        self._min_max_value = None
        self._grid_resolution = grid_resolution

    def encoder_value_to_attribute(self, value):
        raise NotImplementedError

    @property
    def step_length(self):
        if self._grid_resolution:
            return self._grid_resolution.step_length
        return 1.0

    def set_min_max(self, min_max_value):
        self._min_max_value = min_max_value

    @encoder.value
    def encoder(self, value, _):
        self._on_encoder_value_changed(value)

    def _on_encoder_value_changed(self, value):
        self.notify_setting_changed(self.attribute_index, self.encoder_value_to_attribute(value))


class NoteSetting(NoteSettingBase):

    def __init__(self, *a, **k):
        super(NoteSetting, self).__init__(*a, **k)
        self.value_source = DisplayDataSource()
        self.label_source = DisplayDataSource()
        self.label_source.set_display_string(self.get_label())

    def get_label(self):
        raise NotImplementedError

    def attribute_min_max_to_string(self, min_value, max_value):
        raise NotImplementedError

    def set_min_max(self, min_max_value):
        self.value_source.set_display_string(self.attribute_min_max_to_string(min_max_value[0], min_max_value[1]) if min_max_value else '-')


RANGE_STRING_FLOAT = '%.1f' + CHAR_ELLIPSIS + '%.1f'
RANGE_STRING_INT = '%d' + CHAR_ELLIPSIS + '%d'

def step_offset_percentage(step_length, value):
    return int(round((value - int(value / step_length) * step_length) / step_length * 100))


def step_offset_min_max_to_string(step_length, min_value, max_value):
    min_value = step_offset_percentage(step_length, min_value)
    max_value = step_offset_percentage(step_length, max_value)
    if min_value == max_value:
        return '%d%%' % min_value
    return (RANGE_STRING_INT + '%%') % (min_value, max_value)


def convert_value_to_graphic(value, value_range):
    value_bar = GRAPH_VOL
    graph_range = float(len(value_bar))
    value = clamp(int(value / value_range * graph_range), 0, len(value_bar) - 1)
    display_string = value_bar[value]
    return display_string


class NoteNudgeSetting(NoteSetting):
    attribute_index = 1

    def get_label(self):
        return 'Nudge'

    def encoder_value_to_attribute(self, value):
        return self.step_length * value

    def attribute_min_max_to_string(self, min_value, max_value):
        return step_offset_min_max_to_string(self.step_length, min_value, max_value)


class NoteLengthCoarseSetting(NoteSetting):
    attribute_index = 2
    encoder = StepEncoderControl()

    def get_label(self):
        return 'Length -'

    def attribute_min_max_to_string(self, min_value, max_value):
        min_value = min_value / self.step_length
        max_value = max_value / self.step_length

        def format_string(value):
            num_non_decimal_figures = int(math.log10(value)) if value > 0 else 0
            return '%%.%dg' % (num_non_decimal_figures + 2,)

        if min_value == max_value:
            return (format_string(min_value) + ' stp') % min_value
        return (format_string(min_value) + CHAR_ELLIPSIS + format_string(max_value)) % (min_value, max_value)

    def encoder_value_to_attribute(self, value):
        return self.step_length * value

    @encoder.value
    def encoder(self, value, _):
        self._on_encoder_value_changed(value)


class NoteLengthFineSetting(NoteSetting):
    attribute_index = 2

    def get_label(self):
        return 'Fine'

    def encoder_value_to_attribute(self, value):
        return self.step_length * value

    def attribute_min_max_to_string(self, min_value, max_value):
        value = step_offset_percentage(self.step_length, min_value)
        return convert_value_to_graphic(value, 100.0)


class NoteVelocitySetting(NoteSetting):
    attribute_index = 3

    def get_label(self):
        return 'Velocity'

    def encoder_value_to_attribute(self, value):
        return value * 128

    def attribute_min_max_to_string(self, min_value, max_value):
        if int(min_value) == int(max_value):
            return str(int(min_value))
        return RANGE_STRING_INT % (min_value, max_value)


class NoteSettingsComponentBase(Component):
    __events__ = ('setting_changed', 'full_velocity')
    full_velocity_button = ButtonControl()

    def __init__(self, grid_resolution = None, *a, **k):
        super(NoteSettingsComponentBase, self).__init__(*a, **k)
        self._settings = []
        self._encoders = []
        self._create_settings(grid_resolution)

    def _create_settings(self, grid_resolution):
        self._add_setting(NoteNudgeSetting(grid_resolution=grid_resolution))
        self._add_setting(NoteLengthCoarseSetting(grid_resolution=grid_resolution))
        self._add_setting(NoteLengthFineSetting(grid_resolution=grid_resolution))
        self._add_setting(NoteVelocitySetting(grid_resolution=grid_resolution))

    def _add_setting(self, setting):
        raise len(self._settings) < 8 or AssertionError('Cannot show more than 8 settings')
        self._settings.append(setting)
        self._update_encoders()
        self.register_disconnectable(setting)
        self.register_slot(setting, self.notify_setting_changed, 'setting_changed')

    def set_info_message(self, message):
        pass

    def set_encoder_controls(self, encoders):
        self._encoders = encoders or []
        self._update_encoders()

    def set_min_max(self, index, min_max_value):
        setting_for_index = [ i for i in self._settings if i.attribute_index == index ]
        for setting in setting_for_index:
            setting.set_min_max(min_max_value)

    @full_velocity_button.pressed
    def full_velocity_button(self, button):
        if self.is_enabled():
            self.notify_full_velocity()

    def _update_encoders(self):
        if self.is_enabled() and self._encoders:
            for encoder, setting in izip_longest(self._encoders[-len(self._settings):], self._settings):
                setting.encoder.set_control_element(encoder)

        else:
            map(lambda setting: setting.encoder.set_control_element(None), self._settings)

    def update(self):
        super(NoteSettingsComponentBase, self).update()
        self._update_encoders()


class NoteSettingsComponent(NoteSettingsComponentBase):

    def __init__(self, *a, **k):
        super(NoteSettingsComponent, self).__init__(*a, **k)
        self._top_data_sources = [ DisplayDataSource() for _ in xrange(8) ]
        self._bottom_data_sources = [ DisplayDataSource() for _ in xrange(8) ]
        self._info_data_source = DisplayDataSource()
        self._create_display_sources()

    def _create_display_sources(self):
        self._top_data_sources = [ DisplayDataSource() for _ in xrange(8 - len(self._settings)) ] + [ s.label_source for s in self._settings ]
        self._bottom_data_sources = [ DisplayDataSource() for _ in xrange(8 - len(self._settings)) ] + [ s.value_source for s in self._settings ]

    def set_top_display_line(self, display):
        if self.is_enabled() and display:
            display.set_data_sources(self._top_data_sources)

    def set_bottom_display_line(self, display):
        if self.is_enabled() and display:
            display.set_data_sources(self._bottom_data_sources)

    def set_info_display_line(self, display):
        if self.is_enabled() and display:
            display.set_data_sources([self._info_data_source])

    def set_clear_display_line(self, display):
        if self.is_enabled() and display:
            display.reset()

    def set_info_message(self, message):
        self._info_data_source.set_display_string(message.rjust(62))


class DetailViewRestorerMode(Mode):
    """
    Restores the detail view if either only clip view or device view is visible.
    Has no effect if the detail view is hidden at the point the mode is entered.
    """

    def __init__(self, application = None, *a, **k):
        super(DetailViewRestorerMode, self).__init__(*a, **k)
        self._app = application
        self._view_to_restore = None

    def enter_mode(self):
        clip_view_visible = self._app.view.is_view_visible('Detail/Clip', False)
        device_chain_visible = self._app.view.is_view_visible('Detail/DeviceChain', False)
        if clip_view_visible != device_chain_visible:
            self._view_to_restore = 'Detail/Clip' if clip_view_visible else 'Detail/DeviceChain'

    def leave_mode(self):
        try:
            if self._view_to_restore:
                self._app.view.show_view(self._view_to_restore)
                self._view_to_restore = None
        except RuntimeError:
            pass


class NoteEditorSettingsComponent(ModesComponent):

    def __init__(self, note_settings_component = None, automation_component = None, initial_encoder_layer = None, encoder_layer = None, *a, **k):
        super(NoteEditorSettingsComponent, self).__init__(*a, **k)
        raise encoder_layer or AssertionError
        self._request_hide = False
        self.settings = self.register_component(note_settings_component)
        self.settings.set_enabled(False)
        self._automation = self.register_component(automation_component)
        self._automation.set_enabled(False)
        self._mode_selector = self.register_component(OptionsComponent(num_options=2, num_labels=0, num_display_segments=8))
        self._mode_selector.set_enabled(False)
        self._on_selected_option.subject = self._mode_selector
        self._update_available_modes()
        self._mode_selector.selected_option = 0
        self._visible_detail_view = 'Detail/DeviceChain'
        self._show_settings_task = self._tasks.add(task.sequence(task.wait(defaults.MOMENTARY_DELAY), task.run(self._show_settings))).kill()
        self._update_infos_task = self._tasks.add(task.run(self._update_note_infos)).kill()
        self._settings_modes = self.register_component(ModesComponent())
        self._settings_modes.set_enabled(False)
        self._settings_modes.add_mode('automation', [self._automation,
         self._mode_selector,
         partial(self._set_envelope_view_visible, True),
         self._show_clip_view])
        self._settings_modes.add_mode('note_settings', [self.settings,
         self._update_note_infos,
         self._mode_selector,
         partial(self._set_envelope_view_visible, False),
         self._show_clip_view])
        self._encoders = None
        self._initial_encoders = None
        self.add_mode('disabled', [])
        self.add_mode('about_to_show', [AddLayerMode(self, initial_encoder_layer), (self._show_settings_task.restart, self._show_settings_task.kill)])
        self.add_mode('enabled', [DetailViewRestorerMode(self.application()),
         AddLayerMode(self, encoder_layer),
         self._update_available_modes,
         self._settings_modes])
        self.selected_mode = 'disabled'
        self._editors = []
        self._on_detail_clip_changed.subject = self.song.view
        self._on_selected_track_changed.subject = self.song.view
        self.__on_full_velocity_changed.subject = self.settings
        self.__on_setting_changed.subject = self.settings

    automation_layer = forward_property('_automation')('layer')
    mode_selector_layer = forward_property('_mode_selector')('layer')
    selected_setting = forward_property('_settings_modes')('selected_mode')

    @property
    def step_settings(self):
        return self._settings_modes

    @property
    def editors(self):
        return self._editors

    def add_editor(self, editor):
        raise editor != None or AssertionError
        self._editors.append(editor)
        self._on_active_steps_changed.add_subject(editor)
        self._on_notes_changed.replace_subjects(self._editors)
        self.__on_modify_all_notes_changed.add_subject(editor)

    def set_display_line(self, line):
        self._mode_selector.set_display_line(line)

    def set_initial_encoders(self, encoders):
        self._initial_encoders = encoders
        self._on_init_encoder_touch.replace_subjects(encoders or [])
        self._on_init_encoder_value.replace_subjects(encoders or [])

    def set_encoders(self, encoders):
        self._encoders = encoders
        self._on_encoder_touch.replace_subjects(encoders or [])
        self._on_encoder_value.replace_subjects(encoders or [])
        self.settings.set_encoder_controls(encoders)
        self._automation.set_parameter_controls(encoders)

    def _get_parameter_provider(self):
        self._automation.parameter_provider

    def _set_parameter_provider(self, value):
        self._automation.parameter_provider = value
        if self.selected_mode != 'disabled':
            self._update_available_modes()

    parameter_provider = property(_get_parameter_provider, _set_parameter_provider)

    @listens('full_velocity')
    def __on_full_velocity_changed(self):
        for editor in self._editors:
            editor.set_full_velocity()

    @listens('setting_changed')
    def __on_setting_changed(self, index, value):
        for editor in self._editors:
            self._modify_note_property_offset(editor, index, value)

    def _modify_note_property_offset(self, editor, index, value):
        if index == 1:
            editor.set_nudge_offset(value)
        elif index == 2:
            editor.set_length_offset(value)
        elif index == 3:
            editor.set_velocity_offset(value)

    def _update_available_modes(self):
        available_modes = ['Notes']
        if self._automation.can_automate_parameters:
            available_modes.append('Automat')
        self._mode_selector.option_names = available_modes

    def _show_clip_view(self):
        try:
            view = self.application().view
            if view.is_view_visible('Detail/DeviceChain', False) and not view.is_view_visible('Detail/Clip', False):
                self.application().view.show_view('Detail/Clip')
        except RuntimeError:
            pass

    def _set_envelope_view_visible(self, visible):
        clip = self.song.view.detail_clip
        if clip:
            if visible:
                clip.view.show_envelope()
            else:
                clip.view.hide_envelope()

    def _try_immediate_show_settings(self):
        if self.selected_mode == 'about_to_show' and any(imap(lambda e: e and e.is_pressed(), self._initial_encoders or [])):
            self._show_settings()

    @listens_group('active_steps')
    def _on_active_steps_changed(self, editor):
        if self.is_enabled():
            all_steps = list(set(chain.from_iterable(imap(lambda e: e.active_steps, self._editors))))
            self._automation.selected_time = all_steps
            self._update_note_infos()
            if len(all_steps) > 0:
                self._request_hide = False
                if self.selected_mode == 'disabled':
                    self.selected_mode = 'about_to_show'
                    self._try_immediate_show_settings()
            else:
                self._request_hide = True
                self._try_hide_settings()

    @listens_group('modify_all_notes')
    def __on_modify_all_notes_changed(self, editor):
        self.selected_mode = 'about_to_show' if editor.modify_all_notes_enabled else 'disabled'

    @listens_group('notes_changed')
    def _on_notes_changed(self, editor):
        self._update_infos_task.restart()

    @listens('detail_clip')
    def _on_detail_clip_changed(self):
        clip = self.song.view.detail_clip if self.is_enabled() else None
        self._automation.clip = clip

    @listens('selected_track')
    def _on_selected_track_changed(self):
        self.selected_mode = 'disabled'

    @listens('selected_option')
    def _on_selected_option(self, option):
        self._update_selected_setting(option)

    @listens_group('touch_value')
    def _on_init_encoder_touch(self, value, encoder):
        self._show_settings()

    @listens_group('value')
    def _on_init_encoder_value(self, value, encoder):
        self._show_settings()

    @listens_group('touch_value')
    def _on_encoder_touch(self, value, encoder):
        if not value:
            self._try_hide_settings()

    @listens_group('value')
    def _on_encoder_value(self, value, encoder):
        self._notify_modification()

    def _notify_modification(self):
        for editor in self._editors:
            editor.notify_modification()

    def _update_note_infos(self):
        if self.settings.is_enabled():

            def min_max((l_min, l_max), (r_min, r_max)):
                return (min(l_min, r_min), max(l_max, r_max))

            all_min_max_attributes = filter(None, imap(lambda e: e.get_min_max_note_values(), self._editors))
            min_max_values = [(99999, -99999)] * 4 if len(all_min_max_attributes) > 0 else None
            for min_max_attribute in all_min_max_attributes:
                for i, attribute in enumerate(min_max_attribute):
                    min_max_values[i] = min_max(min_max_values[i], attribute)

            for i in xrange(4):
                self.settings.set_min_max(i, min_max_values[i] if min_max_values else None)

            edit_all_notes_active = find_if(lambda e: e.modify_all_notes_enabled, self._editors) != None
            self.settings.set_info_message('Tweak to add note' if not edit_all_notes_active and not min_max_values else '')

    def _show_settings(self):
        if self.selected_mode != 'enabled':
            self.selected_mode = 'enabled'
            self._notify_modification()
            self._update_selected_setting(self._mode_selector.selected_option)

    def _update_selected_setting(self, option):
        if option == 0:
            self.selected_setting = 'note_settings'
        elif option == 1:
            self.selected_setting = 'automation'

    def _try_hide_settings(self):
        if self._request_hide and not any(imap(lambda e: e and e.is_pressed(), self._encoders or [])):
            self.selected_mode = 'disabled'
            self._request_hide = False

    def on_enabled_changed(self):
        super(NoteEditorSettingsComponent, self).on_enabled_changed()
        if not self.is_enabled():
            self.selected_mode = 'disabled'

    def update(self):
        super(NoteEditorSettingsComponent, self).update()
        if self.is_enabled():
            self._on_detail_clip_changed()