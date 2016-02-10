#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad_Pro/SpecialSessionComponent.py
import Live
from _Framework.Util import find_if, in_range
from _Framework.Dependency import depends
from _Framework.SubjectSlot import subject_slot, subject_slot_group
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.Control import ButtonControl
from _Framework.SessionComponent import SessionComponent
from _Framework.SessionZoomingComponent import SessionZoomingComponent
from _Framework.SceneComponent import SceneComponent
from _Framework.ClipSlotComponent import ClipSlotComponent
from .ClipActionsComponent import double_clip, duplicate_clip

class SpecialClipSlotComponent(ClipSlotComponent):
    quantization_component = None

    @depends(should_arm=None)
    def __init__(self, should_arm = None, *a, **k):
        self._should_arm = False
        self._double_loop_button = None
        self._quantize_button = None
        super(SpecialClipSlotComponent, self).__init__(*a, **k)
        self._should_arm = should_arm

    def set_double_loop_button(self, button):
        self._double_loop_button = button

    def set_quantize_button(self, button):
        self._quantize_button = button

    def _do_select_clip(self, clip_slot):
        super(SpecialClipSlotComponent, self)._do_select_clip(clip_slot)
        if self._clip_slot is not None:
            if not self.application().view.is_view_visible('Detail'):
                self.application().view.show_view('Detail')
            if not self.application().view.is_view_visible('Detail/Clip'):
                self.application().view.show_view('Detail/Clip')

    @subject_slot('value')
    def _launch_button_value(self, value):
        if self.is_enabled() and self._clip_slot is not None:
            if self._select_button and self._select_button.is_pressed() and value:
                self._do_select_clip(self._clip_slot)
            elif self._double_loop_button and self._double_loop_button.is_pressed() and value:
                self._do_double_loop(self._clip_slot)
            elif self._duplicate_button and self._duplicate_button.is_pressed() and value:
                self._do_duplicate_clip()
            elif self._delete_button and self._delete_button.is_pressed() and value:
                self._do_delete_clip()
            elif self._quantize_button and self._quantize_button.is_pressed() and value:
                self._do_quantize_clip(self._clip_slot)
            else:
                if self._should_arm() and value:
                    self._do_track_arm()
                self._do_launch_clip(value)

    @property
    def can_duplicate_loop(self):
        clip = self.song().view.detail_clip
        return clip and clip.is_midi_clip

    def _do_double_loop(self, clip_slot):
        self._do_select_clip(clip_slot)
        if self.can_duplicate_loop:
            double_clip(self.song().view.detail_clip)

    def _do_quantize_clip(self, clip_slot):
        clip = clip_slot.clip
        if clip and self.quantization_component:
            self.quantization_component.quantize_clip(clip)

    def _do_duplicate_clip(self):
        if self._clip_slot:
            duplicate_clip(self.song(), self._clip_slot)

    def _do_track_arm(self):
        if self._clip_slot:
            track = self._clip_slot.canonical_parent
            if track.can_be_armed and not track.arm:
                if self.song().exclusive_arm:
                    for t in self.song().tracks:
                        if t.can_be_armed and t.arm:
                            t.arm = False

                track.arm = True
                if self.song().view.selected_track != track:
                    self.song().view.selected_track = track
            if not self.song().session_record and self._clip_slot.has_clip:
                self.song().session_record = True


class SpecialSceneComponent(SceneComponent):
    clip_slot_component_type = SpecialClipSlotComponent

    def __init__(self, *a, **k):
        self._duplicate_button = None
        super(SpecialSceneComponent, self).__init__(*a, **k)

    def set_duplicate_button(self, button):
        self._duplicate_button = button

    @subject_slot('value')
    def _launch_value(self, value):
        if self.is_enabled() and self._scene != None:
            if self._select_button and self._select_button.is_pressed() and value:
                self._do_select_scene(self._scene)
            elif self._delete_button and self._delete_button.is_pressed() and value:
                self._do_delete_scene(self._scene)
            elif self._duplicate_button and self._duplicate_button.is_pressed() and value:
                self._do_duplicate_scene()
            else:
                self._do_launch_scene(value)

    def _do_duplicate_scene(self):
        try:
            song = self.song()
            song.duplicate_scene(list(song.scenes).index(self._scene))
        except Live.Base.LimitationError:
            pass
        except RuntimeError:
            pass
        except IndexError:
            pass


