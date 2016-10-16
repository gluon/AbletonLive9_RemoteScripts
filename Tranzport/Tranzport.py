#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Tranzport/Tranzport.py
import Live
from consts import *
from itertools import chain

class Tranzport:
    """ A simple script to enable control over Live with the Tranzport controller """

    def __init__(self, c_instance):
        self.__c_instance = c_instance
        self.__current_track = self.song().view.selected_track
        self.__last_message = ()
        self.song().view.add_selected_scene_listener(self.__on_selected_scene_changed)
        self.song().add_record_mode_listener(self.__set_record_mode_led)
        self.song().view.add_selected_track_listener(self.__on_selected_track_changed)
        self.song().add_loop_listener(self.__set_loop_led)
        self.song().add_tracks_listener(self.__on_tracks_changed)
        self.application().view.add_is_view_visible_listener('Session', self.__on_view_changed)
        for i in chain(self.song().tracks, self.song().return_tracks):
            i.add_solo_listener(self.__set_any_solo_led)

        if self.__current_track in self.song().visible_tracks and self.__current_track.can_be_armed:
            self.__current_track.add_arm_listener(self.__set_track_armed_led)
        if self.__current_track in chain(self.song().visible_tracks, self.song().return_tracks):
            self.__current_track.add_mute_listener(self.__set_track_muted_led)
            self.__current_track.add_solo_listener(self.__set_track_soloed_led)
            self.__current_track.add_name_listener(self.__current_track_name_changed)
        self.__sends_in_current_track = len(self.__current_track.mixer_device.sends)
        self.__current_send_index = 0
        self.__rewind_pressed = False
        self.__ffwd_pressed = False
        self.__shift_pressed = False
        self.__nexttrack_pressed = False
        self.__prevtrack_pressed = False
        self.__nextmarker_pressed = False
        self.__prevmarker_pressed = False
        self.__showing_page_list = False
        self.__selected_page = 0
        self.__spooling_factor = 1.0
        self.__timer_count = 0
        self.__display_line_one = ()
        self.__display_line_two = ()
        self.__last_line_one = ()
        self.__last_line_two = ()
        self.send_midi(TRANZ_NATIVE_MODE)
        self.__display_line_one = self.__translate_string('    Ableton Live    ')
        self.__display_line_two = self.__translate_string('                    ')

    def application(self):
        """returns a reference to the application that we are running in
        """
        return Live.Application.get_application()

    def song(self):
        """returns a reference to the Live song instance that we do control
        """
        return self.__c_instance.song()

    def disconnect(self):
        """Live -> Script
        Called right before we get disconnected from Live.
        """
        NOTE_OFF_STATUS = 128
        TRANZ_REC = 95
        TRANZ_ARM_TRACK = 0
        TRANZ_MUTE_TRACK = 16
        TRANZ_SOLO_TRACK = 8
        TRANZ_ANY_SOLO = 115
        TRANZ_LOOP = 86
        TRANZ_PUNCH = 120
        SYSEX_START = (240, 0, 1, 64, 16, 0)
        SYSEX_END = (247,)
        CLEAR_LINE = (32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32)
        LED_OFF = 0
        self.send_midi(SYSEX_START + (0,) + CLEAR_LINE + CLEAR_LINE + SYSEX_END)
        self.song().view.remove_selected_scene_listener(self.__on_selected_scene_changed)
        self.song().remove_record_mode_listener(self.__set_record_mode_led)
        self.song().view.remove_selected_track_listener(self.__on_selected_track_changed)
        self.song().remove_loop_listener(self.__set_loop_led)
        self.song().remove_tracks_listener(self.__on_tracks_changed)
        if Live:
            self.application().view.remove_is_view_visible_listener('Session', self.__on_view_changed)
        for i in chain(self.song().tracks, self.song().return_tracks):
            i.remove_solo_listener(self.__set_any_solo_led)

        self.send_midi((NOTE_OFF_STATUS, TRANZ_REC, LED_OFF))
        self.send_midi((NOTE_OFF_STATUS, TRANZ_ARM_TRACK, LED_OFF))
        self.send_midi((NOTE_OFF_STATUS, TRANZ_MUTE_TRACK, LED_OFF))
        self.send_midi((NOTE_OFF_STATUS, TRANZ_SOLO_TRACK, LED_OFF))
        self.send_midi((NOTE_OFF_STATUS, TRANZ_ANY_SOLO, LED_OFF))
        self.send_midi((NOTE_OFF_STATUS, TRANZ_LOOP, LED_OFF))
        self.send_midi((NOTE_OFF_STATUS, TRANZ_PUNCH, LED_OFF))
        if (list(self.song().visible_tracks) + list(self.song().return_tracks)).count(self.__current_track) > 0:
            self.__current_track.remove_mute_listener(self.__set_track_muted_led)
            self.__current_track.remove_solo_listener(self.__set_track_soloed_led)
            self.__current_track.remove_name_listener(self.__current_track_name_changed)
            if self.__current_track in self.song().visible_tracks and self.__current_track.can_be_armed:
                self.__current_track.remove_arm_listener(self.__set_track_armed_led)

    def suggest_input_port(self):
        """Live -> Script
        Live can ask the script for an input port name to find a suitable one.
        """
        return 'TranzPort'

    def suggest_output_port(self):
        """Live -> Script
        Live can ask the script for an output port name to find a suitable one.
        """
        return 'TranzPort'

    def can_lock_to_devices(self):
        return False

    def connect_script_instances(self, instanciated_scripts):
        """Called by the Application as soon as all scripts are initialized.
        You can connect yourself to other running scripts here, as we do it
        connect the extension modules (MackieControlXTs).
        """
        pass

    def request_rebuild_midi_map(self):
        """Script -> Live
        When the internal MIDI controller has changed in a way that you need to rebuild
        the MIDI mappings, request a rebuild by calling this function
        This is processed as a request, to be sure that its not too often called, because
        its time-critical.
        """
        self.__c_instance.request_rebuild_midi_map()

    def send_midi(self, midi_event_bytes):
        """Script -> Live
        Use this function to send MIDI events through Live to the _real_ MIDI devices
        that this script is assigned to.
        """
        self.__c_instance.send_midi(midi_event_bytes)

    def refresh_state(self):
        """Live -> Script
        Send out MIDI to completely update the attached MIDI controller.
        Will be called when requested by the user, after for example having reconnected
        the MIDI cables...
        """
        self.__last_line_one = ()
        self.__last_line_two = ()
        if self.__timer_count >= 20:
            self.__show_track_and_scene()
        self.__set_record_mode_led()
        self.__set_track_armed_led()
        self.__set_track_muted_led()
        self.__set_track_soloed_led()
        self.__set_any_solo_led()
        self.__set_loop_led()

    def build_midi_map(self, midi_map_handle):
        """Live -> Script
        Build DeviceParameter Mappings, that are processed in Audio time, or
        forward MIDI messages explicitly to our receive_midi_functions.
        Which means that when you are not forwarding MIDI, nor mapping parameters, you will
        never get any MIDI messages at all.
        """
        script_handle = self.__c_instance.handle()
        for i in range(NUM_NOTES):
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, 0, i)

        for channel in range(NUM_CHANNELS):
            for cc_no in range(NUM_CC_NO):
                Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, channel, cc_no)

    def update_display(self):
        """Live -> Script
        Aka on_timer. Called every 100 ms and should be used to update display relevant
        parts of the controller
        """
        if self.__timer_count < 21:
            self.__timer_count = self.__timer_count + 1
        if self.__timer_count == 10:
            self.__show_pos_and_tempo()
        if self.__timer_count == 20:
            self.__on_selected_track_changed()
        if self.__ffwd_pressed or self.__rewind_pressed:
            self.__spooling_factor = self.__spooling_factor + 0.2
            if self.__ffwd_pressed:
                self.song().jump_by(1 * self.__spooling_factor)
            if self.__rewind_pressed:
                self.song().jump_by(-1 * self.__spooling_factor)
        if not self.__display_line_one == self.__last_line_one:
            self.send_midi(SYSEX_START + (0,) + self.__display_line_one + SYSEX_END)
            self.__last_line_one = self.__display_line_one
        self.__show_selected_page()
        if not self.__display_line_two == self.__last_line_two:
            self.send_midi(SYSEX_START + (20,) + self.__display_line_two + SYSEX_END)
            self.__last_line_two = self.__display_line_two

    def receive_midi(self, midi_bytes):
        """Live -> Script
        MIDI messages are only received through this function, when explicitly
        forwarded in 'build_midi_map'.
        """
        if midi_bytes[0] & 240 == NOTE_ON_STATUS or midi_bytes[0] & 240 == NOTE_OFF_STATUS:
            note = midi_bytes[1]
            velocity = midi_bytes[2]
            if note == TRANZ_SHIFT:
                self.__shift_status_changed(velocity)
            elif note in TRANZ_TRANS_SECTION:
                self.__on_transport_button_pressed(note, velocity)
            elif note in TRANZ_TRACK_SECTION:
                self.__on_track_button_pressed(note, velocity)
            elif note in TRANZ_LOOP_SECTION:
                self.__on_loop_button_pressed(note, velocity)
            elif note in TRANZ_CUE_SECTION:
                self.__on_cue_button_pressed(note, velocity)
            elif note == TRANZ_UNDO:
                self.__on_undo_pressed(velocity)
        elif midi_bytes[0] & 240 == CC_STATUS:
            cc_no = midi_bytes[1]
            cc_value = midi_bytes[2]
            if midi_bytes[0] == 176 and cc_no == 60:
                self.__on_jogdial_changed(cc_value)

    def __on_transport_button_pressed(self, button, status):
        if button == TRANZ_PLAY:
            if status > 0:
                if not self.__shift_pressed:
                    self.song().is_playing = True
                else:
                    self.song().continue_playing()
        elif button == TRANZ_STOP:
            if status > 0:
                self.song().is_playing = False
        elif button == TRANZ_REC:
            if status > 0:
                if not self.__shift_pressed:
                    self.song().record_mode = not self.song().record_mode
        elif button == TRANZ_FFWD:
            if status > 0:
                if self.__shift_pressed:
                    self.song().jump_by(self.song().signature_denominator)
                else:
                    self.song().jump_by(1)
                    self.__ffwd_pressed = True
            else:
                self.__ffwd_pressed = False
                self.__spooling_factor = 1.0
        elif button == TRANZ_RWD:
            if status > 0:
                if self.__shift_pressed:
                    self.song().jump_by(-1 * self.song().signature_denominator)
                else:
                    self.song().jump_by(-1)
                    self.__rewind_pressed = True
            else:
                self.__rewind_pressed = False
                self.__spooling_factor = 1.0

    def __on_track_button_pressed(self, button, status):
        all_tracks = list(tuple(self.song().visible_tracks) + tuple(self.song().return_tracks) + (self.song().master_track,))
        index = all_tracks.index(self.__current_track)
        if button == TRANZ_PREV_TRACK:
            if status > 0:
                if self.__shift_pressed:
                    self.__handle_page_select(-1)
                else:
                    self.__prevtrack_pressed = True
                    if index > 0:
                        index = index - 1
                        self.song().view.selected_track = all_tracks[index]
            else:
                self.__prevtrack_pressed = False
        elif button == TRANZ_NEXT_TRACK:
            if status > 0:
                if self.__shift_pressed:
                    self.__handle_page_select(1)
                else:
                    self.__nexttrack_pressed = True
                    if index < len(all_tracks) - 1:
                        index = index + 1
                        self.song().view.selected_track = all_tracks[index]
            else:
                self.__nexttrack_pressed = False
        elif button == TRANZ_ARM_TRACK:
            if status > 0 and list(self.song().visible_tracks).count(self.__current_track) > 0:
                if self.song().exclusive_arm and not self.__shift_pressed or self.__shift_pressed and not self.song().exclusive_arm:
                    for i in self.song().tracks:
                        if i != self.__current_track and i.can_be_armed:
                            i.arm = False

                if self.__current_track and self.__current_track.can_be_armed:
                    self.__current_track.arm = not self.__current_track.arm
        elif button == TRANZ_MUTE_TRACK:
            if status > 0 and (list(self.song().visible_tracks) + list(self.song().return_tracks)).count(self.__current_track) > 0:
                if not self.__shift_pressed:
                    self.__current_track.mute = not self.__current_track.mute
                else:
                    for i in chain(self.song().tracks, self.song().return_tracks):
                        i.mute = False

        elif button == TRANZ_SOLO_TRACK:
            if status > 0 and (list(self.song().visible_tracks) + list(self.song().return_tracks)).count(self.__current_track) > 0:
                if self.song().exclusive_solo and not self.__shift_pressed or self.__shift_pressed and not self.song().exclusive_solo:
                    for i in chain(self.song().tracks, self.song().return_tracks):
                        if i.solo and not i == self.__current_track:
                            i.solo = False

            for i in chain(self.song().tracks, self.song().return_tracks):
                self.__current_track.solo = not self.__current_track.solo

    def __on_loop_button_pressed(self, button, status):
        current_pos = self.song().current_song_time
        loop_start = self.song().loop_start
        loop_end = loop_start + self.song().loop_length
        if status > 0:
            if button == TRANZ_LOOP:
                if not self.__shift_pressed:
                    self.song().loop = not self.song().loop
                elif self.application().view.is_view_visible('Session'):
                    self.application().view.show_view('Arranger')
                elif self.application().view.is_view_visible('Arranger'):
                    self.application().view.show_view('Session')
            elif button == TRANZ_PUNCH_IN:
                if not self.__shift_pressed:
                    self.song().punch_in = not self.song().punch_in
                elif current_pos < loop_end:
                    self.song().loop_start = current_pos
                    self.song().loop_length = loop_end - current_pos
            elif button == TRANZ_PUNCH_OUT:
                if not self.__shift_pressed:
                    self.song().punch_out = not self.song().punch_out
                elif current_pos > loop_start:
                    self.song().loop_length = current_pos - loop_start
            elif button == TRANZ_PUNCH:
                if self.application().view.is_view_visible('Session'):
                    current_slot = self.song().view.highlighted_clip_slot
                    if not self.__shift_pressed and list(self.song().visible_tracks).count(self.__current_track) > 0:
                        current_slot.fire()
                    else:
                        self.song().view.selected_scene.fire_as_selected()

    def __on_cue_button_pressed(self, button, status):
        if status > 0:
            if button == TRANZ_PREV_CUE:
                if not self.__shift_pressed:
                    self.__prevmarker_pressed = True
                    if self.song().can_jump_to_prev_cue:
                        self.song().jump_to_prev_cue()
                else:
                    self.song().current_song_time = 0
            elif button == TRANZ_ADD_CUE:
                if not self.__shift_pressed:
                    self.song().set_or_delete_cue()
            elif button == TRANZ_NEXT_CUE:
                if not self.__shift_pressed:
                    self.__nextmarker_pressed = True
                    if self.song().can_jump_to_next_cue:
                        self.song().jump_to_next_cue()
                else:
                    self.song().current_song_time = self.song().last_event_time
        elif status == 0:
            if button == TRANZ_PREV_CUE:
                self.__prevmarker_pressed = False
            elif button == TRANZ_NEXT_CUE:
                self.__nextmarker_pressed = False

    def __on_jogdial_changed(self, value):
        neg_value = value - 64
        all_tracks = list(tuple(self.song().visible_tracks) + tuple(self.song().return_tracks) + (self.song().master_track,))
        index = all_tracks.index(self.__current_track)
        if value in range(1, 64):
            if not self.__shift_pressed:
                if self.__prevtrack_pressed or self.__nexttrack_pressed:
                    if index < len(all_tracks) - 1:
                        index = index + 1
                        self.song().view.selected_track = all_tracks[index]
                elif self.__prevmarker_pressed or self.__nextmarker_pressed:
                    if self.song().can_jump_to_next_cue:
                        self.song().jump_to_next_cue()
                elif self.__selected_page == 0:
                    if self.application().view.is_view_visible('Session'):
                        index = list(self.song().scenes).index(self.song().view.selected_scene)
                        if index < len(self.song().scenes) - 1:
                            index = index + 1
                            self.song().view.selected_scene = self.song().scenes[index]
                    else:
                        self.song().jump_by(value)
                elif self.__selected_page == 1:
                    if self.__current_track.mixer_device.volume.value <= self.__current_track.mixer_device.volume.max - 0.01 * value:
                        self.__current_track.mixer_device.volume.value = self.__current_track.mixer_device.volume.value + 0.01 * value
                    else:
                        self.__current_track.mixer_device.volume.value = self.__current_track.mixer_device.volume.max
                elif self.__selected_page == 2:
                    self.song().loop_start = self.song().loop_start + value
                elif self.__selected_page == 3:
                    if self.__current_track.mixer_device.sends[self.__current_send_index].value <= self.__current_track.mixer_device.sends[self.__current_send_index].max - 0.01 * value:
                        self.__current_track.mixer_device.sends[self.__current_send_index].value = self.__current_track.mixer_device.sends[self.__current_send_index].value + 0.01 * value
                    else:
                        self.__current_track.mixer_device.sends[self.__current_send_index].value = self.__current_track.mixer_device.sends[self.__current_send_index].max
            elif self.__selected_page == 0:
                self.song().tempo = self.song().tempo + 0.1 * value
            elif self.__selected_page == 1:
                if self.__current_track.mixer_device.panning.value <= self.__current_track.mixer_device.panning.max - 0.02 * value:
                    self.__current_track.mixer_device.panning.value = self.__current_track.mixer_device.panning.value + 0.02 * value
                else:
                    self.__current_track.mixer_device.panning.value = self.__current_track.mixer_device.panning.max
            elif self.__selected_page == 2:
                self.song().loop_length = self.song().loop_length + value
            elif self.__selected_page == 3:
                if self.__current_send_index < len(self.__current_track.mixer_device.sends) - 1:
                    self.__current_send_index = self.__current_send_index + 1
                else:
                    self.__current_send_index = len(self.__current_track.mixer_device.sends) - 1
        elif value in range(65, 128):
            if not self.__shift_pressed:
                if self.__prevtrack_pressed or self.__nexttrack_pressed:
                    if index > 0:
                        index = index - 1
                        self.song().view.selected_track = all_tracks[index]
                elif self.__prevmarker_pressed or self.__nextmarker_pressed:
                    if self.song().can_jump_to_prev_cue:
                        self.song().jump_to_prev_cue()
                elif self.__selected_page == 0:
                    if self.application().view.is_view_visible('Session'):
                        index = list(self.song().scenes).index(self.song().view.selected_scene)
                        if index > 0:
                            index = index - 1
                        self.song().view.selected_scene = self.song().scenes[index]
                    else:
                        self.song().jump_by(-1 * neg_value)
                elif self.__selected_page == 1:
                    if self.__current_track.mixer_device.volume.value >= self.__current_track.mixer_device.volume.min + 0.01 * neg_value:
                        self.__current_track.mixer_device.volume.value = self.__current_track.mixer_device.volume.value - 0.01 * neg_value
                    else:
                        self.__current_track.mixer_device.volume.value = self.__current_track.mixer_device.volume.min
                elif self.__selected_page == 2:
                    if self.song().loop_start >= neg_value:
                        self.song().loop_start = self.song().loop_start - neg_value
                elif self.__selected_page == 3:
                    if self.__current_track.mixer_device.sends[self.__current_send_index].value >= self.__current_track.mixer_device.sends[self.__current_send_index].min + 0.01 * neg_value:
                        self.__current_track.mixer_device.sends[self.__current_send_index].value = self.__current_track.mixer_device.sends[self.__current_send_index].value - 0.01 * neg_value
                    else:
                        self.__current_track.mixer_device.sends[self.__current_send_index].value = self.__current_track.mixer_device.sends[self.__current_send_index].min
            elif self.__selected_page == 0:
                self.song().tempo = self.song().tempo - 0.1 * neg_value
            elif self.__selected_page == 1:
                if self.__current_track.mixer_device.panning.value >= self.__current_track.mixer_device.panning.min + 0.02 * neg_value:
                    self.__current_track.mixer_device.panning.value = self.__current_track.mixer_device.panning.value - 0.02 * neg_value
                else:
                    self.__current_track.mixer_device.panning.value = self.__current_track.mixer_device.panning.min
            elif self.__selected_page == 2:
                if self.song().loop_length > neg_value:
                    self.song().loop_length = self.song().loop_length - neg_value
            elif self.__selected_page == 3:
                if self.__current_send_index > 0:
                    self.__current_send_index = self.__current_send_index - 1
                else:
                    self.__current_send_index = 0

    def __on_undo_pressed(self, status):
        if status > 0:
            if not self.__shift_pressed:
                if self.song().can_undo:
                    self.song().undo()
            elif self.song().can_redo:
                self.song().redo()

    def __on_selected_scene_changed(self):
        if self.application().view.is_view_visible('Session'):
            self.__show_track_and_scene()

    def __on_current_song_time_changed(self):
        if self.__selected_page == 0:
            self.__show_selected_page()

    def __on_current_song_tempo_changed(self):
        if self.__selected_page == 0:
            self.__show_selected_page()

    def __on_current_track_volume_changed(self):
        if self.__selected_page == 1:
            self.__show_selected_page()

    def __on_current_track_panning_changed(self):
        if self.__selected_page == 1:
            self.__show_selected_page()

    def __on_song_loop_start_changed(self):
        if self.__selected_page == 2:
            self.__show_selected_page()

    def __on_song_loop_length_changed(self):
        if self.__selected_page == 2:
            self.__show_selected_page()

    def __on_view_changed(self):
        self.__show_track_and_scene()
        self.__show_selected_page()

    def __on_tracks_changed(self):
        for i in chain(self.song().tracks, self.song().return_tracks):
            if not i.solo_has_listener(self.__set_any_solo_led):
                i.add_solo_listener(self.__set_any_solo_led)

    def __show_track_and_scene(self):
        line = ()
        if self.application().view.is_view_visible('Session'):
            line = self.__translate_string(self.__bring_string_to_length(self.__current_track.name, 11))
            line = line + self.__translate_string('  Scene%2d' % (list(self.song().scenes).index(self.song().view.selected_scene) + 1))
        elif self.application().view.is_view_visible('Arranger'):
            line = self.__translate_string(self.__bring_string_to_length(self.__current_track.name, 20))
        self.__display_line_one = line

    def __show_selected_page(self):
        if not self.__showing_page_list and self.__timer_count > 20:
            index = self.__selected_page
            if index == 0:
                self.__show_pos_and_tempo()
            elif index == 1:
                self.__show_vol_and_pan()
            elif index == 2:
                self.__show_loop_settings()
            elif index == 3:
                self.__show_send_settings()
        elif self.__showing_page_list:
            self.__show_page_select()

    def __show_pos_and_tempo(self):
        beat_time = self.song().get_current_beats_song_time()
        position_str = ()
        if self.application().view.is_view_visible('Session'):
            current_slot = self.song().view.highlighted_clip_slot
            position_str = self.__translate_string('[No Clip]  ')
            if current_slot:
                if current_slot.clip:
                    if current_slot.clip.name == '':
                        position_str = self.__translate_string('[No Name]  ')
                    else:
                        position_str = self.__translate_string(self.__bring_string_to_length(current_slot.clip.name, 9)) + self.__translate_string('  ')
        else:
            position_str = self.__translate_string(str('%3d.' % beat_time.bars)) + self.__translate_string(str('%02d.' % beat_time.beats)) + self.__translate_string(str('%02d  ' % beat_time.ticks))
        tempo_str = self.__translate_string('%3.2fbpm' % self.song().tempo)
        if len(tempo_str) == 8:
            tempo_str = (32,) + tempo_str
        self.__display_line_two = position_str + tempo_str

    def __show_vol_and_pan(self):
        volume = self.__current_track.mixer_device.volume
        panning = self.__current_track.mixer_device.panning
        if self.__current_track.has_audio_output:
            self.__display_line_two = self.__translate_string(self.__string_from_number_with_length(volume, 9)) + self.__translate_string('       ') + self.__translate_string(self.__string_from_number_with_length(panning, 3))
        else:
            self.__display_line_two = self.__translate_string('  No Audio Output   ')

    def __show_loop_settings(self):
        start_time = self.song().get_beats_loop_start()
        length_time = self.song().get_beats_loop_length()
        self.__display_line_two = self.__translate_string('S%3d.' % start_time.bars) + self.__translate_string('%02d.' % start_time.beats) + self.__translate_string('%02d ' % start_time.ticks) + self.__translate_string('L%2d.' % length_time.bars) + self.__translate_string('%02d.' % length_time.beats) + self.__translate_string('%02d' % length_time.ticks)

    def __show_send_settings(self):
        result = ()
        if len(self.__current_track.mixer_device.sends) > 0 and self.__current_track.has_audio_output:
            if self.__current_send_index >= len(self.__current_track.mixer_device.sends):
                self.__current_send_index = len(self.__current_track.mixer_device.sends) - 1
            elif self.__current_send_index < 0:
                self.__current_send_index = 0
            current_send = self.__current_track.mixer_device.sends[self.__current_send_index]
            result = self.__translate_string(self.__string_from_number_with_length(current_send, 8)) + self.__translate_string('  in  ') + self.__translate_string(current_send.name)
        else:
            result = self.__translate_string(' No Sends Available ')
        self.__display_line_two = result

    def __show_page_select(self):
        index = self.__selected_page
        if self.application().view.is_view_visible('Session') or index > 0:
            index = index + 1
        pages_list = ('<',) + PAGES_NAMES[index] + ('>',)
        position = 10 - len(pages_list) / 2
        message = ()
        for i in range(position):
            message = message + (32,)

        message = message + self.__translate_string(pages_list)
        for i in range(position):
            message = message + (32,)

        self.__display_line_two = message

    def __set_record_mode_led(self):
        if self.song().record_mode:
            self.send_midi((NOTE_ON_STATUS, TRANZ_REC, LED_ON))
        else:
            self.send_midi((NOTE_ON_STATUS, TRANZ_REC, LED_OFF))

    def __set_track_armed_led(self):
        status = LED_OFF
        if list(self.song().visible_tracks).count(self.__current_track) > 0:
            if self.song().view.selected_track.arm:
                status = LED_ON
        self.send_midi((NOTE_ON_STATUS, TRANZ_ARM_TRACK, status))

    def is_track_visible(self, track):
        return (list(self.song().visible_tracks) + list(self.song().return_tracks)).count(track) > 0

    def __set_track_muted_led(self):
        status = LED_OFF
        if self.is_track_visible(self.__current_track):
            if self.song().view.selected_track.mute:
                status = LED_ON
        self.send_midi((NOTE_ON_STATUS, TRANZ_MUTE_TRACK, status))

    def __set_track_soloed_led(self):
        status = LED_OFF
        if self.is_track_visible(self.__current_track):
            if self.song().view.selected_track.solo:
                status = LED_ON
        self.send_midi((NOTE_ON_STATUS, TRANZ_SOLO_TRACK, status))

    def __set_any_solo_led(self):
        status = LED_OFF
        for i in chain(self.song().tracks, self.song().return_tracks):
            if i.solo:
                status = LED_ON
                break

        self.send_midi((NOTE_ON_STATUS, TRANZ_ANY_SOLO, status))

    def __set_loop_led(self):
        status = LED_OFF
        if self.song().loop:
            status = LED_ON
        self.send_midi((NOTE_ON_STATUS, TRANZ_LOOP, status))

    def __current_track_name_changed(self):
        self.__show_track_and_scene()

    def __on_selected_track_changed(self):
        if self.is_track_visible(self.__current_track):
            self.__current_track.remove_mute_listener(self.__set_track_muted_led)
            self.__current_track.remove_solo_listener(self.__set_track_soloed_led)
            self.__current_track.remove_name_listener(self.__current_track_name_changed)
            if self.__current_track in self.song().tracks and self.__current_track.can_be_armed:
                self.__current_track.remove_arm_listener(self.__set_track_armed_led)
        self.__current_track = self.song().view.selected_track
        if (list(self.song().visible_tracks) + list(self.song().return_tracks)).count(self.__current_track) > 0:
            self.__current_track.add_solo_listener(self.__set_track_soloed_led)
            self.__current_track.add_mute_listener(self.__set_track_muted_led)
            self.__current_track.add_name_listener(self.__current_track_name_changed)
            if self.__current_track in self.song().visible_tracks and self.__current_track.can_be_armed:
                self.__current_track.add_arm_listener(self.__set_track_armed_led)
        self.__sends_in_current_track = len(self.__current_track.mixer_device.sends)
        self.__current_send_index = 0
        self.refresh_state()

    def __handle_page_select(self, direction):
        if self.__showing_page_list:
            self.__selected_page = self.__selected_page + direction
            if self.__selected_page >= NUM_PAGES:
                self.__selected_page = 0
            elif self.__selected_page < 0:
                self.__selected_page = NUM_PAGES - 1
        else:
            self.__showing_page_list = True
        self.__show_page_select()

    def __shift_status_changed(self, status):
        if status == 0:
            self.__shift_pressed = False
            self.__showing_page_list = False
        else:
            self.__shift_pressed = True
        self.__show_selected_page()

    def __translate_string(self, text):
        result = ()
        length = len(text)
        for i in range(0, length):
            char_code = self.__character_code(text[i])
            if char_code < 0:
                char_code = 32
            result = result + (char_code,)

        return result

    def __character_code(self, character):
        result = -1
        try:
            result = TRANZ_DICT[character]
        finally:
            return result

    def __bring_string_to_length(self, text, length):
        result = ()
        string_length = len(text)
        for i in range(length):
            if i < string_length:
                if i == length - 1:
                    result = result + ('>',)
                else:
                    result = result + (text[i],)
            else:
                result = result + (' ',)

        return result

    def __string_from_number_with_length(self, number, length):
        result = ()
        text = str(number)
        for i in range(len(text)):
            result = result + (text[i],)

        if len(result) < length:
            for i in range(length - len(result)):
                result = (' ',) + result

        return result