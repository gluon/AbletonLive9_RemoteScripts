#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Axiom_AIR_25_49_61/SpecialSessionComponent.py
from _Framework.SessionComponent import SessionComponent

class SpecialSessionComponent(SessionComponent):
    """ Session component which allows parallel mixer components
    and has track select buttons """

    def __init__(self, num_tracks, num_scenes):
        self._alt_mixer = None
        self._next_track_button = None
        self._prev_track_button = None
        SessionComponent.__init__(self, num_tracks, num_scenes)

    def disconnect(self):
        SessionComponent.disconnect(self)
        self._alt_mixer = None
        if self._next_track_button != None:
            self._next_track_button.remove_value_listener(self._next_track_value)
            self._next_track_button = None
        if self._prev_track_button != None:
            self._prev_track_button.remove_value_listener(self._prev_track_value)
            self._prev_track_button = None

    def set_alt_mixer(self, alt_mixer):
        self._alt_mixer = alt_mixer
        if self._alt_mixer != None:
            self._alt_mixer.set_track_offset(self.track_offset())

    def set_track_select_buttons(self, next_button, prev_button):
        do_update = False
        if next_button is not self._next_track_button:
            do_update = True
            if self._next_track_button != None:
                self._next_track_button.remove_value_listener(self._next_track_value)
            self._next_track_button = next_button
            if self._next_track_button != None:
                self._next_track_button.add_value_listener(self._next_track_value)
        if prev_button is not self._prev_track_button:
            do_update = True
            if self._prev_track_button != None:
                self._prev_track_button.remove_value_listener(self._prev_track_value)
            self._prev_track_button = prev_button
            if self._prev_track_button != None:
                self._prev_track_button.add_value_listener(self._prev_track_value)
        if do_update:
            self.on_selected_track_changed()

    def tracks_to_use(self):
        list_of_tracks = None
        if self._mixer != None:
            list_of_tracks = self._mixer.tracks_to_use()
        elif self._alt_mixer != None:
            list_of_tracks = self._alt_mixer.tracks_to_use()
        else:
            list_of_tracks = self.song().visible_tracks
        return list_of_tracks

    def _change_offsets(self, track_increment, scene_increment):
        offsets_changed = track_increment != 0 or scene_increment != 0
        if offsets_changed:
            self._track_offset += track_increment
            self._scene_offset += scene_increment
            if self._mixer != None:
                self._mixer.set_track_offset(self.track_offset())
            if self._alt_mixer != None:
                self._alt_mixer.set_track_offset(self.track_offset())
        self._reassign_tracks()
        if offsets_changed:
            self._reassign_scenes()
            self.notify_offset()
            if self.width() > 0 and self.height() > 0:
                self._do_show_highlight()

    def _next_track_value(self, value):
        if self.is_enabled():
            if value is not 0 or not self._next_track_button.is_momentary():
                selected_track = self.song().view.selected_track
                all_tracks = self.song().visible_tracks + self.song().return_tracks + (self.song().master_track,)
                if selected_track != all_tracks[-1]:
                    index = list(all_tracks).index(selected_track)
                    self.song().view.selected_track = all_tracks[index + 1]

    def _prev_track_value(self, value):
        if self.is_enabled():
            if value is not 0 or not self._prev_track_button.is_momentary():
                selected_track = self.song().view.selected_track
                all_tracks = self.song().visible_tracks + self.song().return_tracks + (self.song().master_track,)
                if selected_track != all_tracks[0]:
                    index = list(all_tracks).index(selected_track)
                    self.song().view.selected_track = all_tracks[index - 1]