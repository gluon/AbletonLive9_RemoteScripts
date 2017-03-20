# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/session_component.py
# Compiled at: 2016-09-29 19:13:24
from __future__ import absolute_import, print_function
import Live
from itertools import imap
from ableton.v2.base import Proxy, liveobj_valid
from ableton.v2.control_surface.control import ButtonControl
from pushbase.actions import get_clip_name
from pushbase.colors import Blink, Pulse
from pushbase.special_session_component import ClipSlotCopyHandler, SpecialClipSlotComponent, SpecialSceneComponent, SpecialSessionComponent
from .clip_decoration import ClipDecoratedPropertiesCopier
from .colors import IndexedColor, translate_color_index
from .skin_default import CLIP_PLAYING_COLOR, RECORDING_COLOR
PLAYING_CLIP_PULSE_SPEED = 48
TRIGGERED_CLIP_BLINK_SPEED = 24

class DecoratingCopyHandler(ClipSlotCopyHandler):

    def __init__(self, decorator_factory=None, *a, **k):
        assert decorator_factory is not None
        super(DecoratingCopyHandler, self).__init__(*a, **k)
        self._decorator_factory = decorator_factory
        return

    def _on_duplicated(self, source_clip_slot, target_clip_slot):
        super(DecoratingCopyHandler, self)._on_duplicated(source_clip_slot, target_clip_slot)
        ClipDecoratedPropertiesCopier(source_clip=source_clip_slot.clip, destination_clip=target_clip_slot.clip, decorator_factory=self._decorator_factory).post_duplication_action()


class ClipProxy(Proxy):

    @property
    def name(self):
        return get_clip_name(self.proxied_object)


class ClipSlotComponent(SpecialClipSlotComponent):
    _decorator_factory = None
    select_color_button = ButtonControl()

    def __init__(self, color_chooser=None, *a, **k):
        super(ClipSlotComponent, self).__init__(*a, **k)
        self._color_chooser = color_chooser

    @select_color_button.released
    def select_color_button(self, button):
        self._color_chooser.object = None
        return

    def _on_launch_button_pressed(self):
        if self.select_color_button.is_pressed and self._color_chooser is not None:
            clip = self._clip_slot.clip if self.has_clip() else None
            if liveobj_valid(clip):
                self._color_chooser.object = ClipProxy(clip)
        else:
            super(ClipSlotComponent, self)._on_launch_button_pressed()
        return

    def _feedback_value(self, track, slot_or_clip):
        clip_color = self._color_value(slot_or_clip)
        if slot_or_clip.is_triggered and not slot_or_clip.will_record_on_start:
            if isinstance(slot_or_clip, Live.Clip.Clip):
                return Blink(color1=CLIP_PLAYING_COLOR, color2=IndexedColor(clip_color), speed=TRIGGERED_CLIP_BLINK_SPEED)
            return 'Session.EmptySlotTriggeredPlay'
        else:
            if slot_or_clip.is_playing:
                animate_to_color = RECORDING_COLOR if slot_or_clip.is_recording else IndexedColor(clip_color)
                return Pulse(color1=IndexedColor.from_push_index(clip_color, 2), color2=animate_to_color, speed=PLAYING_CLIP_PULSE_SPEED)
            return super(ClipSlotComponent, self)._feedback_value(track, slot_or_clip)

    def _color_value(self, slot_or_clip):
        return translate_color_index(slot_or_clip.color_index)

    def _on_clip_duplicated(self, source_clip, destination_clip):
        super(ClipSlotComponent, self)._on_clip_duplicated(source_clip, destination_clip)
        if self._decorator_factory:
            ClipDecoratedPropertiesCopier(source_clip=source_clip, destination_clip=destination_clip, decorator_factory=self._decorator_factory).post_duplication_action()

    def set_decorator_factory(self, factory):
        self._decorator_factory = factory


class SceneComponent(SpecialSceneComponent):
    clip_slot_component_type = ClipSlotComponent

    def __init__(self, color_chooser=None, *a, **k):
        self._color_chooser = color_chooser
        super(SceneComponent, self).__init__(*a, **k)

    def build_clip_slot_list(self):
        scene_index = list(self.song.scenes).index(self._scene)

        def slot_for_track(mixable):
            if not hasattr(mixable, 'clip_slots') or len(mixable.clip_slots) == 0:
                return None
            else:
                return mixable.clip_slots[scene_index]
                return None

        return imap(slot_for_track, self._session_ring.controlled_tracks())

    def _create_clip_slot(self):
        return self.clip_slot_component_type(color_chooser=self._color_chooser)


class SessionComponent(SpecialSessionComponent):
    scene_component_type = SceneComponent

    def __init__(self, color_chooser=None, *a, **k):
        self._color_chooser = color_chooser
        super(SessionComponent, self).__init__(*a, **k)

    def _create_scene(self):
        return self.scene_component_type(session_ring=self._session_ring, color_chooser=self._color_chooser)