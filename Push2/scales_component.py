#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/scales_component.py
from functools import partial
from ableton.v2.base import clamp, listens, listenable_property
from ableton.v2.control_surface import Component
from ableton.v2.control_surface.control import ButtonControl, RadioButtonControl, StepEncoderControl, ToggleButtonControl, control_list
from pushbase.melodic_pattern import ROOT_NOTES, SCALES, NOTE_NAMES

class ScalesComponent(Component):
    __events__ = ('close',)
    root_note_buttons = control_list(RadioButtonControl, control_count=len(ROOT_NOTES), checked_color='Scales.OptionOn', unchecked_color='Scales.OptionOff')
    in_key_toggle_button = ToggleButtonControl(toggled_color='Scales.OptionOn', untoggled_color='Scales.OptionOn')
    fixed_toggle_button = ToggleButtonControl(toggled_color='Scales.OptionOn', untoggled_color='Scales.OptionOff')
    scale_encoders = control_list(StepEncoderControl)
    close_button = ButtonControl(color='Scales.Close')

    def __init__(self, note_layout = None, *a, **k):
        raise note_layout is not None or AssertionError
        super(ScalesComponent, self).__init__(*a, **k)
        self._note_layout = note_layout
        self._scale_list = list(SCALES)
        self._scale_name_list = map(lambda m: m.name, self._scale_list)
        self._selected_scale_index = -1
        self._selected_root_note_index = -1
        self.in_key_toggle_button.connect_property(note_layout, 'is_in_key')
        self.fixed_toggle_button.connect_property(note_layout, 'is_fixed')
        self.__on_root_note_changed.subject = self._note_layout
        self.__on_scale_changed.subject = self._note_layout
        self.__on_root_note_changed(note_layout.root_note)
        self.__on_scale_changed(note_layout.scale)

    @root_note_buttons.pressed
    def root_note_buttons(self, button):
        self._note_layout.root_note = ROOT_NOTES[button.index]

    @listens('root_note')
    def __on_root_note_changed(self, root_note):
        self._selected_root_note_index = list(ROOT_NOTES).index(root_note)
        self.root_note_buttons.checked_index = self._selected_root_note_index
        self.notify_selected_root_note_index()

    @property
    def root_note_names(self):
        return [ NOTE_NAMES[note] for note in ROOT_NOTES ]

    @listenable_property
    def selected_root_note_index(self):
        return self._selected_root_note_index

    @scale_encoders.value
    def scale_encoders(self, value, encoder):
        index = clamp(self._selected_scale_index + value, 0, len(self._scale_list) - 1)
        self._note_layout.scale = self._scale_list[index]

    @property
    def scale_names(self):
        return self._scale_name_list

    @listenable_property
    def selected_scale_index(self):
        return self._selected_scale_index

    @listens('scale')
    def __on_scale_changed(self, scale):
        index = self._scale_list.index(scale) if scale in self._scale_list else -1
        if index != self._selected_scale_index:
            self._selected_scale_index = index
            self.notify_selected_scale_index()

    @close_button.pressed
    def close_button(self, button):
        self.notify_close()

    @property
    def note_layout(self):
        return self._note_layout


class ScalesEnabler(Component):
    toggle_button = ButtonControl(color='DefaultButton.On')

    def __init__(self, enter_dialog_mode = None, exit_dialog_mode = None, *a, **k):
        raise enter_dialog_mode is not None or AssertionError
        raise exit_dialog_mode is not None or AssertionError
        super(ScalesEnabler, self).__init__(*a, **k)
        self._enable_dialog_mode = partial(enter_dialog_mode, 'scales')
        self._exit_dialog_mode = partial(exit_dialog_mode, 'scales')

    @toggle_button.pressed
    def toggle_button(self, button):
        self._enable_dialog_mode()

    def on_enabled_changed(self):
        super(ScalesEnabler, self).on_enabled_changed()
        if not self.is_enabled():
            self._exit_dialog_mode()