class SpecialSessionComponent(SessionComponent):
    scene_component_type = SpecialSceneComponent
    delete_button = ButtonControl(color='DefaultButton.Off', pressed_color='DefaultButton.On')
    quantize_button = ButtonControl(color='DefaultButton.Off', pressed_color='DefaultButton.On')
    double_button = ButtonControl(color='DefaultButton.Off', pressed_color='DefaultButton.On')
    duplicate_button = ButtonControl(color='DefaultButton.Off', pressed_color='DefaultButton.On')

    def __init__(self, *a, **k):
        self._stop_scene_clip_buttons = None
        super(SpecialSessionComponent, self).__init__(*a, **k)

    def set_clip_launch_buttons(self, buttons):
        if buttons:
            buttons.reset()
        super(SpecialSessionComponent, self).set_clip_launch_buttons(buttons)

    def set_stop_track_clip_buttons(self, buttons):
        if buttons:
            buttons.reset()
        super(SpecialSessionComponent, self).set_stop_track_clip_buttons(buttons)

    def set_scene_launch_buttons(self, buttons):
        if buttons:
            buttons.reset_state()
        super(SpecialSessionComponent, self).set_scene_launch_buttons(buttons)

    def set_stop_scene_clip_buttons(self, buttons):
        if buttons:
            buttons.reset()
        self._stop_scene_clip_buttons = buttons
        self._on_stop_scene_value.replace_subjects(buttons or [])
        self._update_stop_scene_clip_buttons()

    def set_stop_all_clips_button(self, button):
        if button:
            button.reset()
        super(SpecialSessionComponent, self).set_stop_all_clips_button(button)

    @subject_slot_group('value')
    def _on_stop_scene_value(self, value, button):
        if self.is_enabled():
            if value is not 0 or not button.is_momentary():
                scene_index = list(self._stop_scene_clip_buttons).index(button) + self.scene_offset()
                for track in self.tracks_to_use():
                    if in_range(scene_index, 0, len(track.clip_slots)) and (track.playing_slot_index == scene_index or track.fired_slot_index == scene_index):
                        track.stop_all_clips()

    def update_navigation_buttons(self):
        self._vertical_banking.update()
        self._horizontal_banking.update()

    def _update_stop_clips_led(self, index):
        if self.is_enabled() and self._stop_track_clip_buttons is not None and index < len(self._stop_track_clip_buttons):
            button = self._stop_track_clip_buttons[index]
            if button is not None:
                tracks_to_use = self.tracks_to_use()
                track_index = index + self.track_offset()
                value_to_send = None
                if track_index < len(tracks_to_use):
                    if tracks_to_use[track_index].clip_slots:
                        track = tracks_to_use[track_index]
                        if track.fired_slot_index == -2:
                            value_to_send = self._stop_clip_triggered_value
                        elif track.playing_slot_index >= 0:
                            value_to_send = self._stop_clip_value
                        else:
                            value_to_send = 'Session.StoppedClip'
                if value_to_send is None:
                    button.turn_off()
                elif in_range(value_to_send, 0, 128):
                    button.send_value(value_to_send)
                else:
                    button.set_light(value_to_send)

    def _update_stop_scene_clip_buttons(self):
        if self.is_enabled():
            for index in xrange(self._num_scenes):
                self._update_stop_scene_leds(index)

    def _update_stop_scene_leds(self, index):
        scenes = self.song().scenes
        scene_index = index + self.scene_offset()
        if self.is_enabled() and self._stop_scene_clip_buttons is not None and index < len(self._stop_scene_clip_buttons):
            button = self._stop_scene_clip_buttons[index]
            if button is not None:
                value_to_send = None
                if scene_index < len(scenes) and scenes[scene_index].clip_slots:
                    tracks = self.tracks_to_use()
                    if find_if(lambda x: x.playing_slot_index == scene_index and x.fired_slot_index != -2, tracks):
                        value_to_send = self._stop_clip_value
                    elif find_if(lambda x: x.fired_slot_index == -2 and x.playing_slot_index == scene_index, tracks):
                        value_to_send = self._stop_clip_triggered_value
                    else:
                        value_to_send = 'Session.StoppedClip'
                if value_to_send is None:
                    button.turn_off()
                elif in_range(value_to_send, 0, 128):
                    button.send_value(value_to_send)
                else:
                    button.set_light(value_to_send)

    def _update_stop_all_clips_button(self):
        button = self._stop_all_button
        if button:
            value_to_send = 'Session.StoppedClip'
            tracks = self.tracks_to_use()
            if find_if(lambda x: x.playing_slot_index >= 0 and x.fired_slot_index != -2, tracks):
                value_to_send = self._stop_clip_value
            elif find_if(lambda x: x.fired_slot_index == -2, tracks):
                value_to_send = self._stop_clip_triggered_value
            if value_to_send is None:
                button.turn_off()
            else:
                button.set_light(value_to_send)

    @subject_slot_group('fired_slot_index')
    def _on_fired_slot_index_changed(self, track_index):
        button_index = track_index - self.track_offset()
        self._update_stop_clips_led(button_index)
        self._update_stop_scene_clip_buttons()
        self._update_stop_all_clips_button()

    @subject_slot_group('playing_slot_index')
    def _on_playing_slot_index_changed(self, track_index):
        button_index = track_index - self.track_offset()
        self._update_stop_clips_led(button_index)
        self._update_stop_scene_clip_buttons()
        self._update_stop_all_clips_button()

    def _reassign_scenes(self):
        super(SpecialSessionComponent, self)._reassign_scenes()
        self._update_stop_scene_clip_buttons()

    def update(self):
        super(SpecialSessionComponent, self).update()
        if self._allow_updates:
            self._update_stop_scene_clip_buttons()


