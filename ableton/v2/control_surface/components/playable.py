#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/components/playable.py
from __future__ import absolute_import, print_function
from .. import Component
from ..control import PlayableControl, ButtonControl, control_matrix

class PlayableComponent(Component):
    __events__ = ('pressed_pads',)
    matrix = control_matrix(PlayableControl)
    select_button = ButtonControl()

    def __init__(self, *a, **k):
        super(PlayableComponent, self).__init__(*a, **k)
        self._takeover_pads = False
        self._selected_pads = []

    def _set_control_pads_from_script(self, takeover_pads):
        """
        If takeover_pads, the matrix buttons will be controlled from
        the script. Otherwise they send midi notes to the track
        associated to the instrument.
        """
        if takeover_pads != self._takeover_pads:
            self._takeover_pads = takeover_pads
            self._update_control_from_script()

    def _update_control_from_script(self):
        takeover_pads = self._takeover_pads or bool(self._selected_pads)
        for button in self.matrix:
            button.set_playable(not takeover_pads)

    def set_matrix(self, matrix):
        self.matrix.set_control_element(matrix)
        self._reset_selected_pads()
        self._update_led_feedback()
        self._update_note_translations()

    @matrix.pressed
    def matrix(self, button):
        self._on_matrix_pressed(button)

    @matrix.released
    def matrix(self, button):
        self._on_matrix_released(button)

    def _on_matrix_pressed(self, button):
        self._selected_pads.append(button)
        if len(self._selected_pads) == 1:
            self._update_control_from_script()
        self.notify_pressed_pads()

    def _on_matrix_released(self, button):
        if button in self._selected_pads:
            self._selected_pads.remove(button)
            if not self._selected_pads:
                self._update_control_from_script()
            self.notify_pressed_pads()
        self._update_led_feedback()

    @select_button.value
    def select_button(self, value, button):
        self._set_control_pads_from_script(bool(value))

    def _reset_selected_pads(self):
        if self._selected_pads:
            self._selected_pads = []
            self._update_control_from_script()
            self.notify_pressed_pads()

    def _update_led_feedback(self):
        for button in self.matrix:
            self._update_button_color(button)

    def _update_button_color(self, button):
        button.color = 'DefaultButton.Off'

    def _button_should_be_enabled(self, button):
        identifier, _ = self._note_translation_for_button(button)
        return identifier < 128

    def _note_translation_for_button(self, button):
        return (button.identifier, button.channel)

    def _update_note_translations(self):
        for button in self.matrix:
            if self._button_should_be_enabled(button):
                self._set_button_control_properties(button)
                button.enabled = True
            else:
                button.enabled = False

    def _set_button_control_properties(self, button):
        identifier, channel = self._note_translation_for_button(button)
        button.identifier = identifier
        button.channel = channel

    def update(self):
        super(PlayableComponent, self).update()
        if self.is_enabled():
            self._set_control_pads_from_script(False)

    @property
    def width(self):
        if self.matrix.width:
            return self.matrix.width
        return 4

    @property
    def height(self):
        if self.matrix.height:
            return self.matrix.height
        return 4

    @property
    def pressed_pads(self):
        return self._selected_pads