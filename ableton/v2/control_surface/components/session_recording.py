#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/components/session_recording.py
from __future__ import absolute_import, print_function
import Live
from ...base import find_if, listens, liveobj_valid
from ..compound_component import CompoundComponent
from ..control import ToggleButtonControl, ButtonControl

def track_fired_slot(track):
    index = track.fired_slot_index
    if index >= 0:
        return track.clip_slots[index]


def track_playing_slot(track):
    index = track.playing_slot_index
    if index >= 0:
        return track.clip_slots[index]


def track_is_recording(track):
    playing_slot = track_playing_slot(track)
    return playing_slot and playing_slot.is_recording


def track_will_record(track):
    fired_slot = track_fired_slot(track)
    return fired_slot and fired_slot.will_record_on_start


class SessionRecordingComponent(CompoundComponent):
    """
    Orchestrates the session recording (clip slot based) workflow.
    """
    _automation_toggle = ToggleButtonControl(toggled_color='Automation.On', untoggled_color='Automation.Off')
    _re_enable_automation = ButtonControl(color='Automation.On')
    _delete_automation = ButtonControl(color='Automation.Off')
    _record_button = ButtonControl()

    def __init__(self, clip_creator = None, view_controller = None, *a, **k):
        super(SessionRecordingComponent, self).__init__(*a, **k)
        raise clip_creator or AssertionError
        raise view_controller or AssertionError
        self._target_slots = []
        self._clip_creator = clip_creator
        self._view_controller = view_controller
        self._new_button = None
        self._scene_list_new_button = None
        self._length_press_state = None
        self._new_scene_button = None
        song = self.song
        self.__on_tracks_changed_in_live.subject = song
        self.__on_is_playing_changed_in_live.subject = song
        self._track_subject_slots = self.register_slot_manager()
        self._reconnect_track_listeners()
        self.register_slot(song, self.update, 'overdub')
        self.register_slot(song, self.update, 'session_record_status')
        self.register_slot(song, self._update_record_button, 'session_record')
        self.register_slot(song.view, self.update, 'selected_track')
        self.register_slot(song.view, self.update, 'selected_scene')
        self.register_slot(song.view, self.update, 'detail_clip')
        self._clip_creator.fixed_length = 8.0
        self.__on_session_automation_record_changed.subject = song
        self.__on_session_automation_record_changed()
        self.__on_re_enable_automation_enabled_changed.subject = song
        self.__on_re_enable_automation_enabled_changed()

    def set_record_button(self, button):
        self._record_button.set_control_element(button)
        self._update_record_button()

    def set_automation_button(self, button):
        self._automation_toggle.set_control_element(button)

    def set_re_enable_automation_button(self, button):
        self._re_enable_automation.set_control_element(button)

    def set_delete_automation_button(self, button):
        self._update_delete_automation_button_color()
        self._delete_automation.set_control_element(button)

    def set_scene_list_new_button(self, button):
        self._scene_list_new_button = button
        self.__on_scene_list_new_button_value.subject = button
        self._update_scene_list_new_button()

    def set_new_button(self, button):
        self._new_button = button
        self.__on_new_button_value.subject = button
        self._update_new_button()

    def set_new_scene_button(self, button):
        self._new_scene_button = button
        self.__on_new_scene_button_value.subject = button
        self._update_new_scene_button()

    def deactivate_recording(self):
        self._stop_recording()

    @listens('re_enable_automation_enabled')
    def __on_re_enable_automation_enabled_changed(self):
        self._re_enable_automation.enabled = self.song.re_enable_automation_enabled

    @_re_enable_automation.released
    def _on_re_enable_automation_released(self, button):
        if self.song.re_enable_automation_enabled:
            self.song.re_enable_automation()

    @listens('session_automation_record')
    def __on_session_automation_record_changed(self):
        self._automation_toggle.is_toggled = self.song.session_automation_record

    @_automation_toggle.toggled
    def _on_automation_toggled(self, is_toggled, button):
        self.song.session_automation_record = is_toggled

    @_delete_automation.released
    def _on_delete_button_released(self, button):
        self._delete_automation_value()

    def update(self):
        super(SessionRecordingComponent, self).update()
        if self.is_enabled():
            self._on_playing_clip_has_envelopes_changed.subject = self._get_playing_clip()
            self._update_record_button()
            self._update_new_button()
            self._update_scene_list_new_button()
            self._update_new_scene_button()

    def _update_scene_list_new_button(self):
        self._update_generic_new_button(self._scene_list_new_button)

    def _update_new_button(self):
        self._update_generic_new_button(self._new_button)

    def _update_generic_new_button(self, new_button):
        if new_button and self.is_enabled():
            song = self.song
            selected_track = song.view.selected_track
            clip_slot = song.view.highlighted_clip_slot
            can_new = liveobj_valid(clip_slot) and clip_slot.clip or selected_track.can_be_armed and selected_track.playing_slot_index >= 0
            new_button.set_light(can_new or 'DefaultButton.Disabled')

    def _update_new_scene_button(self):
        if self._new_scene_button and self.is_enabled():
            song = self.song
            track_is_playing = find_if(lambda x: x.playing_slot_index >= 0, song.tracks)
            can_new = not song.view.selected_scene.is_empty or track_is_playing
            self._new_scene_button.set_light(can_new or 'DefaultButton.Disabled')

    def _update_record_button(self):
        if self.is_enabled():
            song = self.song
            status = song.session_record_status
            if status == Live.Song.SessionRecordStatus.transition:
                self._record_button.color = 'Recording.Transition'
            elif status == Live.Song.SessionRecordStatus.on or song.session_record:
                self._record_button.color = 'Recording.On'
            else:
                self._record_button.color = 'Recording.Off'

    @listens('has_envelopes')
    def _on_playing_clip_has_envelopes_changed(self):
        self._update_delete_automation_button_color()

    def _update_delete_automation_button_color(self):
        if self._on_playing_clip_has_envelopes_changed.subject:
            self._delete_automation.color = 'Automation.On' if self._on_playing_clip_has_envelopes_changed.subject.has_envelopes else 'Automation.Off'

    def _delete_automation_value(self):
        if self.is_enabled():
            clip = self._get_playing_clip()
            selected_track = self.song.view.selected_track
            track_frozen = selected_track and selected_track.is_frozen
            if clip and not track_frozen:
                clip.clear_all_envelopes()
            self._update_delete_automation_button_color()

    def _get_playing_clip(self):
        playing_clip = None
        selected_track = self.song.view.selected_track
        try:
            playing_slot_index = selected_track.playing_slot_index
            if playing_slot_index >= 0:
                playing_clip = selected_track.clip_slots[playing_slot_index].clip
        except RuntimeError:
            pass

        return playing_clip

    def _handle_limitation_error_on_scene_creation(self):
        pass

    @listens('tracks')
    def __on_tracks_changed_in_live(self):
        self._reconnect_track_listeners()

    @listens('is_playing')
    def __on_is_playing_changed_in_live(self):
        if self.is_enabled():
            self._update_record_button()

    @_record_button.pressed
    def _record_button(self, button):
        self._on_record_button_pressed()

    def _on_record_button_pressed(self):
        self._trigger_recording()

    def _trigger_recording(self):
        if self.is_enabled():
            if not self._stop_recording():
                self._start_recording()

    @_record_button.released
    def _record_button(self, button):
        self._on_record_button_released()

    def _on_record_button_released(self):
        pass

    @listens('value')
    def __on_new_scene_button_value(self, value):
        if self.is_enabled() and value and self._prepare_new_action():
            song = self.song
            selected_scene_index = list(song.scenes).index(song.view.selected_scene)
            try:
                self._create_silent_scene(selected_scene_index)
            except Live.Base.LimitationError:
                self._handle_limitation_error_on_scene_creation()

    @listens('value')
    def __on_scene_list_new_button_value(self, value):
        if self.is_enabled() and value and self._prepare_new_action():
            song = self.song
            view = song.view
            try:
                if liveobj_valid(view.highlighted_clip_slot.clip):
                    song.capture_and_insert_scene(Live.Song.CaptureMode.all_except_selected)
                else:
                    view.selected_track.stop_all_clips(False)
            except Live.Base.LimitationError:
                self._handle_limitation_error_on_scene_creation()

            self._view_selected_clip_detail()

    @listens('value')
    def __on_new_button_value(self, value):
        if self.is_enabled() and value and self._prepare_new_action():
            song = self.song
            view = song.view
            try:
                selected_track = view.selected_track
                selected_scene_index = list(song.scenes).index(view.selected_scene)
                selected_track.stop_all_clips(False)
                self._jump_to_next_slot(selected_track, selected_scene_index)
            except Live.Base.LimitationError:
                self._handle_limitation_error_on_scene_creation()

            self._view_selected_clip_detail()

    def _prepare_new_action(self):
        song = self.song
        selected_track = song.view.selected_track
        if selected_track.can_be_armed:
            song.overdub = False
            return True

    def _has_clip(self, scene_or_track):
        return find_if(lambda x: liveobj_valid(x.clip), scene_or_track.clip_slots) != None

    def _create_silent_scene(self, scene_index):
        song = self.song
        song.stop_all_clips(False)
        selected_scene = song.view.selected_scene
        if not selected_scene.is_empty:
            new_scene_index = list(song.scenes).index(selected_scene) + 1
            song.view.selected_scene = song.create_scene(new_scene_index)

    def _jump_to_next_slot(self, track, start_index):
        song = self.song
        new_scene_index = self._next_empty_slot(track, start_index)
        song.view.selected_scene = song.scenes[new_scene_index]

    def _stop_recording(self):
        """ Retriggers all new recordings and returns true if there
        was any recording at all """
        song = self.song
        status = song.session_record_status
        was_recording = status != Live.Song.SessionRecordStatus.off or song.session_record
        if was_recording:
            song.session_record = False
        return was_recording

    def _start_recording(self):
        song = self.song
        song.session_record = True

    def _next_empty_slot(self, track, scene_index):
        """ Finds an empty slot in the track after the given position,
        creating new scenes if needed, and returns the found scene
        index """
        song = self.song
        scene_count = len(song.scenes)
        while track.clip_slots[scene_index].has_clip:
            scene_index += 1
            if scene_index == scene_count:
                song.create_scene(scene_count)

        return scene_index

    def _view_selected_clip_detail(self):
        view = self.song.view
        if view.highlighted_clip_slot.clip:
            view.detail_clip = view.highlighted_clip_slot.clip
        self._view_controller.show_view('Detail/Clip')

    def _reconnect_track_listeners(self):
        manager = self._track_subject_slots
        manager.disconnect()
        for track in self.song.tracks:
            if track.can_be_armed:
                manager.register_slot(track, self.update, 'arm')
                manager.register_slot(track, self.update, 'playing_slot_index')
                manager.register_slot(track, self.update, 'fired_slot_index')

    @property
    def scene_list_mode(self):
        return self._scene_list_mode

    @scene_list_mode.setter
    def scene_list_mode(self, scene_list_mode):
        self._scene_list_mode = scene_list_mode
        self._update_new_button()