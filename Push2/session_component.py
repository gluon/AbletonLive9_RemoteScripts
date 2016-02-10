#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/session_component.py
from __future__ import absolute_import, print_function
from itertools import imap
from pushbase.special_session_component import SpecialClipSlotComponent, SpecialSceneComponent, SpecialSessionComponent
from .clip_decoration import ClipDecoratedPropertiesCopier
from .colors import translate_color_index, WHITE_COLOR_INDEX_FROM_LIVE, WHITE_MIDI_VALUE

class ClipSlotComponent(SpecialClipSlotComponent):
    _decorator_factory = None

    def _color_value(self, slot_or_clip):
        if slot_or_clip.color_index == WHITE_COLOR_INDEX_FROM_LIVE:
            return WHITE_MIDI_VALUE
        return translate_color_index(slot_or_clip.color_index)

    def _do_duplicate_clip(self):

        def get_destination_clip(destination_slot_ix):
            track = self._clip_slot.canonical_parent
            return track.clip_slots[destination_slot_ix].clip

        if not (self._clip_slot and self._clip_slot.has_clip):
            return
        destination_slot_ix = super(ClipSlotComponent, self)._do_duplicate_clip()
        if destination_slot_ix is not None and self._decorator_factory:
            ClipDecoratedPropertiesCopier(target_clip=self._clip_slot.clip, destination_clip=get_destination_clip(destination_slot_ix), decorator_factory=self._decorator_factory).post_duplication_action()
        return destination_slot_ix

    def set_decorator_factory(self, factory):
        self._decorator_factory = factory


class SceneComponent(SpecialSceneComponent):
    clip_slot_component_type = ClipSlotComponent

    def build_clip_slot_list(self):
        scene_index = list(self.song.scenes).index(self._scene)

        def slot_for_track(mixable):
            if not hasattr(mixable, 'clip_slots') or len(mixable.clip_slots) == 0:
                return None
            else:
                return mixable.clip_slots[scene_index]

        return imap(slot_for_track, self._session_ring.controlled_tracks())


class SessionComponent(SpecialSessionComponent):
    scene_component_type = SceneComponent