class SpecialSessionZoomingComponent(SessionZoomingComponent):
    """
    Specialized SessionZoomingComponent that doesn't disable/enable its
    associated SessionComponent or deal with showing/hiding session highlight.
    """

    def on_enabled_changed(self):
        self.update()

    def set_enabled(self, enable):
        self._explicit_is_enabled = bool(enable)
        self._update_is_enabled()
        for component in self._sub_components:
            if not isinstance(component, SessionComponent):
                component._set_enabled_recursive(self.is_enabled())


class SessionZoomingManagerComponent(ControlSurfaceComponent):
    session_zooming_button = ButtonControl(color='Session.Enabled')

    def __init__(self, modes, *a, **k):
        self._modes = modes
        self._mode = modes.selected_mode
        super(SessionZoomingManagerComponent, self).__init__(*a, **k)

    @session_zooming_button.pressed
    def session_zooming_button(self, button):
        pass

    @session_zooming_button.pressed_delayed
    def session_zooming_button(self, button):
        """
        Show the session overview
        """
        self._modes.selected_mode = 'prioritized_session_zooming_mode'

    @session_zooming_button.released_immediately
    def session_zooming_button(self, button):
        self._modes.selected_mode = 'session_mode'

    @session_zooming_button.released_delayed
    def session_zooming_button(self, button):
        if self._mode:
            self._modes.selected_mode = self._mode

    def on_enabled_changed(self):
        super(SessionZoomingManagerComponent, self).on_enabled_changed()
        if self.is_enabled():
            self._mode = self._modes.selected_mode