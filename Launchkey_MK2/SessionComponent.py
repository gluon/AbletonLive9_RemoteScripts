#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchkey_MK2/SessionComponent.py
from _Framework.Util import index_if
from _Framework.SessionComponent import SessionComponent as SessionComponentBase

class SessionComponent(SessionComponentBase):
    _session_component_ends_initialisation = False

    def __init__(self, *a, **k):
        super(SessionComponent, self).__init__(*a, **k)
        self.set_offsets(0, 0)
        self.on_selected_scene_changed()
        self.on_selected_track_changed()

    def on_selected_track_changed(self):
        all_tracks = self.tracks_to_use()
        selected_track = self.song().view.selected_track
        num_strips = self.width()
        if selected_track in all_tracks:
            track_index = list(all_tracks).index(selected_track)
            new_offset = track_index - track_index % num_strips
            self.set_offsets(new_offset, self.scene_offset())

    def on_selected_scene_changed(self):
        super(SessionComponent, self).on_selected_scene_changed()
        all_scenes = self.song().scenes
        selected_scene = self.song().view.selected_scene
        new_offset = index_if(lambda a: a == selected_scene, all_scenes)
        if new_offset < len(all_scenes):
            self.set_offsets(self.track_offset(), new_offset)

    def _update_stop_all_clips_button(self):
        button = self._stop_all_button
        if button:
            value_to_send = False
            if button.is_pressed():
                value_to_send = self._stop_clip_value
            button.set_light(value_to_send)