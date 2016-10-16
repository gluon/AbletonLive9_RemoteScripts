#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/SelectPlayingClipComponent.py
"""
Component that automatically selects the playing clip in the selected track.
"""
from _Framework.Control import ButtonControl
from _Framework.ModesComponent import ModesComponent, AddLayerMode
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import forward_property, index_if, partial
from _Framework import Task
from MessageBoxComponent import NotificationComponent
from consts import MessageBoxText

class SelectPlayingClipComponent(ModesComponent):
    action_button = ButtonControl(color='DefaultButton.Alert')

    def __init__(self, playing_clip_above_layer = None, playing_clip_below_layer = None, *a, **k):
        super(SelectPlayingClipComponent, self).__init__(*a, **k)
        self._update_mode_task = self._tasks.add(Task.sequence(Task.delay(1), Task.run(self._update_mode)))
        self._update_mode_task.kill()
        self._notification = self.register_component(NotificationComponent(notification_time=-1, is_enabled=False))
        self.add_mode('default', None)
        self.add_mode('above', [AddLayerMode(self, playing_clip_above_layer), self._notification, partial(self._show_notification, MessageBoxText.PLAYING_CLIP_ABOVE_SELECTED_CLIP)])
        self.add_mode('below', [AddLayerMode(self, playing_clip_below_layer), self._notification, partial(self._show_notification, MessageBoxText.PLAYING_CLIP_BELOW_SELECTED_CLIP)])
        self.selected_mode = 'default'
        self._on_detail_clip_changed.subject = self.song().view
        self._on_playing_slot_index_changed.subject = self.song().view.selected_track

    notification_layer = forward_property('_notification')('message_box_layer')

    @action_button.pressed
    def action_button(self, button):
        self._go_to_playing_clip()

    @subject_slot('detail_clip')
    def _on_detail_clip_changed(self):
        self._update_mode_task.restart()

    @subject_slot('playing_slot_index')
    def _on_playing_slot_index_changed(self):
        self._update_mode_task.restart()

    def _go_to_playing_clip(self):
        song_view = self.song().view
        playing_clip_slot = self._playing_clip_slot()
        if playing_clip_slot:
            song_view.highlighted_clip_slot = playing_clip_slot
            song_view.detail_clip = playing_clip_slot.clip

    def _show_notification(self, display_text):
        self._notification.show_notification(display_text, blink_text=MessageBoxText.SELECTED_CLIP_BLINK)

    def _selected_track_clip_is_playing(self):
        playing_clip_slot = self._playing_clip_slot()
        return playing_clip_slot and not playing_clip_slot.clip != self.song().view.detail_clip

    def _playing_clip_slot(self):
        track = self.song().view.selected_track
        try:
            playing_slot_index = track.playing_slot_index
            slot = track.clip_slots[playing_slot_index] if 0 <= playing_slot_index < len(track.clip_slots) else None
            return slot
        except RuntimeError:
            pass

    def _selected_track_clip_is_above_playing_clip(self):
        song_view = self.song().view
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