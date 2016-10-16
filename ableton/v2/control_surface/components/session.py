#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/components/session.py
from __future__ import absolute_import, print_function
import Live
from itertools import count
from ...base import in_range, product, listens, listens_group
from ..compound_component import CompoundComponent
from .scene import SceneComponent

class SessionComponent(CompoundComponent):
    """
    Class encompassing several scenes to cover a defined section of
    Live's session. It handles starting and playing clips.
    """
    _session_component_ends_initialisation = True
    scene_component_type = SceneComponent

    def __init__(self, session_ring = None, auto_name = False, enable_skinning = False, *a, **k):
        super(SessionComponent, self).__init__(*a, **k)
        if not session_ring is not None:
            raise AssertionError
            self._session_ring = session_ring
            self.__on_offsets_changed.subject = self._session_ring
            self._stop_all_button = None
            self._stop_track_clip_buttons = None
            self._stop_clip_triggered_value = 127
            self._stop_clip_value = None
            self._track_slots = self.register_slot_manager()
            self._selected_scene = self.register_component(self._create_scene())
            self._scenes = self.register_components(*[ self._create_scene() for _ in xrange(self._session_ring.num_scenes) ])
            if self._session_component_ends_initialisation:
                self._end_initialisation()
            if auto_name:
                self._auto_name()
            enable_skinning and self._enable_skinning()
        self.__on_track_list_changed.subject = self.song
        self.__on_scene_list_changed.subject = self.song
        self.__on_selected_scene_changed.subject = self.song.view

    def _end_initialisation(self):
        self.__on_selected_scene_changed()
        self._reassign_scenes_and_tracks()

    def _create_scene(self):
        return self.scene_component_type(session_ring=self._session_ring)

    def scene(self, index):
        raise in_range(index, 0, len(self._scenes)) or AssertionError
        return self._scenes[index]

    def selected_scene(self):
        return self._selected_scene

    def _enable_skinning(self):
        self.set_stop_clip_triggered_value('Session.StopClipTriggered')
        self.set_stop_clip_value('Session.StopClip')
        for scene_index in xrange(self._session_ring.num_scenes):
            scene = self.scene(scene_index)
            scene.set_scene_value('Session.Scene')
            scene.set_no_scene_value('Session.NoScene')
            scene.set_triggered_value('Session.SceneTriggered')
            for track_index in xrange(self._session_ring.num_tracks):
                clip_slot = scene.clip_slot(track_index)
                clip_slot.set_triggered_to_play_value('Session.ClipTriggeredPlay')
                clip_slot.set_triggered_to_record_value('Session.ClipTriggeredRecord')
                clip_slot.set_record_button_value('Session.RecordButton')
                clip_slot.set_stopped_value('Session.ClipStopped')
                clip_slot.set_started_value('Session.ClipStarted')
                clip_slot.set_recording_value('Session.ClipRecording')

    def _auto_name(self):
        self.name = 'Session_Control'
        self.selected_scene().name = 'Selected_Scene'
        for track_index in xrange(self._session_ring.num_tracks):
            clip_slot = self.selected_scene().clip_slot(track_index)
            clip_slot.name = 'Selected_Scene_Clip_Slot_%d' % track_index

        for scene_index in xrange(self._session_ring.num_scenes):
            scene = self.scene(scene_index)
            scene.name = 'Scene_%d' % scene_index
            for track_index in xrange(self._session_ring.num_tracks):
                clip_slot = scene.clip_slot(track_index)
                clip_slot.name = '%d_Clip_Slot_%d' % (track_index, scene_index)

    def set_stop_all_clips_button(self, button):
        self._stop_all_button = button
        self.__on_stop_all_value.subject = button
        self._update_stop_all_clips_button()

    def set_stop_track_clip_buttons(self, buttons):
        self._stop_track_clip_buttons = buttons
        self.__on_stop_track_value.replace_subjects(buttons or [])
        self._update_stop_track_clip_buttons()

    def set_stop_clip_triggered_value(self, value):
        self._stop_clip_triggered_value = value

    def set_stop_clip_value(self, value):
        self._stop_clip_value = value

    def set_clip_launch_buttons(self, buttons):
        raise not buttons or buttons.width() == self._session_ring.num_tracks and buttons.height() == self._session_ring.num_scenes or AssertionError
        if buttons:
            for button, (x, y) in buttons.iterbuttons():
                scene = self.scene(y)
                slot = scene.clip_slot(x)
                slot.set_launch_button(button)

        else:
            for x, y in product(xrange(self._session_ring.num_tracks), xrange(self._session_ring.num_scenes)):
                scene = self.scene(y)
                slot = scene.clip_slot(x)
                slot.set_launch_button(None)

    def set_scene_launch_buttons(self, buttons):
        raise not buttons or buttons.width() == self._session_ring.num_scenes and buttons.height() == 1 or AssertionError
        if buttons:
            for button, (x, _) in buttons.iterbuttons():
                scene = self.scene(x)
                scene.set_launch_button(button)

        else:
            for x in xrange(self._session_ring.num_scenes):
                scene = self.scene(x)
                scene.set_launch_button(None)

    @listens('offset')
    def __on_offsets_changed(self, *a):
        if self.is_enabled():
            self._reassign_scenes_and_tracks()

    def _reassign_scenes_and_tracks(self):
        self._reassign_tracks()
        self._reassign_scenes()

    def set_rgb_mode(self, color_palette, color_table, clip_slots_only = False):
        """
        Put the session into rgb mode by providing a color table and a color palette.
        color_palette is a dictionary, mapping custom Live colors to MIDI ids. This can be
        used to map a color directly to a CC value.
        The color_table is a list of tuples, where the first element is a MIDI CC and the
        second is the RGB color is represents. The table will be used to find the nearest
        matching color for a custom color. The table is used if there is no entry in the
        palette.
        """
        for y in xrange(self._session_ring.num_scenes):
            scene = self.scene(y)
            if not clip_slots_only:
                scene.set_color_palette(color_palette)
                scene.set_color_table(color_table)
            for x in xrange(self._session_ring.num_tracks):
                slot = scene.clip_slot(x)
                slot.set_clip_palette(color_palette)
                slot.set_clip_rgb_table(color_table)

    def update(self):
        super(SessionComponent, self).update()
        if self._allow_updates:
            if self.is_enabled():
                self._update_stop_track_clip_buttons()
                self._update_stop_all_clips_button()
                self._reassign_scenes_and_tracks()
        else:
            self._update_requests += 1

    def _update_stop_track_clip_buttons(self):
        if self.is_enabled():
            for index in xrange(self._session_ring.num_tracks):
                self._update_stop_clips_led(index)

    @listens('scenes')
    def __on_scene_list_changed(self):
        self._reassign_scenes()

    @listens('visible_tracks')
    def __on_track_list_changed(self):
        self._reassign_tracks()

    @listens('selected_scene')
    def __on_selected_scene_changed(self):
        if self._selected_scene != None:
            self._selected_scene.set_scene(self.song.view.selected_scene)

    def _update_stop_all_clips_button(self):
        if self.is_enabled():
            button = self._stop_all_button
            if button:
                button.set_light(button.is_pressed())

    def _reassign_scenes(self):
        scenes = self.song.scenes
        for index, scene in enumerate(self._scenes):
            scene_index = self._session_ring.scene_offset + index
            if len(scenes) > scene_index:
                scene.set_scene(scenes[scene_index])
                scene.set_track_offset(self._session_ring.track_offset)
            else:
                self._scenes[index].set_scene(None)

        if self._selected_scene != None:
            self._selected_scene.set_track_offset(self._session_ring.track_offset)

    def _reassign_tracks(self):
        tracks_to_use = self._session_ring.tracks_to_use()
        tracks = map(lambda t: (t if isinstance(t, Live.Track.Track) else None), tracks_to_use)
        self.__on_fired_slot_index_changed.replace_subjects(tracks, count())
        self.__on_playing_slot_index_changed.replace_subjects(tracks, count())
        self._update_stop_all_clips_button()
        self._update_stop_track_clip_buttons()

    @listens('value')
    def __on_stop_all_value(self, value):
        self._stop_all_value(value)

    def _stop_all_value(self, value):
        if self.is_enabled():
            if value is not 0 or not self._stop_all_button.is_momentary():
                self.song.stop_all_clips()
            self._update_stop_all_clips_button()

    @listens_group('value')
    def __on_stop_track_value(self, value, button):
        if self.is_enabled():
            if value is not 0 or not button.is_momentary():
                tracks = self._session_ring.tracks_to_use()
                track_index = list(self._stop_track_clip_buttons).index(button) + self._session_ring.track_offset
                if in_range(track_index, 0, len(tracks)) and tracks[track_index] in self.song.tracks:
                    tracks[track_index].stop_all_clips()

    @listens_group('fired_slot_index')
    def __on_fired_slot_index_changed(self, track_index):
        button_index = track_index - self._session_ring.track_offset
        self._update_stop_clips_led(button_index)

    @listens_group('playing_slot_index')
    def __on_playing_slot_index_changed(self, track_index):
        button_index = track_index - self._session_ring.track_offset
        self._update_stop_clips_led(button_index)

    def _update_stop_clips_led(self, index):
        tracks_to_use = self._session_ring.tracks_to_use()
        track_index = index + self._session_ring.track_offset
        if self.is_enabled() and self._stop_track_clip_buttons != None and index < len(self._stop_track_clip_buttons):
            button = self._stop_track_clip_buttons[index]
            if button != None:
                value_to_send = None
                if track_index < len(tracks_to_use) and tracks_to_use[track_index].clip_slots:
                    track = tracks_to_use[track_index]
                    if track.fired_slot_index == -2:
                        value_to_send = self._stop_clip_triggered_value
                    elif track.playing_slot_index >= 0:
                        value_to_send = self._stop_clip_value
                if value_to_send == None:
                    button.turn_off()
                elif in_range(value_to_send, 0, 128):
                    button.send_value(value_to_send)
                else:
                    button.set_light(value_to_send)