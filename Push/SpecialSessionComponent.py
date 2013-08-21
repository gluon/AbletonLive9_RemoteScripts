#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/SpecialSessionComponent.py
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.SessionComponent import SessionComponent
from _Framework.ClipSlotComponent import ClipSlotComponent
from _Framework.SceneComponent import SceneComponent
from _Framework.SessionZoomingComponent import SessionZoomingComponent
from _Framework.SubjectSlot import subject_slot
from _Framework.ScrollComponent import ScrollComponent
from _Framework.Util import forward_property
from _Framework.ModesComponent import ModesComponent
from MessageBoxComponent import Messenger
import consts
from consts import MessageBoxText
import Live

class SpecialSessionZoomingComponent(SessionZoomingComponent):
    """
    Zooming component that does not disable session, instead it sends
    it to the back by changing its priority.
    """

    def set_button_matrix(self, buttons):
        if buttons:
            buttons.reset()
        super(SpecialSessionZoomingComponent, self).set_button_matrix(buttons)

    def _session_set_enabled(self, is_enabled):
        layer = self._session.layer
        if layer:
            layer.priority = None if is_enabled else consts.HIDDEN_SESSION_PRIORITY


class DuplicateSceneComponent(ControlSurfaceComponent, Messenger):

    def __init__(self, session = None, *a, **k):
        super(DuplicateSceneComponent, self).__init__(*a, **k)
        if not session:
            raise AssertionError
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

    def update(self):
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

    def _feedback_value(self):
        value_to_send = -1
        if self._clip_slot != None:
            slot_or_clip = self._clip_slot
            if self.has_clip():
                slot_or_clip = self._clip_slot.clip
                if self._stopped_value != None:
                    value_to_send = self._stopped_value
                else:
                    try:
                        value_to_send = self._clip_palette[self._clip_slot.clip.color]
                    except KeyError:
                        if self._clip_rgb_table != None:
                            value_to_send = self._find_nearest_color(self._clip_rgb_table, self._clip_slot.clip.color)
                        else:
                            value_to_send = 0
            else:
                track = self._clip_slot.canonical_parent
                if track and track.can_be_armed and (track.arm or track.implicit_arm) and self._clip_slot.has_stop_button and self._record_button_value:
                    value_to_send = self._record_button_value
            if slot_or_clip.is_triggered:
                value_to_send = self._triggered_to_record_value if slot_or_clip.will_record_on_start else self._triggered_to_play_value
            elif slot_or_clip.is_playing:
                value_to_send = self._recording_value if slot_or_clip.is_recording else self._started_value
            elif hasattr(slot_or_clip, 'controls_other_clips') and slot_or_clip.controls_other_clips:
                track = self._clip_slot.canonical_parent
                tracklist = list(track.canonical_parent.tracks)
                trackIndex = tracklist.index(track)
                clipIndex = list(track.clip_slots).index(slot_or_clip)
                nextTrack = None
                nextSlot = None
                x = 1
                while x < 8:
                    nextSlot = tracklist[trackIndex+x].clip_slots[clipIndex]
                    if nextSlot.has_clip:
                        value_to_send = self._find_nearest_color(self._clip_rgb_table, nextSlot.clip.color)
                        break
                    x = x + 1
        return value_to_send

