#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/pushbase/session_recording_component.py
import Live
from ableton.v2.base import listens
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.control_surface.components import SessionRecordingComponent
from .consts import MessageBoxText
from .message_box_component import Messenger
Quantization = Live.Song.Quantization

def track_can_overdub(track):
    return not track.has_audio_input


class FixedLengthSessionRecordingComponent(SessionRecordingComponent, Messenger):
    foot_switch_button = ButtonControl()

    def __init__(self, fixed_length_setting = None, *a, **k):
        raise fixed_length_setting is not None or AssertionError
        super(FixedLengthSessionRecordingComponent, self).__init__(*a, **k)
        self._fixed_length_setting = fixed_length_setting
        self.__on_setting_selected_index_changes.subject = self._fixed_length_setting

    @foot_switch_button.pressed
    def foot_switch_button(self, button):
        self._trigger_recording()

    def _start_recording(self):
        song = self.song
        song.overdub = True
        selected_scene = song.view.selected_scene
        scene_index = list(song.scenes).index(selected_scene)
        track = self.song.view.selected_track
        if track.can_be_armed and (track.arm or track.implicit_arm):
            self._record_in_slot(track, track.clip_slots[scene_index])
            self._ensure_slot_is_visible(track, scene_index)
        if not song.is_playing:
            song.is_playing = True

    def _record_in_slot(self, track, clip_slot):
        if self._fixed_length_setting.enabled and not clip_slot.has_clip:
            length, quant = self._fixed_length_setting.get_selected_length(self.song)
            if track_can_overdub(track):
                self._clip_creator.create(clip_slot, length)
            else:
                clip_slot.fire(record_length=length, launch_quantization=quant)
        elif not clip_slot.is_playing:
            if clip_slot.has_clip:
                clip_slot.fire(force_legato=True, launch_quantization=Quantization.q_no_q)
            else:
                clip_slot.fire()

    def _ensure_slot_is_visible(self, track, scene_index):
        song = self.song
        if song.view.selected_track == track:
            song.view.selected_scene = song.scenes[scene_index]
        self._view_selected_clip_detail()

    @listens('selected_index')
    def __on_setting_selected_index_changes(self, _):
        length, _ = self._fixed_length_setting.get_selected_length(self.song)
        self._clip_creator.fixed_length = length

    def _handle_limitation_error_on_scene_creation(self):
        self.expect_dialog(MessageBoxText.SCENE_LIMIT_REACHED)