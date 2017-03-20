# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/select_playing_clip_component.py
# Compiled at: 2016-06-08 13:13:04
"""
Component that automatically selects the playing clip in the selected track.
"""
from __future__ import absolute_import, print_function
from functools import partial
from ableton.v2.base import index_if, nop, listens, task
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.control_surface.mode import AddLayerMode
from .consts import MessageBoxText
from .messenger_mode_component import MessengerModesComponent

class SelectPlayingClipComponent(MessengerModesComponent):
    action_button = ButtonControl(color='DefaultButton.Alert')

    def __init__(self, playing_clip_above_layer=None, playing_clip_below_layer=None, *a, **k):
        super(SelectPlayingClipComponent, self).__init__(*a, **k)
        self._update_mode_task = self._tasks.add(task.sequence(task.delay(1), task.run(self._update_mode)))
        self._update_mode_task.kill()
        self.add_mode('default', None)
        self.add_mode('above', [
         AddLayerMode(self, playing_clip_above_layer)], message=MessageBoxText.PLAYING_CLIP_ABOVE_SELECTED_CLIP)
        self.add_mode('below', [
         AddLayerMode(self, playing_clip_below_layer)], message=MessageBoxText.PLAYING_CLIP_BELOW_SELECTED_CLIP)
        self.selected_mode = 'default'
        self.notify_when_enabled = True
        self._on_detail_clip_changed.subject = self.song.view
        self._on_playing_slot_index_changed.subject = self.song.view.selected_track
        self._notification_reference = partial(nop, None)
        return

    @action_button.pressed
    def action_button(self, button):
        self._go_to_playing_clip()

    @listens('detail_clip')
    def _on_detail_clip_changed(self):
        self._update_mode_task.restart()

    @listens('playing_slot_index')
    def _on_playing_slot_index_changed(self):
        self._update_mode_task.restart()

    def _go_to_playing_clip(self):
        song_view = self.song.view
        playing_clip_slot = self._playing_clip_slot()
        if playing_clip_slot:
            song_view.highlighted_clip_slot = playing_clip_slot
            song_view.detail_clip = playing_clip_slot.clip
            self._hide_notification()

    def _hide_notification(self):
        if self._notification_reference() is not None:
            self._notification_reference().hide()
        return

    def show_notification(self, display_text):
        self._notification_reference = super(SelectPlayingClipComponent, self).show_notification(display_text, blink_text=MessageBoxText.SELECTED_CLIP_BLINK, notification_time=-1)

    def _selected_track_clip_is_playing(self):
        playing_clip_slot = self._playing_clip_slot()
        return not (playing_clip_slot and playing_clip_slot.clip != self.song.view.detail_clip)

    def _playing_clip_slot(self):
        track = self.song.view.selected_track
        try:
            playing_slot_index = track.playing_slot_index
            slot = track.clip_slots[playing_slot_index] if 0 <= playing_slot_index < len(track.clip_slots) else None
            return slot
        except RuntimeError:
            pass

        return

    def _selected_track_clip_is_above_playing_clip(self):
        song_view = self.song.view
        track = song_view.selected_track
        playing_slot_index = track.playing_slot_index
        selected_index = index_if(lambda slot: slot == song_view.highlighted_clip_slot, track.clip_slots)
        return playing_slot_index <= selected_index

    def _update_mode(self):
        if not self._selected_track_clip_is_playing():
            if self._selected_track_clip_is_above_playing_clip():
                self.selected_mode = 'above'
            else:
                self.selected_mode = 'below'
        else:
            self.selected_mode = 'default'
            self._hide_notification()