class SpecialSceneComponent(SceneComponent, Messenger):
    clip_slot_component_type = SpecialClipSlotComponent

    def _on_is_triggered_changed(self):
        if not self._scene != None:
            raise AssertionError
            if self.is_enabled() and self._launch_button != None:
                self._scene.is_triggered and self._launch_button.send_value(self._triggered_value)
            else:
                self._launch_button.turn_on()

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
        self._duplicate, self._duplicate_modes, self._paginator = self.register_components(DuplicateSceneComponent(self), ModesComponent(), ScrollComponent())
        self._paginator.can_scroll_up = self._can_scroll_page_up
        self._paginator.can_scroll_down = self._can_scroll_page_down
        self._paginator.scroll_up = self._scroll_page_up
        self._paginator.scroll_down = self._scroll_page_down
        self._duplicate.set_enabled(False)
        self._duplicate_modes.add_mode('disabled', None)
        self._duplicate_modes.add_mode('enabled', self._duplicate)
        self._duplicate_modes.selected_mode = 'disabled'
        self._duplicate_modes.momentary_toggle = True
        self._track_playing_slots = self.register_slot_manager()
        self._end_initialisation()

    duplicate_layer = forward_property('_duplicate')('layer')

    def set_duplicate_button(self, button):
        self._duplicate_modes.set_toggle_button(button)

    def set_page_up_button(self, page_up_button):
        self._paginator.set_scroll_up_button(page_up_button)

    def set_page_down_button(self, page_down_button):
        self._paginator.set_scroll_down_button(page_down_button)

    def set_slot_launch_button(self, button):
        self._slot_launch_button = button
        self._on_slot_launch_value.subject = button

    def set_stop_track_clip_buttons(self, buttons):
        for button in buttons or []:
            if button:
                button.set_on_off_values('Option.On', 'Option.Off')

        super(SpecialSessionComponent, self).set_stop_track_clip_buttons(buttons)

    def set_clip_launch_buttons(self, buttons):
        if buttons:
            buttons.reset()
        super(SpecialSessionComponent, self).set_clip_launch_buttons(buttons)

    def _reassign_scenes(self):
        super(SpecialSessionComponent, self)._reassign_scenes()
        self._paginator.update()

    def _reassign_tracks(self):
        super(SpecialSessionComponent, self)._reassign_tracks()
        self._track_playing_slots.disconnect()
        tracks_to_use = self.tracks_to_use()
        for index in range(self._num_tracks):
            listener = lambda index = index: self._on_playing_slot_index_changed(index)
            if self._track_offset + index < len(tracks_to_use):
                track = tracks_to_use[self._track_offset + index]
                if track in self.song().tracks:
                    self._track_slots.register_slot(track, listener, 'playing_slot_index')
            listener()

    def _on_fired_slot_index_changed(self, index):
        self._update_stop_clips_led(index)

    def _on_playing_slot_index_changed(self, index):
        self._update_stop_clips_led(index)

    def _update_stop_clips_led(self, index):
        """ self.canonical_parent.log_message('update_Stop called with parameter ' + str(index)) """
        track_index = index + self.track_offset()
        tracks_to_use = self.tracks_to_use()
        if self.is_enabled() and self._stop_track_clip_buttons != None and index < len(self._stop_track_clip_buttons):
            button = self._stop_track_clip_buttons[index]
            if button != None :
                if track_index < len(tracks_to_use) and tracks_to_use[track_index].clip_slots:
                    check_for_group_track = True
                    if tracks_to_use[track_index].fired_slot_index == -2:
                        button.set_light('Mixer.StoppingTrack')
                    elif tracks_to_use[track_index].playing_slot_index >= 0:
                        button.set_light('Mixer.StopTrack')
                    else:
                        button.turn_off()
                        if tracks_to_use[track_index].is_foldable:
                            check_for_group_track = False;
                            for actual_slot in tracks_to_use[track_index].clip_slots:
                                if actual_slot.is_playing:
                                    button.set_light('Mixer.StopTrack')
                    if check_for_group_track:
                        tracklist = list(tracks_to_use[track_index].canonical_parent.tracks)
                        tracklist_index = tracklist.index(tracks_to_use[track_index])
                        x = 1
                        while x < 8:
                            if tracklist_index-x >= 0:                
                                if tracklist[tracklist_index-x].is_foldable:
                                    if index-x >= 0:
                                        self._update_stop_clips_led(index-x)
                                        break
                            x = x + 1
                else:
                    button.turn_off()

    @subject_slot('value')
    def _on_slot_launch_value(self, value):
        if self.is_enabled():
            if value != 0 or not self._slot_launch_button.is_momentary():
                if self.song().view.highlighted_clip_slot != None:
                    self.song().view.highlighted_clip_slot.fire()
                self._slot_launch_button.turn_on()
            else:
                self._slot_launch_button.turn_off()

    def _can_scroll_page_up(self):
        return self.scene_offset() > 0

    def _can_scroll_page_down(self):
        return self.scene_offset() < len(self.song().scenes) - self.height()

    def _scroll_page_up(self):
        height = self.height()
        track_offset = self.track_offset()
        scene_offset = self.scene_offset()
        if scene_offset > 0:
            new_scene_offset = scene_offset
            if scene_offset % height > 0:
                new_scene_offset -= scene_offset % height
            else:
                new_scene_offset = max(0, scene_offset - height)
            self.set_offsets(track_offset, new_scene_offset)

    def _scroll_page_down(self):
        height = self.height()
        track_offset = self.track_offset()
        scene_offset = self.scene_offset()
        new_scene_offset = scene_offset + height - scene_offset % height
        self.set_offsets(track_offset, new_scene_offset)
