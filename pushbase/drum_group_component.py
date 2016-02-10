#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/drum_group_component.py
from __future__ import absolute_import, print_function
from functools import partial
from ableton.v2.base import nop, listens, liveobj_valid, listenable_property
from ableton.v2.control_surface.control import control_matrix, ButtonControl
from ableton.v2.control_surface.components import DrumGroupComponent
from .consts import MessageBoxText
from .matrix_maps import PAD_FEEDBACK_CHANNEL
from .message_box_component import Messenger
from .pad_control import PadControl
from .slideable_touch_strip_component import SlideableTouchStripComponent

class DrumPadCopyHandler(object):

    def __init__(self, show_notification = None, notification_formatter = None, *a, **k):
        super(DrumPadCopyHandler, self).__init__(*a, **k)
        self.is_copying = False
        self._source_pad = None
        self._show_notification = show_notification
        self._format_notification_string = notification_formatter if notification_formatter is not None else nop

    def _start_copying(self, source_pad):
        if len(source_pad.chains) > 0:
            self._source_pad = source_pad
            self.is_copying = True
            message = MessageBoxText.COPIED_DRUM_PAD % self._format_notification_string(source_pad.name)
        else:
            message = MessageBoxText.CANNOT_COPY_EMPTY_DRUM_PAD
        return self._show_notification(message)

    def _finish_copying(self, drum_group_device, destination_pad):
        if self._source_pad.note != destination_pad.note:
            destination_pad_name = destination_pad.name
            if len(destination_pad.chains) != 0:
                destination_pad.delete_all_chains()
            drum_group_device.copy_pad(self._source_pad.note, destination_pad.note)
            self.is_copying = False
            message = MessageBoxText.PASTED_DRUM_PAD % (self._format_notification_string(self._source_pad.name), self._format_notification_string(destination_pad_name))
        else:
            message = MessageBoxText.CANNOT_PASTE_TO_SOURCE_DRUM_PAD
        return self._show_notification(message)

    def duplicate_pad(self, drum_group_device, drum_pad):
        if not self.is_copying:
            return self._start_copying(drum_pad)
        return self._finish_copying(drum_group_device, drum_pad)

    def stop_copying(self):
        self.is_copying = False


class DrumGroupComponent(SlideableTouchStripComponent, DrumGroupComponent, Messenger):
    """
    Class representing a drum group pads in a matrix.
    """
    matrix = control_matrix(PadControl)
    duplicate_button = ButtonControl()

    def __init__(self, notification_formatter = None, quantizer = None, *a, **k):
        super(DrumGroupComponent, self).__init__(touch_slideable=self, translation_channel=PAD_FEEDBACK_CHANNEL, dragging_enabled=True, *a, **k)
        self._copy_handler = self._make_copy_handler(notification_formatter)
        self._notification_reference = partial(nop, None)
        self._quantizer = quantizer

    position_count = 32
    page_length = 4
    page_offset = 1

    def update(self):
        super(DrumGroupComponent, self).update()
        if self._copy_handler:
            self._copy_handler.stop_copying()

    def set_drum_group_device(self, drum_group_device):
        super(DrumGroupComponent, self).set_drum_group_device(drum_group_device)
        self._on_chains_changed.subject = self._drum_group_device
        self.notify_contents()

    def quantize_pitch(self, note):
        self._quantizer.quantize_pitch(note)

    def _update_selected_drum_pad(self):
        super(DrumGroupComponent, self)._update_selected_drum_pad()
        self.notify_selected_note()

    def _make_copy_handler(self, notification_formatter):
        return DrumPadCopyHandler(self.show_notification, notification_formatter)

    @matrix.pressed
    def matrix(self, pad):
        self._on_matrix_pressed(pad)

    @matrix.released
    def matrix(self, pad):
        self._on_matrix_released(pad)

    def _on_matrix_pressed(self, pad):
        super(DrumGroupComponent, self)._on_matrix_pressed(pad)
        if self.duplicate_button.is_pressed:
            self._duplicate_pad(pad)

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

    @duplicate_button.pressed
    def duplicate_button(self, button):
        self._set_control_pads_from_script(True)

    @duplicate_button.released
    def duplicate_button(self, button):
        self._set_control_pads_from_script(False)
        if self._copy_handler:
            self._copy_handler.stop_copying()
        if self._notification_reference() is not None:
            self._notification_reference().hide()

    @listens('chains')
    def _on_chains_changed(self):
        self._update_led_feedback()
        self.notify_contents()

    def delete_pitch(self, drum_pad):
        clip = self.song.view.detail_clip
        if clip and any(clip.get_notes(0, drum_pad.note, 999999, 1)):
            clip.remove_notes(0, drum_pad.note, 999999, 1)
            self.show_notification(MessageBoxText.DELETE_NOTES % drum_pad.name)
        else:
            self.show_notification(MessageBoxText.DELETE_DRUM_RACK_PAD % drum_pad.name)
            self.delete_drum_pad_content(drum_pad)

    def delete_drum_pad_content(self, drum_pad):
        drum_pad.delete_all_chains()

    def _duplicate_pad(self, pad):
        if self._copy_handler and self._drum_group_device:
            drum_pad = self._pad_for_button(pad)
            self._notification_reference = self._copy_handler.duplicate_pad(self._drum_group_device, drum_pad)

    def set_matrix(self, matrix):
        super(DrumGroupComponent, self).set_matrix(matrix)
        self._update_sensitivity_profile()

    def _update_control_from_script(self):
        super(DrumGroupComponent, self)._update_control_from_script()
        self._update_sensitivity_profile()

    def _update_sensitivity_profile(self):
        profile = 'default' if self._takeover_pads or self._selected_pads else 'drums'
        for button in self.matrix:
            button.sensitivity_profile = profile

    @listenable_property
    def selected_note(self):
        selected_drum_pad = self._drum_group_device.view.selected_drum_pad if liveobj_valid(self._drum_group_device) else None
        if liveobj_valid(selected_drum_pad):
            return selected_drum_pad.note
        return -1