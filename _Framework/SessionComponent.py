#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/SessionComponent.py
import Live
from CompoundComponent import CompoundComponent
from SceneComponent import SceneComponent
from SubjectSlot import subject_slot
from ScrollComponent import ScrollComponent
from Util import in_range, product

class SessionComponent(CompoundComponent):
    """
    Class encompassing several scene to cover a defined section of
    Live's session.  It controls the session ring and the set of tracks
    controlled by a given mixer.
    """
    __subject_events__ = ('offset',)
    _linked_session_instances = []
    _minimal_track_offset = -1
    _minimal_scene_offset = -1
    _highlighting_callback = None
    _session_component_ends_initialisation = True
    scene_component_type = SceneComponent

    def __init__(self, num_tracks = 0, num_scenes = 0, *a, **k):
        super(SessionComponent, self).__init__(*a, **k)
        raise num_tracks >= 0 or AssertionError
        if not num_scenes >= 0:
            raise AssertionError
            self._track_offset = -1
            self._scene_offset = -1
            self._num_tracks = num_tracks
            self._num_scenes = num_scenes
            self._vertical_banking, self._horizontal_banking = self.register_components(ScrollComponent(), ScrollComponent())
            self._vertical_banking.can_scroll_up = self._can_bank_up
            self._vertical_banking.can_scroll_down = self._can_bank_down
            self._vertical_banking.scroll_up = self._bank_up
            self._vertical_banking.scroll_down = self._bank_down
            self._horizontal_banking.can_scroll_up = self._can_bank_left
            self._horizontal_banking.can_scroll_down = self._can_bank_right
            self._horizontal_banking.scroll_up = self._bank_left
            self._horizontal_banking.scroll_down = self._bank_right
            self._track_banking_increment = 1
            self._stop_all_button = None
            self._next_scene_button = None
            self._prev_scene_button = None
            self._stop_track_clip_buttons = None
            self._stop_track_clip_value = 127
            self._stop_track_clip_slots = self.register_slot_manager()
            self._highlighting_callback = None
            self._show_highlight = num_tracks > 0 and num_scenes > 0
            self._mixer = None
            self._track_slots = self.register_slot_manager()
            self._selected_scene = self.register_component(self._create_scene())
            self._scenes = self.register_components(*[ self._create_scene() for _ in xrange(num_scenes) ])
            self._session_component_ends_initialisation and self._end_initialisation()

    def _end_initialisation(self):
        self.on_selected_scene_changed()
        self.set_offsets(0, 0)

    def _create_scene(self):
        return self.scene_component_type(num_slots=self._num_tracks, tracks_to_use_callback=self.tracks_to_use)

    def disconnect(self):
        if self._is_linked():
            self._unlink()
        super(CompoundComponent, self).disconnect()

    def set_highlighting_callback(self, callback):
        if not (not callback or callable(callback)):
            raise AssertionError
            self._highlighting_callback = self._highlighting_callback != callback and callback
            self._do_show_highlight()

    def scene(self, index):
        raise in_range(index, 0, len(self._scenes)) or AssertionError
        return self._scenes[index]

    def selected_scene(self):
        return self._selected_scene

    def set_scene_bank_buttons(self, down_button, up_button):
        self.set_scene_bank_up_button(up_button)
        self.set_scene_bank_down_button(down_button)

    def set_scene_bank_up_button(self, button):
        self._bank_up_button = button
        self._vertical_banking.set_scroll_up_button(button)

    def set_scene_bank_down_button(self, button):
        self._bank_down_button = button
        self._vertical_banking.set_scroll_down_button(button)

    def set_track_bank_buttons(self, right_button, left_button):
        self.set_track_bank_left_button(left_button)
        self.set_track_bank_right_button(right_button)

    def set_track_bank_left_button(self, button):
        self._bank_left_button = button
        self._horizontal_banking.set_scroll_up_button(button)

    def set_track_bank_right_button(self, button):
        self._bank_right_button = button
        self._horizontal_banking.set_scroll_down_button(button)

    def set_stop_all_clips_button(self, button):
        self._stop_all_button = button
        self._on_stop_all_value.subject = button
        self._update_stop_all_clips_button()

    def set_stop_track_clip_buttons(self, buttons):
        self._stop_track_clip_slots.disconnect()
        self._stop_track_clip_buttons = buttons
        if self._stop_track_clip_buttons != None:
            for index, button in enumerate(self._stop_track_clip_buttons):
                if button:
                    self._stop_track_clip_slots.register_slot(button, self._on_stop_track_value, 'value', extra_kws={'identify_sender': True})
                self._on_fired_slot_index_changed(index)

    def set_track_banking_increment(self, increment):
        raise increment > 0 or AssertionError
        self._track_banking_increment = increment

    def set_stop_track_clip_value(self, value):
        raise in_range(value, 0, 128) or AssertionError
        self._stop_track_clip_value = value

    def set_select_buttons(self, next_button, prev_button):
        self.set_select_next_button(next_button)
        self.set_select_prev_button(prev_button)

    def set_select_next_button(self, next_button):
        self._next_scene_button = next_button
        self._on_next_scene_value.subject = next_button
        self._update_select_buttons()

    def set_select_prev_button(self, prev_button):
        self._prev_scene_button = prev_button
        self._on_prev_scene_value.subject = prev_button
        self._update_select_buttons()

    def set_clip_launch_buttons(self, buttons):
        raise not buttons or buttons.width() == self._num_tracks and buttons.height() == self._num_scenes or AssertionError
        if buttons:
            for button, (x, y) in buttons.iterbuttons():
                scene = self.scene(y)
                slot = scene.clip_slot(x)
                slot.set_launch_button(button)

        else:
            for x, y in product(xrange(self._num_tracks), xrange(self._num_scenes)):
                scene = self.scene(y)
                slot = scene.clip_slot(x)
                slot.set_launch_button(None)

    def set_scene_launch_buttons(self, buttons):
        raise not buttons or buttons.width() == self._num_scenes and buttons.height() == 1 or AssertionError
        if buttons:
            for button, (x, _) in buttons.iterbuttons():
                scene = self.scene(x)
                scene.set_launch_button(button)

        else:
            for x in xrange(self._num_scenes):
                scene = self.scene(x)
                scene.set_launch_button(None)

    def set_mixer(self, mixer):
        """ Sets the MixerComponent to be controlled by this session """
        self._mixer = mixer
        if self._mixer != None:
            self._mixer.set_track_offset(self.track_offset())

    def set_offsets(self, track_offset, scene_offset):
        if not track_offset >= 0:
            raise AssertionError
            raise scene_offset >= 0 or AssertionError
            track_increment = 0
            scene_increment = 0
            self._is_linked() and SessionComponent._perform_offset_change(track_offset - self._track_offset, scene_offset - self._scene_offset)
        else:
            if len(self.tracks_to_use()) > track_offset:
                track_increment = track_offset - self._track_offset
            if len(self.song().scenes) > scene_offset:
                scene_increment = scene_offset - self._scene_offset
            self._change_offsets(track_increment, scene_increment)

    def set_show_highlight(self, show_highlight):
        if self._show_highlight != show_highlight:
            self._show_highlight = show_highlight
            self._do_show_highlight()

    def on_enabled_changed(self):
        self.update()
        self._do_show_highlight()

    def update(self):
        if self._allow_updates:
            self._update_select_buttons()
            self._update_stop_track_clip_buttons()
            self._update_stop_all_clips_button()
        else:
            self._update_requests += 1

    def _update_stop_track_clip_buttons(self):
        if self.is_enabled():
            for index in xrange(self._num_tracks):
                self._on_fired_slot_index_changed(index)

    def on_scene_list_changed(self):
        if not self._update_scene_offset():
            self._reassign_scenes()

    def on_track_list_changed(self):
        num_tracks = len(self.tracks_to_use())
        new_track_offset = self.track_offset()
        if new_track_offset >= num_tracks:
            new_track_offset = num_tracks - 1
            new_track_offset -= new_track_offset % self._track_banking_increment
        self._reassign_tracks()
        self.set_offsets(new_track_offset, self.scene_offset())

    def on_selected_scene_changed(self):
        self._update_scene_offset()
        if self._selected_scene != None:
            self._selected_scene.set_scene(self.song().view.selected_scene)

    def width(self):
        return self._num_tracks

    def height(self):
        return len(self._scenes)

    def track_offset(self):
        return self._track_offset

    def scene_offset(self):
        return self._scene_offset

    def tracks_to_use(self):
        list_of_tracks = None
        if self._mixer != None:
            list_of_tracks = self._mixer.tracks_to_use()
        else:
            list_of_tracks = self.song().visible_tracks
        return list_of_tracks

    def _get_minimal_track_offset(self):
        return SessionComponent._minimal_track_offset if self._is_linked() else self.track_offset()

    def _get_minimal_scene_offset(self):
        return SessionComponent._minimal_scene_offset if self._is_linked() else self.scene_offset()

    def _can_bank_down(self):
        return len(self.song().scenes) > self._get_minimal_scene_offset() + 1

    def _can_bank_up(self):
        return self._get_minimal_scene_offset() > 0

    def _can_bank_right(self):
        return len(self.tracks_to_use()) > self._get_minimal_track_offset() + 1

    def _can_bank_left(self):
        return self._get_minimal_track_offset() > 0

    def _bank_up(self):
        return self.set_offsets(self.track_offset(), max(0, self.scene_offset() - 1))

    def _bank_down(self):
        return self.set_offsets(self.track_offset(), self.scene_offset() + 1)

    def _bank_right(self):
        return self.set_offsets(self.track_offset() + self._track_banking_increment, self.scene_offset())

    def _bank_left(self):
        return self.set_offsets(max(self.track_offset() - self._track_banking_increment, 0), self.scene_offset())

    def _update_stop_all_clips_button(self):
        pass

    def _update_select_buttons(self):
        selected_scene = self.song().view.selected_scene
        if self._next_scene_button != None:
            self._next_scene_button.set_light(selected_scene != self.song().scenes[-1])
        if self._prev_scene_button != None:
            self._next_scene_button.set_light(selected_scene != self.song().scenes[0])

    def _update_scene_offset(self):
        offset_corrected = False
        num_scenes = len(self.song().scenes)
        if self.scene_offset() >= num_scenes:
            self.set_offsets(self.track_offset(), num_scenes - 1)
            offset_corrected = True
        return offset_corrected

    def _change_offsets(self, track_increment, scene_increment):
        if not track_increment != 0:
            offsets_changed = scene_increment != 0
            offsets_changed and self._track_offset += track_increment
            self._scene_offset += scene_increment
            raise self._track_offset >= 0 or AssertionError
            if not self._scene_offset >= 0:
                raise AssertionError
                if self._mixer != None:
                    self._mixer.set_track_offset(self.track_offset())
                self._reassign_tracks()
                self._reassign_scenes()
                self.notify_offset()
                self.width() > 0 and self.height() > 0 and self._do_show_highlight()

    def _reassign_scenes(self):
        scenes = self.song().scenes
        for index, scene in enumerate(self._scenes):
            scene_index = self._scene_offset + index
            if len(scenes) > scene_index:
                scene.set_scene(scenes[scene_index])
                scene.set_track_offset(self._track_offset)
            else:
                self._scenes[index].set_scene(None)

        if self._selected_scene != None:
            self._selected_scene.set_track_offset(self._track_offset)
        self._vertical_banking.update()

    def _reassign_tracks(self):
        self._track_slots.disconnect()
        tracks_to_use = self.tracks_to_use()
        for index in range(self._num_tracks):
            listener = lambda index = index: self._on_fired_slot_index_changed(index)
            if self._track_offset + index < len(tracks_to_use):
                track = tracks_to_use[self._track_offset + index]
                if track in self.song().tracks:
                    self._track_slots.register_slot(track, listener, 'fired_slot_index')
            listener()

        self._horizontal_banking.update()

    @subject_slot('value')
    def _on_stop_all_value(self, value):
        self._stop_all_value(value)

    def _stop_all_value(self, value):
        if self.is_enabled():
            if value is not 0 or not self._stop_all_button.is_momentary():
                self.song().stop_all_clips()

    @subject_slot('value')
    def _on_next_scene_value(self, value):
        if self.is_enabled():
            if value is not 0 or not self._next_scene_button.is_momentary():
                selected_scene = self.song().view.selected_scene
                all_scenes = self.song().scenes
                if selected_scene != all_scenes[-1]:
                    index = list(all_scenes).index(selected_scene)
                    self.song().view.selected_scene = all_scenes[index + 1]

    @subject_slot('value')
    def _on_prev_scene_value(self, value):
        if self.is_enabled():
            if value is not 0 or not self._prev_scene_button.is_momentary():
                selected_scene = self.song().view.selected_scene
                all_scenes = self.song().scenes
                if selected_scene != all_scenes[0]:
                    index = list(all_scenes).index(selected_scene)
                    self.song().view.selected_scene = all_scenes[index - 1]

    @subject_slot('value')
    def _on_stop_track_value(self, value, sender):
        if self.is_enabled():
            if value is not 0 or not sender.is_momentary():
                tracks = self.tracks_to_use()
                track_index = list(self._stop_track_clip_buttons).index(sender) + self.track_offset()
                if in_range(track_index, 0, len(tracks)) and tracks[track_index] in self.song().tracks:
                    tracks[track_index].stop_all_clips()

    def _do_show_highlight(self):
        if self._highlighting_callback != None:
            return_tracks = self.song().return_tracks
            if len(return_tracks) > 0:
                include_returns = return_tracks[0] in self.tracks_to_use()
                self._show_highlight and self._highlighting_callback(self._track_offset, self._scene_offset, self.width(), self.height(), include_returns)
            else:
                self._highlighting_callback(-1, -1, -1, -1, include_returns)

    def _on_fired_slot_index_changed(self, index):
        tracks_to_use = self.tracks_to_use()
        track_index = index + self.track_offset()
        if self.is_enabled() and self._stop_track_clip_buttons != None:
            if index < len(self._stop_track_clip_buttons):
                button = self._stop_track_clip_buttons[index]
                if button != None:
                    track_index < len(tracks_to_use) and tracks_to_use[track_index].clip_slots and tracks_to_use[track_index].fired_slot_index == -2 and button.send_value(self._stop_track_clip_value)
                else:
                    button.turn_off()

    def _is_linked(self):
        return self in SessionComponent._linked_session_instances

    def _link(self):
        raise not self._is_linked() or AssertionError
        SessionComponent._linked_session_instances.append(self)

    def _unlink(self):
        raise self._is_linked() or AssertionError
        SessionComponent._linked_session_instances.remove(self)

    @staticmethod
    def _perform_offset_change(track_increment, scene_increment):
        """ Performs the given offset changes on all linked instances """
        if not len(SessionComponent._linked_session_instances) > 0:
            raise AssertionError
            scenes = Live.Application.get_application().get_document().scenes
            instances_covering_session = 0
            found_negative_offset = False
            minimal_track_offset = -1
            minimal_scene_offset = -1
            for instance in SessionComponent._linked_session_instances:
                new_track_offset = instance.track_offset() + track_increment
                new_scene_offset = instance.scene_offset() + scene_increment
                if new_track_offset >= 0 and new_scene_offset >= 0:
                    if new_track_offset < len(instance.tracks_to_use()) and new_scene_offset < len(scenes):
                        instances_covering_session += 1
                        if minimal_track_offset < 0:
                            minimal_track_offset = new_track_offset
                        else:
                            minimal_track_offset = min(minimal_track_offset, new_track_offset)
                        if minimal_scene_offset < 0:
                            minimal_scene_offset = new_scene_offset
                        else:
                            minimal_scene_offset = min(minimal_scene_offset, new_scene_offset)
                else:
                    found_negative_offset = True
                    break

            SessionComponent._minimal_track_offset = not found_negative_offset and instances_covering_session > 0 and minimal_track_offset
            SessionComponent._minimal_scene_offset = minimal_scene_offset
            for instance in SessionComponent._linked_session_instances:
                instance._change_offsets(track_increment, scene_increment)