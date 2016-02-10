#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Serato/SpecialSessionComponent.py
import Live
from _Framework.SessionComponent import SessionComponent
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from _Framework.ClipSlotComponent import ClipSlotComponent
from SpecialSceneComponent import SpecialSceneComponent

class SpecialSessionComponent(SessionComponent):

    def __init__(self, num_tracks, num_scenes):
        self._visible_width = num_tracks
        self._visible_height = num_scenes
        self._synced_session = None
        self._serato_interface = None
        SessionComponent.__init__(self, num_tracks, num_scenes)

    def disconnect(self):
        SessionComponent.disconnect(self)
        if self._synced_session != None:
            self._synced_session.remove_offset_listener(self._on_control_surface_offset_changed)
            self._mixer.set_tracks_to_use_callback(None)
        self._serato_interface = None

    def set_serato_interface(self, serato_interface):
        raise serato_interface != None or AssertionError
        self._serato_interface = serato_interface
        self.on_selected_scene_changed()

    def on_selected_scene_changed(self):
        SessionComponent.on_selected_scene_changed(self)
        if self._serato_interface != None:
            self._serato_interface.PySCA_SetSelectedScene(self._selected_scene_index())

    def set_size(self, width, height):
        if not width in range(self._num_tracks + 1):
            raise AssertionError
            raise height in range(len(self._scenes) + 1) or AssertionError
            self._visible_width = width
            self._visible_height = height
            self._show_highlight = self._show_highlight and False
            self.set_show_highlight(True)

    def move_by(self, track_increment, scene_increment):
        track_offset = self._track_offset + track_increment
        scene_offset = self._scene_offset + scene_increment
        self.set_offsets(max(0, track_offset), max(0, scene_offset))

    def width(self):
        return self._visible_width

    def height(self):
        return self._visible_height

    def sync_to(self, other_session):
        if not isinstance(other_session, (type(None), SessionComponent)):
            raise AssertionError
            if other_session != self._synced_session:
                if self._synced_session != None:
                    self._synced_session.remove_offset_listener(self._on_control_surface_offset_changed)
                    self._mixer.set_tracks_to_use_callback(None)
                self._synced_session = other_session
                self._synced_session != None and self._synced_session.add_offset_listener(self._on_control_surface_offset_changed)
                self._mixer.set_tracks_to_use_callback(self._synced_session.tracks_to_use)
            self._do_show_highlight()

    def set_offsets(self, track_offset, scene_offset):
        if self._synced_session != None:
            self._synced_session.set_offsets(track_offset, scene_offset)
        else:
            SessionComponent.set_offsets(self, track_offset, scene_offset)

    def _on_control_surface_offset_changed(self):
        """
        Updates offsets in serato to be the same as in control surface
        Called whenever control surface offsets are changed.
        """
        SessionComponent.set_offsets(self, self._synced_session.track_offset(), self._synced_session.scene_offset())

    def _create_scene(self):
        return SpecialSceneComponent(self._num_tracks, self.tracks_to_use)

    def _reassign_scenes(self):
        SessionComponent._reassign_scenes(self)
        self.on_selected_scene_changed()

    def _selected_scene_index(self):
        result = -1
        for index in range(len(self._scenes)):
            if self._scenes[index].is_selected():
                result = index + 1
                break

        return result