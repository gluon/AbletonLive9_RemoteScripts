#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/SpecialSessionComponent.py
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.SessionComponent import SessionComponent
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.SceneComponent import SceneComponent
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import forward_property
from _Framework.ModesComponent import EnablingModesComponent
from MessageBoxComponent import Messenger
from TouchStripElement import TouchStripElement, TouchStripModes
from consts import MessageBoxText
import Live

class DuplicateSceneComponent(ControlSurfaceComponent, Messenger):

    def __init__(self, session = None, *a, **k):
        super(DuplicateSceneComponent, self).__init__(*a, **k)
        raise session or AssertionError
        self._session = session
        self._scene_buttons = None

    def set_scene_buttons(self, buttons):
        self._scene_buttons = buttons
        self._on_scene_value.subject = buttons

    @subject_slot('value')
    def _on_scene_value(self, value, index, _, is_momentary):
        if self.is_enabled() and (value or not is_momentary):
            try:
                self.song().duplicate_scene(self._session._scene_offset + index)
                self.show_notification(MessageBoxText.DUPLICATE_SCENE % self.song().view.selected_scene.name)
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
        if self._clip_slot != None:
            if self.song().view.highlighted_clip_slot != self._clip_slot:
                self.song().view.highlighted_clip_slot = self._clip_slot

    def _do_duplicate_clip(self):
        if self._clip_slot and self._clip_slot.has_clip:
            try:
                slot_name = self._clip_slot.clip.name
                track = self._clip_slot.canonical_parent
                track.duplicate_clip_slot(list(track.clip_slots).index(self._clip_slot))
                self.show_notification(MessageBoxText.DUPLICATE_CLIP % slot_name)
            except Live.Base.LimitationError:
                self.expect_dialog(MessageBoxText.SCENE_LIMIT_REACHED)
            except RuntimeError:
                self.expect_dialog(MessageBoxText.CLIP_DUPLICATION_FAILED)


class SpecialSceneComponent(SceneComponent, Messenger):
    clip_slot_component_type = SpecialClipSlotComponent

    def _do_delete_scene(self, scene):
        try:
            if self._scene:
                song = self.song()
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

    def __init__(self, *a, **k):
        super(SpecialSessionComponent, self).__init__(*a, **k)
        self._slot_launch_button = None
        self._duplicate_button = None
        self._duplicate = self.register_component(DuplicateSceneComponent(self))
        self._duplicate_enabler = self.register_component(EnablingModesComponent(component=self._duplicate))
        self._duplicate_enabler.momentary_toggle = True
        self._end_initialisation()

    duplicate_layer = forward_property('_duplicate')('layer')

    def set_duplicate_button(self, button):
        self._duplicate_enabler.set_toggle_button(button)

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
            touch_strip.send_state([ TouchStripElement.STATE_OFF for _ in xrange(TouchStripElement.STATE_COUNT) ])
        self._on_touch_strip_value.subject = touch_strip

    @subject_slot('value')
    def _on_touch_strip_value(self, value):
        pass

    @subject_slot('value')
    def _on_slot_launch_value(self, value):
        if self.is_enabled():
            if value != 0 or not self._slot_launch_button.is_momentary():
                if self.song().view.highlighted_clip_slot != None:
                    self.song().view.highlighted_clip_slot.fire()
                self._slot_launch_button.turn_on()
            else:
                self._slot_launch_button.turn_off()

    def set_show_highlight(self, show_highlight):
        super(SpecialSessionComponent, self).set_show_highlight(True)