#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/components/scene.py
from __future__ import absolute_import, print_function
from itertools import izip
from ...base import in_range, listens, liveobj_valid, liveobj_changed
from ..compound_component import CompoundComponent
from .clip_slot import ClipSlotComponent, find_nearest_color

class SceneComponent(CompoundComponent):
    """
    Class representing a scene in Live
    """
    clip_slot_component_type = ClipSlotComponent

    def __init__(self, session_ring = None, *a, **k):
        raise session_ring is not None or AssertionError
        raise session_ring.num_tracks >= 0 or AssertionError
        super(SceneComponent, self).__init__(*a, **k)
        self._session_ring = session_ring
        self._scene = None
        self._clip_slots = []
        self._color_palette = None
        self._color_table = None
        for _ in range(session_ring.num_tracks):
            new_slot = self._create_clip_slot()
            self._clip_slots.append(new_slot)
            self.register_components(new_slot)

        self._launch_button = None
        self._triggered_value = 127
        self._scene_value = None
        self._no_scene_value = None
        self._track_offset = 0
        self._select_button = None
        self._delete_button = None
        self.__on_track_list_changed.subject = session_ring

    @listens('tracks')
    def __on_track_list_changed(self):
        self.update()

    def set_scene(self, scene):
        if liveobj_changed(scene, self._scene):
            self._scene = scene
            self.__on_is_triggered_changed.subject = scene
            self.__on_scene_color_changed.subject = scene
            self.update()

    def set_launch_button(self, button):
        if button != self._launch_button:
            self._launch_button = button
            self.__launch_value.subject = button
            self.update()

    def set_select_button(self, button):
        self._select_button = button

    def set_delete_button(self, button):
        self._delete_button = button

    def set_track_offset(self, offset):
        if not offset >= 0:
            raise AssertionError
            self._track_offset = offset != self._track_offset and offset
            self.update()

    def set_triggered_value(self, value):
        self._triggered_value = value

    def set_scene_value(self, value):
        self._scene_value = value

    def set_no_scene_value(self, value):
        self._no_scene_value = value

    def set_color_palette(self, palette):
        self._scene_value = None
        self._color_palette = palette

    def set_color_table(self, table):
        self._scene_value = None
        self._color_table = table

    def clip_slot(self, index):
        return self._clip_slots[index]

    def update(self):
        super(SceneComponent, self).update()
        if self._allow_updates:
            if liveobj_valid(self._scene) and self.is_enabled():
                clip_slots_to_use = self.build_clip_slot_list()
                for slot_wrapper, clip_slot in izip(self._clip_slots, clip_slots_to_use):
                    slot_wrapper.set_clip_slot(clip_slot)

            else:
                for slot in self._clip_slots:
                    slot.set_clip_slot(None)

            self._update_launch_button()
        else:
            self._update_requests += 1

    def _determine_actual_track_offset(self, tracks):
        actual_track_offset = self._track_offset
        if self._track_offset > 0:
            real_offset = 0
            visible_tracks = 0
            while visible_tracks < self._track_offset and len(tracks) > real_offset:
                if tracks[real_offset].is_visible:
                    visible_tracks += 1
                real_offset += 1

            actual_track_offset = real_offset
        return actual_track_offset

    def build_clip_slot_list(self):
        slots_to_use = []
        tracks = self.song.tracks
        track_offset = self._determine_actual_track_offset(tracks)
        clip_slots = self._scene.clip_slots
        for slot in self._clip_slots:
            while len(tracks) > track_offset and not tracks[track_offset].is_visible:
                track_offset += 1

            if len(clip_slots) > track_offset:
                slots_to_use.append(clip_slots[track_offset])
            else:
                slots_to_use.append(None)
            track_offset += 1

        return slots_to_use

    @listens('value')
    def __launch_value(self, value):
        if self.is_enabled():
            if self._select_button and self._select_button.is_pressed() and value:
                self._do_select_scene(self._scene)
            elif liveobj_valid(self._scene):
                if self._delete_button and self._delete_button.is_pressed() and value:
                    self._do_delete_scene(self._scene)
                else:
                    self._do_launch_scene(value)

    def _do_select_scene(self, scene_for_overrides):
        if liveobj_valid(self._scene):
            view = self.song.view
            if view.selected_scene != self._scene:
                view.selected_scene = self._scene

    def _do_delete_scene(self, scene_for_overrides):
        try:
            if self._scene:
                song = self.song
                song.delete_scene(list(song.scenes).index(self._scene))
        except RuntimeError:
            pass

    def _do_launch_scene(self, value):
        launched = False
        if self._launch_button.is_momentary():
            self._scene.set_fire_button_state(value != 0)
            launched = value != 0
        elif value != 0:
            self._scene.fire()
            launched = True
        if launched and self.song.select_on_launch:
            self.song.view.selected_scene = self._scene

    @listens('is_triggered')
    def __on_is_triggered_changed(self):
        raise liveobj_valid(self._scene) or AssertionError
        self._update_launch_button()

    @listens('color')
    def __on_scene_color_changed(self):
        raise liveobj_valid(self._scene) or AssertionError
        self._update_launch_button()

    def _color_value(self, color):
        value = None
        if self._color_palette:
            value = self._color_palette.get(color, None)
        if value is None and self._color_table:
            value = find_nearest_color(self._color_table, color)
        return value

    def _update_launch_button(self):
        if self.is_enabled() and self._launch_button != None:
            value_to_send = self._no_scene_value
            if self._scene:
                if self._scene.is_triggered:
                    value_to_send = self._triggered_value
                elif self._scene_value is not None:
                    value_to_send = self._scene_value
                else:
                    value_to_send = self._color_value(self._scene.color)
            if value_to_send is None:
                self._launch_button.turn_off()
            elif in_range(value_to_send, 0, 128):
                self._launch_button.send_value(value_to_send)
            else:
                self._launch_button.set_light(value_to_send)

    def _create_clip_slot(self):
        return self.clip_slot_component_type()