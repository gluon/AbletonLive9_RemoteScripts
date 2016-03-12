#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/Transport.py
from MackieControlComponent import *

class Transport(MackieControlComponent):
    """Representing the transport section of the Mackie Control: """

    def __init__(self, main_script):
        MackieControlComponent.__init__(self, main_script)
        self.__forward_button_down = False
        self.____rewind_button_down = False
        self.__zoom_button_down = False
        self.__scrub_button_down = False
        self.__cursor_left_is_down = False
        self.__cursor_right_is_down = False
        self.__cursor_up_is_down = False
        self.__cursor_down_is_down = False
        self.__cursor_repeat_delay = 0
        self.__transport_repeat_delay = 0
        self.____fast_forward_counter = 0
        self.__fast___rewind_counter = 0
        self.__jog_step_count_forward = 0
        self.__jog_step_count_backwards = 0
        self.__last_focussed_clip_play_state = CLIP_STATE_INVALID
        self.song().add_record_mode_listener(self.__update_record_button_led)
        self.song().add_is_playing_listener(self.__update_play_button_led)
        self.song().add_loop_listener(self.__update_loop_button_led)
        self.song().add_punch_out_listener(self.__update_punch_out_button_led)
        self.song().add_punch_in_listener(self.__update_punch_in_button_led)
        self.song().add_can_jump_to_prev_cue_listener(self.__update_prev_cue_button_led)
        self.song().add_can_jump_to_next_cue_listener(self.__update_next_cue_button_led)
        self.application().view.add_is_view_visible_listener('Session', self.__on_session_is_visible_changed)
        self.refresh_state()

    def destroy(self):
        self.song().remove_record_mode_listener(self.__update_record_button_led)
        self.song().remove_is_playing_listener(self.__update_play_button_led)
        self.song().remove_loop_listener(self.__update_loop_button_led)
        self.song().remove_punch_out_listener(self.__update_punch_out_button_led)
        self.song().remove_punch_in_listener(self.__update_punch_in_button_led)
        self.song().remove_can_jump_to_prev_cue_listener(self.__update_prev_cue_button_led)
        self.song().remove_can_jump_to_next_cue_listener(self.__update_next_cue_button_led)
        self.application().view.remove_is_view_visible_listener('Session', self.__on_session_is_visible_changed)
        for note in transport_control_switch_ids:
            self.send_midi((NOTE_ON_STATUS, note, BUTTON_STATE_OFF))

        for note in jog_wheel_switch_ids:
            self.send_midi((NOTE_ON_STATUS, note, BUTTON_STATE_OFF))

        for note in marker_control_switch_ids:
            self.send_midi((NOTE_ON_STATUS, note, BUTTON_STATE_OFF))

        MackieControlComponent.destroy(self)

    def refresh_state(self):
        self.__update_play_button_led()
        self.__update_record_button_led()
        self.__update_prev_cue_button_led()
        self.__update_next_cue_button_led()
        self.__update_loop_button_led()
        self.__update_punch_in_button_led()
        self.__update_punch_out_button_led()
        self.__forward_button_down = False
        self.____rewind_button_down = False
        self.__zoom_button_down = False
        self.__scrub_button_down = False
        self.__cursor_left_is_down = False
        self.__cursor_right_is_down = False
        self.__cursor_up_is_down = False
        self.__cursor_down_is_down = False
        self.__cursor_repeat_delay = 0
        self.__transport_repeat_delay = 0
        self.____fast_forward_counter = 0
        self.__fast___rewind_counter = 0
        self.__jog_step_count_forward = 0
        self.__jog_step_count_backwards = 0
        self.__last_focussed_clip_play_state = CLIP_STATE_INVALID
        self.__update_forward_rewind_leds()
        self.__update_zoom_button_led()
        self.__update_scrub_button_led()

    def session_is_visible(self):
        return self.application().view.is_view_visible('Session')

    def selected_clip_slot(self):
        return self.song().view.highlighted_clip_slot

    def on_update_display_timer(self):
        if self.__transport_repeat_delay > 2:
            if self.alt_is_pressed():
                base_acceleration = 1
            else:
                base_acceleration = self.song().signature_numerator
            if self.song().is_playing:
                base_acceleration *= 4
            if not (self.__forward_button_down and self.____rewind_button_down):
                if self.__forward_button_down:
                    self.____fast_forward_counter += 1
                    self.__fast___rewind_counter -= 4
                    if not self.alt_is_pressed():
                        self.__fast_forward(base_acceleration + max(1, self.____fast_forward_counter / 4))
                    else:
                        self.__fast_forward(base_acceleration)
                if self.____rewind_button_down:
                    self.__fast___rewind_counter += 1
                    self.____fast_forward_counter -= 4
                    if not self.alt_is_pressed():
                        self.__rewind(base_acceleration + max(1, self.__fast___rewind_counter / 4))
                    else:
                        self.__rewind(base_acceleration)
        else:
            self.__transport_repeat_delay += 1
        if self.__cursor_repeat_delay > 2:
            if self.__cursor_left_is_down:
                self.__on_cursor_left_pressed()
            if self.__cursor_right_is_down:
                self.__on_cursor_right_pressed()
            if self.__cursor_up_is_down:
                self.__on_cursor_up_pressed()
            if self.__cursor_down_is_down:
                self.__on_cursor_down_pressed()
        else:
            self.__cursor_repeat_delay += 1
        if self.session_is_visible():
            self.__update_zoom_led_in_session()

    def handle_marker_switch_ids(self, switch_id, value):
        if switch_id == SID_MARKER_FROM_PREV:
            if value == BUTTON_PRESSED:
                self.__jump_to_prev_cue()
        elif switch_id == SID_MARKER_FROM_NEXT:
            if value == BUTTON_PRESSED:
                self.__jump_to_next_cue()
        elif switch_id == SID_MARKER_LOOP:
            if value == BUTTON_PRESSED:
                self.__toggle_loop()
        elif switch_id == SID_MARKER_PI:
            if value == BUTTON_PRESSED:
                if self.control_is_pressed():
                    self.__set_loopstart_from_cur_position()
                else:
                    self.__toggle_punch_in()
        elif switch_id == SID_MARKER_PO:
            if value == BUTTON_PRESSED:
                if self.control_is_pressed():
                    self.__set_loopend_from_cur_position()
                else:
                    self.__toggle_punch_out()
        elif switch_id == SID_MARKER_HOME:
            if value == BUTTON_PRESSED:
                self.__goto_home()
        elif switch_id == SID_MARKER_END:
            if value == BUTTON_PRESSED:
                self.__goto_end()

    def handle_transport_switch_ids(self, switch_id, value):
        if switch_id == SID_TRANSPORT_REWIND:
            if value == BUTTON_PRESSED:
                self.__rewind()
                self.____rewind_button_down = True
            elif value == BUTTON_RELEASED:
                self.____rewind_button_down = False
                self.__fast___rewind_counter = 0
            self.__update_forward_rewind_leds()
        elif switch_id == SID_TRANSPORT_FAST_FORWARD:
            if value == BUTTON_PRESSED:
                self.__fast_forward()
                self.__forward_button_down = True
            elif value == BUTTON_RELEASED:
                self.__forward_button_down = False
                self.____fast_forward_counter = 0
            self.__update_forward_rewind_leds()
        elif switch_id == SID_TRANSPORT_STOP:
            if value == BUTTON_PRESSED:
                self.__stop_song()
        elif switch_id == SID_TRANSPORT_PLAY:
            if value == BUTTON_PRESSED:
                self.__start_song()
        elif switch_id == SID_TRANSPORT_RECORD:
            if value == BUTTON_PRESSED:
                self.__toggle_record()

    def handle_jog_wheel_rotation(self, value):
        backwards = value >= 64
        if self.control_is_pressed():
            if self.alt_is_pressed():
                step = 0.1
            else:
                step = 1.0
            if backwards:
                amount = -(value - 64)
            else:
                amount = value
            tempo = max(20, min(999, self.song().tempo + amount * step))
            self.song().tempo = tempo
        elif self.session_is_visible():
            num_steps_per_session_scroll = 4
            if backwards:
                self.__jog_step_count_backwards += 1
                if self.__jog_step_count_backwards >= num_steps_per_session_scroll:
                    self.__jog_step_count_backwards = 0
                    step = -1
                else:
                    step = 0
            else:
                self.__jog_step_count_forward += 1
                if self.__jog_step_count_forward >= num_steps_per_session_scroll:
                    self.__jog_step_count_forward = 0
                    step = 1
                else:
                    step = 0
            if step:
                new_index = list(self.song().scenes).index(self.song().view.selected_scene) + step
                new_index = min(len(self.song().scenes) - 1, max(0, new_index))
                self.song().view.selected_scene = self.song().scenes[new_index]
        else:
            if backwards:
                step = max(1.0, (value - 64) / 2.0)
            else:
                step = max(1.0, value / 2.0)
            if self.song().is_playing:
                step *= 4.0
            if self.alt_is_pressed():
                step /= 4.0
            if self.__scrub_button_down:
                if backwards:
                    self.song().scrub_by(-step)
                else:
                    self.song().scrub_by(step)
            elif backwards:
                self.song().jump_by(-step)
            else:
                self.song().jump_by(step)

    def handle_jog_wheel_switch_ids(self, switch_id, value):
        if switch_id == SID_JOG_CURSOR_UP:
            if value == BUTTON_PRESSED:
                self.__cursor_up_is_down = True
                self.__cursor_repeat_delay = 0
                self.__on_cursor_up_pressed()
            elif value == BUTTON_RELEASED:
                self.__cursor_up_is_down = False
        elif switch_id == SID_JOG_CURSOR_DOWN:
            if value == BUTTON_PRESSED:
                self.__cursor_down_is_down = True
                self.__cursor_repeat_delay = 0
                self.__on_cursor_down_pressed()
            elif value == BUTTON_RELEASED:
                self.__cursor_down_is_down = False
        elif switch_id == SID_JOG_CURSOR_LEFT:
            if value == BUTTON_PRESSED:
                self.__cursor_left_is_down = True
                self.__cursor_repeat_delay = 0
                self.__on_cursor_left_pressed()
            elif value == BUTTON_RELEASED:
                self.__cursor_left_is_down = False
        elif switch_id == SID_JOG_CURSOR_RIGHT:
            if value == BUTTON_PRESSED:
                self.__cursor_right_is_down = True
                self.__cursor_repeat_delay = 0
                self.__on_cursor_right_pressed()
            elif value == BUTTON_RELEASED:
                self.__cursor_right_is_down = False
        elif switch_id == SID_JOG_ZOOM:
            if value == BUTTON_PRESSED:
                if self.session_is_visible():
                    if self.selected_clip_slot():
                        if self.alt_is_pressed():
                            self.selected_clip_slot().has_stop_button = not self.selected_clip_slot().has_stop_button
                        elif self.option_is_pressed():
                            self.selected_clip_slot().stop()
                        else:
                            self.selected_clip_slot().fire()
                else:
                    self.__zoom_button_down = not self.__zoom_button_down
                    self.__update_zoom_button_led()
        elif switch_id == SID_JOG_SCRUB:
            if value == BUTTON_PRESSED:
                if self.session_is_visible():
                    if self.option_is_pressed():
                        self.song().stop_all_clips()
                    else:
                        self.song().view.selected_scene.fire_as_selected()
                else:
                    self.__scrub_button_down = not self.__scrub_button_down
                    self.__update_scrub_button_led()

    def __on_cursor_up_pressed(self):
        nav = Live.Application.Application.View.NavDirection
        if self.__zoom_button_down:
            self.application().view.zoom_view(nav.up, '', self.alt_is_pressed())
        else:
            self.application().view.scroll_view(nav.up, '', self.alt_is_pressed())

    def __on_cursor_down_pressed(self):
        nav = Live.Application.Application.View.NavDirection
        if self.__zoom_button_down:
            self.application().view.zoom_view(nav.down, '', self.alt_is_pressed())
        else:
            self.application().view.scroll_view(nav.down, '', self.alt_is_pressed())

    def __on_cursor_left_pressed(self):
        nav = Live.Application.Application.View.NavDirection
        if self.__zoom_button_down:
            self.application().view.zoom_view(nav.left, '', self.alt_is_pressed())
        else:
            self.application().view.scroll_view(nav.left, '', self.alt_is_pressed())

    def __on_cursor_right_pressed(self):
        nav = Live.Application.Application.View.NavDirection
        if self.__zoom_button_down:
            self.application().view.zoom_view(nav.right, '', self.alt_is_pressed())
        else:
            self.application().view.scroll_view(nav.right, '', self.alt_is_pressed())

    def __toggle_record(self):
        self.song().record_mode = not self.song().record_mode

    def __rewind(self, acceleration = 1):
        beats = acceleration
        self.song().jump_by(-beats)

    def __fast_forward(self, acceleration = 1):
        beats = acceleration
        self.song().jump_by(beats)

    def __stop_song(self):
        self.song().stop_playing()

    def __start_song(self):
        if self.shift_is_pressed():
            if not self.song().is_playing:
                self.song().continue_playing()
            else:
                self.song().stop_playing()
        elif self.control_is_pressed():
            self.song().play_selection()
        else:
            self.song().start_playing()

    def __toggle_follow(self):
        self.song().follow_song = not self.song().follow_song

    def __toggle_loop(self):
        self.song().loop = not self.song().loop

    def __toggle_punch_in(self):
        self.song().punch_in = not self.song().punch_in

    def __toggle_punch_out(self):
        self.song().punch_out = not self.song().punch_out

    def __jump_to_prev_cue(self):
        self.song().jump_to_prev_cue()

    def __jump_to_next_cue(self):
        self.song().jump_to_next_cue()

    def __set_loopstart_from_cur_position(self):
        if self.song().current_song_time < self.song().loop_start + self.song().loop_length:
            old_loop_start = self.song().loop_start
            self.song().loop_start = self.song().current_song_time
            self.song().loop_length += old_loop_start - self.song().loop_start

    def __set_loopend_from_cur_position(self):
        if self.song().current_song_time > self.song().loop_start:
            self.song().loop_length = self.song().current_song_time - self.song().loop_start

    def __goto_home(self):
        self.song().current_song_time = 0

    def __goto_end(self):
        self.song().current_song_time = self.song().last_event_time

    def __on_session_is_visible_changed(self):
        if not self.session_is_visible():
            self.__update_zoom_button_led()

    def __update_zoom_led_in_session(self):
        if self.session_is_visible():
            clip_slot = self.selected_clip_slot()
            if clip_slot and clip_slot.clip:
                if clip_slot.clip.is_triggered:
                    state = CLIP_TRIGGERED
                elif clip_slot.clip.is_playing:
                    state = CLIP_PLAYING
                else:
                    state = CLIP_STOPPED
            else:
                state = CLIP_STOPPED
            if state != self.__last_focussed_clip_play_state:
                self.__last_focussed_clip_play_state = state
                if state == CLIP_PLAYING:
                    self.send_midi((NOTE_ON_STATUS, SID_JOG_ZOOM, BUTTON_STATE_ON))
                elif state == CLIP_TRIGGERED:
                    self.send_midi((NOTE_ON_STATUS, SID_JOG_ZOOM, BUTTON_STATE_BLINKING))
                else:
                    self.send_midi((NOTE_ON_STATUS, SID_JOG_ZOOM, BUTTON_STATE_OFF))

    def __update_forward_rewind_leds(self):
        if self.__forward_button_down:
            self.send_midi((NOTE_ON_STATUS, SID_TRANSPORT_FAST_FORWARD, BUTTON_STATE_ON))
            self.__transport_repeat_delay = 0
        else:
            self.send_midi((NOTE_ON_STATUS, SID_TRANSPORT_FAST_FORWARD, BUTTON_STATE_OFF))
        if self.____rewind_button_down:
            self.send_midi((NOTE_ON_STATUS, SID_TRANSPORT_REWIND, BUTTON_STATE_ON))
            self.__transport_repeat_delay = 0
        else:
            self.send_midi((NOTE_ON_STATUS, SID_TRANSPORT_REWIND, BUTTON_STATE_OFF))

    def __update_zoom_button_led(self):
        if self.__zoom_button_down:
            self.send_midi((NOTE_ON_STATUS, SID_JOG_ZOOM, BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS, SID_JOG_ZOOM, BUTTON_STATE_OFF))

    def __update_scrub_button_led(self):
        if self.__scrub_button_down:
            self.send_midi((NOTE_ON_STATUS, SID_JOG_SCRUB, BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS, SID_JOG_SCRUB, BUTTON_STATE_OFF))

    def __update_play_button_led(self):
        if self.song().is_playing:
            self.send_midi((NOTE_ON_STATUS, SID_TRANSPORT_PLAY, BUTTON_STATE_ON))
            self.send_midi((NOTE_ON_STATUS, SID_TRANSPORT_STOP, BUTTON_STATE_OFF))
        else:
            self.send_midi((NOTE_ON_STATUS, SID_TRANSPORT_PLAY, BUTTON_STATE_OFF))
            self.send_midi((NOTE_ON_STATUS, SID_TRANSPORT_STOP, BUTTON_STATE_ON))

    def __update_record_button_led(self):
        if self.song().record_mode:
            self.send_midi((NOTE_ON_STATUS, SID_TRANSPORT_RECORD, BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS, SID_TRANSPORT_RECORD, BUTTON_STATE_OFF))

    def __update_follow_song_button_led(self):
        if self.song().follow_song:
            self.send_midi((NOTE_ON_STATUS, SID_MARKER_FROM_PREV, BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS, SID_MARKER_FROM_PREV, BUTTON_STATE_OFF))

    def __update_prev_cue_button_led(self):
        if self.song().can_jump_to_prev_cue:
            self.send_midi((NOTE_ON_STATUS, SID_MARKER_FROM_PREV, BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS, SID_MARKER_FROM_PREV, BUTTON_STATE_OFF))

    def __update_next_cue_button_led(self):
        if self.song().can_jump_to_next_cue:
            self.send_midi((NOTE_ON_STATUS, SID_MARKER_FROM_NEXT, BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS, SID_MARKER_FROM_NEXT, BUTTON_STATE_OFF))

    def __update_loop_button_led(self):
        if self.song().loop:
            self.send_midi((NOTE_ON_STATUS, SID_MARKER_LOOP, BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS, SID_MARKER_LOOP, BUTTON_STATE_OFF))

    def __update_punch_in_button_led(self):
        if self.song().punch_in:
            self.send_midi((NOTE_ON_STATUS, SID_MARKER_PI, BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS, SID_MARKER_PI, BUTTON_STATE_OFF))

    def __update_punch_out_button_led(self):
        if self.song().punch_out:
            self.send_midi((NOTE_ON_STATUS, SID_MARKER_PO, BUTTON_STATE_ON))
        else:
            self.send_midi((NOTE_ON_STATUS, SID_MARKER_PO, BUTTON_STATE_OFF))