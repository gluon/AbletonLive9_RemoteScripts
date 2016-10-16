#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/actions.py
from __future__ import absolute_import, print_function
from pushbase.actions import CaptureAndInsertSceneComponent as CaptureAndInsertSceneComponentBase
from .clip_decoration import ClipDecoratedPropertiesCopier

class CaptureAndInsertSceneComponent(CaptureAndInsertSceneComponentBase):

    def __init__(self, name = None, decorator_factory = None, *a, **k):
        super(CaptureAndInsertSceneComponent, self).__init__(name, *a, **k)
        self._decorator_factory = decorator_factory

    def post_trigger_action(self):

        def get_playing_clip(track):
            slot_ix = track.playing_slot_index
            if slot_ix > -1:
                return track.clip_slots[slot_ix].clip

        played_clips = [ get_playing_clip(track) for track in self.song.tracks ]
        super(CaptureAndInsertSceneComponent, self).post_trigger_action()
        new_slots = self.song.view.selected_scene.clip_slots
        for ix, clip in enumerate(played_clips):
            if clip:
                ClipDecoratedPropertiesCopier(target_clip=clip, destination_clip=new_slots[ix].clip, decorator_factory=self._decorator_factory).post_duplication_action()