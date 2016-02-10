#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/special_session_component.py
from __future__ import absolute_import, print_function
import Live
from ableton.v2.base import forward_property, listens, liveobj_valid
from ableton.v2.control_surface import Component
from ableton.v2.control_surface.components import ClipSlotComponent, SceneComponent, SessionComponent
from ableton.v2.control_surface.control import ButtonControl
from ableton.v2.control_surface.mode import EnablingModesComponent
from pushbase.touch_strip_element import TouchStripStates, TouchStripModes
from .message_box_component import Messenger
from .consts import MessageBoxText

class DuplicateSceneComponent(Component, Messenger):

    def __init__(self, session_ring = None, *a, **k):
        super(DuplicateSceneComponent, self).__init__(*a, **k)
        raise session_ring is not None or AssertionError
        self._session_ring = session_ring
        self._scene_buttons = None

    def set_scene_buttons(self, buttons):
        self._scene_buttons = buttons
        self._on_scene_value.subject = buttons

    @listens('value')
    def _on_scene_value(self, value, index, _, is_momentary):
        if self.is_enabled() and (value or not is_momentary):
            try:
                self.song.duplicate_scene(self._session_ring.scene_offset + index)
                self.show_notification(MessageBoxText.DUPLICATE_SCENE % self.song.view.selected_scene.name)
            except Live.Base.LimitationError:
                self.expect_dialog(MessageBoxText.SCENE_LIMIT_REACHED)
            except RuntimeError:
                self.expect_dialog(MessageBoxText.SCENE_DUPLICATION_FAILED)
            except IndexError:
                pass


class SpecialClipSlotComponent(ClipSlotComponent, Messenger):

    def _do_delete_clip(self):
        if self._clip_slot and self._clip_slot.has_clip:
            clip_name = self._clip_slot.clip.name
            self._clip_slot.delete_clip()
            self.show_notification(MessageBoxText.DELETE_CLIP % clip_name)

    def _do_select_clip(self, clip_slot):
        if liveobj_valid(self._clip_slot):
            if self.song.view.highlighted_clip_slot != self._clip_slot:
                self.song.view.highlighted_clip_slot = self._clip_slot

    def _do_duplicate_clip(self):
        if self._clip_slot and self._clip_slot.has_clip:
            try:
                slot_name = self._clip_slot.clip.name
                track = self._clip_slot.canonical_parent
                destination_slot_ix = track.duplicate_clip_slot(list(track.clip_slots).index(self._clip_slot))
                self.show_notification(MessageBoxText.DUPLICATE_CLIP % slot_name)
                return destination_slot_ix
            except Live.Base.LimitationError:
                self.expect_dialog(MessageBoxText.SCENE_LIMIT_REACHED)
            except RuntimeError:
                self.expect_dialog(MessageBoxText.CLIP_DUPLICATION_FAILED)


class SpecialSceneComponent(SceneComponent, Messenger):
    clip_slot_component_type = SpecialClipSlotComponent

    def _do_delete_scene(self, scene):
        try:
            if self._scene:
                song = self.song
                name = self._scene.name
                song.delete_scene(list(song.scenes).index(self._scene))
                self.show_notification(MessageBoxText.DELETE_SCENE % name)
        except RuntimeError:
            pass


class SpecialSessionComponent(SessionComponent):
    """
    Special session subclass that handles ConfigurableButtons
    and has a button to fire the selected clip slot.
    """
    _session_component_ends_initialisation = False
    scene_component_type = SpecialSceneComponent
    duplicate_button = ButtonControl()

    def __init__(self, *a, **k):
        super(SpecialSessionComponent, self).__init__(*a, **k)
        self._slot_launch_button = None
        self._duplicate_button = None
        self._duplicate = self.register_component(DuplicateSceneComponent(self._session_ring))
        self._duplicate_enabler = self.register_component(EnablingModesComponent(component=self._duplicate))
        self._end_initialisation()

    duplicate_layer = forward_property('_duplicate')('layer')

    @duplicate_button.pressed
    def duplicate_button(self, button):
        self._duplicate_enabler.selected_mode = 'enabled'

    @duplicate_button.released
    def duplicate_button(self, button):
        self._duplicate_enabler.selected_mode = 'disabled'

    def set_slot_launch_button(self, button):
        self._slot_launch_button = button
        self._on_slot_launch_value.subject = button

    def set_clip_launch_buttons(self, buttons):
        if buttons:
            buttons.reset()
        super(SpecialSessionComponent, self).set_clip_launch_buttons(buttons)

    def set_touch_strip(self, touch_strip):
        if touch_strip:
            touch_strip.set_mode(TouchStripModes.CUSTOM_FREE)
            touch_strip.send_state([ TouchStripStates.STATE_OFF for _ in xrange(touch_strip.state_count) ])
        self._on_touch_strip_value.subject = touch_strip

    @listens('value')
    def _on_touch_strip_value(self, value):
        pass

    @listens('value')
    def _on_slot_launch_value(self, value):
        if self.is_enabled():
            if value != 0 or not self._slot_launch_button.is_momentary():
                if liveobj_valid(self.song.view.highlighted_clip_slot):
                    self.song.view.highlighted_clip_slot.fire()
                self._slot_launch_button.turn_on()
            else:
                self._slot_launch_button.turn_off()