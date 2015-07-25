#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/DrumGroupComponent.py
from _Framework.Control import control_matrix
from _Framework.DrumGroupComponent import DrumGroupComponent as DrumGroupComponentBase
from _Framework.SubjectSlot import subject_slot
from consts import MessageBoxText
from MatrixMaps import PAD_FEEDBACK_CHANNEL
from MessageBoxComponent import Messenger
from .PadControl import PadControl
from SlideableTouchStripComponent import SlideableTouchStripComponent

class DrumGroupComponent(SlideableTouchStripComponent, DrumGroupComponentBase, Messenger):
    """
    Class representing a drum group pads in a matrix.
    """
    drum_matrix = control_matrix(PadControl)

    def __init__(self, *a, **k):
        super(DrumGroupComponent, self).__init__(touch_slideable=self, translation_channel=PAD_FEEDBACK_CHANNEL, dragging_enabled=True, *a, **k)

    position_count = 32
    page_length = 4
    page_offset = 1

    def set_drum_group_device(self, drum_group_device):
        super(DrumGroupComponent, self).set_drum_group_device(drum_group_device)
        self._on_chains_changed.subject = self._drum_group_device
        self.notify_contents()

    @drum_matrix.pressed
    def drum_matrix(self, pad):
        self._on_matrix_pressed(pad)

    @drum_matrix.released
    def drum_matrix(self, pad):
        self._on_matrix_released(pad)

    def set_select_button(self, button):
        self.select_button.set_control_element(button)

    def set_mute_button(self, button):
        self.mute_button.set_control_element(button)

    def set_solo_button(self, button):
        self.solo_button.set_control_element(button)

    def set_quantize_button(self, button):
        self.quantize_button.set_control_element(button)

    def set_delete_button(self, button):
        self.delete_button.set_control_element(button)

    @subject_slot('chains')
    def _on_chains_changed(self):
        self._update_led_feedback()
        self.notify_contents()

    def delete_pitch(self, drum_pad):
        clip = self.song().view.detail_clip
        if clip:
            loop_length = clip.loop_end - clip.loop_start
            clip.remove_notes(clip.loop_start, drum_pad.note, loop_length, 1)
            self.show_notification(MessageBoxText.DELETE_NOTES % drum_pad.name)

    def _update_control_from_script(self):
        super(DrumGroupComponent, self)._update_control_from_script()
        profile = 'default' if self._takeover_drums or self._selected_pads else 'drums'
        for button in self.drum_matrix:
            button.sensitivity_profile = profile