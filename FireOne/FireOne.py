#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/FireOne/FireOne.py
import Live
import MidiRemoteScript
NOTE_OFF_STATUS = 128
NOTE_ON_STATUS = 144
CC_STATUS = 176
NUM_NOTES = 128
NUM_CC_NO = 128
NUM_CHANNELS = 16
JOG_DIAL_CC = 60
RWD_NOTE = 91
FFWD_NOTE = 92
STOP_NOTE = 93
PLAY_NOTE = 94
REC_NOTE = 95
SHIFT_NOTE = 70
FIRE_ONE_TRANSPORT = [RWD_NOTE,
 FFWD_NOTE,
 STOP_NOTE,
 PLAY_NOTE,
 REC_NOTE]
FIRE_ONE_F_KEYS = range(54, 64)
FIRE_ONE_CHANNEL = 0

class FireOne:
    """ Small script for the Tascam FireOne mapping transport, jog dial, and shift """

    def __init__(self, c_instance):
        self.__c_instance = c_instance
        self.__shift_pressed = False
        self.__rwd_pressed = False
        self.__ffwd_pressed = False
        self.__jog_dial_map_mode = Live.MidiMap.MapMode.absolute
        self.__spooling_counter = 0
        self.song().add_is_playing_listener(self.__playing_status_changed)
        self.song().add_record_mode_listener(self.__recording_status_changed)
        self.song().add_visible_tracks_listener(self.__tracks_changed)
        self.__playing_status_changed()
        self.__recording_status_changed()

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
        self.send_midi((NOTE_OFF_STATUS + FIRE_ONE_CHANNEL, PLAY_NOTE, 0))
        self.send_midi((NOTE_OFF_STATUS + FIRE_ONE_CHANNEL, REC_NOTE, 0))
        self.song().remove_is_playing_listener(self.__playing_status_changed)
        self.song().remove_record_mode_listener(self.__recording_status_changed)
        self.song().remove_visible_tracks_listener(self.__tracks_changed)

    def connect_script_instances(self, instanciated_scripts):
        """Called by the Application as soon as all scripts are initialized.
        You can connect yourself to other running scripts here, as we do it
        connect the extension modules (MackieControlXTs).
        """
        pass

    def suggest_input_port(self):
        """Live -> Script
        Live can ask the script for an input port name to find a suitable one.
        """
        return str('FireOne Control')

    def suggest_output_port(self):
        """Live -> Script
        Live can ask the script for an output port name to find a suitable one.
        """
        return str('FireOne Control')

    def suggest_map_mode(self, cc_no, channel):
        """Live -> Script
        Live can ask the script for a suitable mapping mode for a given CC.
        """
        suggested_map_mode = Live.MidiMap.MapMode.absolute
        if cc_no == JOG_DIAL_CC:
            suggested_map_mode = self.__jog_dial_map_mode
        return suggested_map_mode

    def can_lock_to_devices(self):
        return False

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
        pass

    def build_midi_map(self, midi_map_handle):
        """Live -> Script
        Build DeviceParameter Mappings, that are processed in Audio time, or
        forward MIDI messages explicitly to our receive_midi_functions.
        Which means that when you are not forwarding MIDI, nor mapping parameters, you will
        never get any MIDI messages at all.
        """
        script_handle = self.__c_instance.handle()
        Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, FIRE_ONE_CHANNEL, JOG_DIAL_CC)
        for note in FIRE_ONE_TRANSPORT:
            Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, FIRE_ONE_CHANNEL, note)

        Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, FIRE_ONE_CHANNEL, SHIFT_NOTE)
        for index in range(len(self.song().visible_tracks)):
            if len(FIRE_ONE_F_KEYS) > index:
                Live.MidiMap.forward_midi_note(script_handle, midi_map_handle, FIRE_ONE_CHANNEL, FIRE_ONE_F_KEYS[index])
            else:
                break

    def update_display(self):
        """Live -> Script
        Aka on_timer. Called every 100 ms and should be used to update display relevant
        parts of the controller
        """
        if self.__ffwd_pressed:
            self.__spooling_counter += 1
            if self.__spooling_counter % 2 == 0:
                self.song().jump_by(self.song().signature_denominator)
        elif self.__rwd_pressed:
            self.__spooling_counter += 1
            if self.__spooling_counter % 2 == 0:
                self.song().jump_by(-1 * self.song().signature_denominator)

    def receive_midi(self, midi_bytes):
        """Live -> Script
        MIDI messages are only received through this function, when explicitly
        forwarded in 'build_midi_map'.
        """
        cc_or_note = midi_bytes[1]
        if midi_bytes[0] & 240 == CC_STATUS:
            if cc_or_note is JOG_DIAL_CC:
                self.__jog_dial_message(cc_or_note, midi_bytes[2])
        elif midi_bytes[0] & 240 in (NOTE_ON_STATUS, NOTE_OFF_STATUS):
            value = midi_bytes[2]
            if midi_bytes[0] & 240 == NOTE_OFF_STATUS:
                value = 0
            if cc_or_note is SHIFT_NOTE:
                self.__shift_pressed = value != 0
            elif cc_or_note in FIRE_ONE_TRANSPORT:
                self.__transport_message(cc_or_note, value)
            elif cc_or_note in FIRE_ONE_F_KEYS:
                self.__f_key_message(cc_or_note, value)

    def __playing_status_changed(self):
        """ Update the LED accordingly """
        status = NOTE_OFF_STATUS
        note = PLAY_NOTE
        value = 0
        if self.song().is_playing:
            status = NOTE_ON_STATUS
            value = 127
        status += FIRE_ONE_CHANNEL
        self.send_midi((status, note, value))

    def __recording_status_changed(self):
        """ Update the LED accordingly """
        status = NOTE_OFF_STATUS
        note = REC_NOTE
        value = 0
        if self.song().record_mode:
            status = NOTE_ON_STATUS
            value = 127
        status += FIRE_ONE_CHANNEL
        self.send_midi((status, note, value))

    def __tracks_changed(self):
        self.request_rebuild_midi_map()

    def __transport_message(self, note, value):
        """ One of the transport buttons was pressed or release """
        if not note in FIRE_ONE_TRANSPORT:
            raise AssertionError
            if note is PLAY_NOTE and value != 0:
                self.__shift_pressed and self.song().continue_playing()
            else:
                self.song().is_playing = True
        elif note is STOP_NOTE and value != 0:
            self.song().is_playing = False
        elif note is REC_NOTE and value != 0:
            self.song().record_mode = not self.song().record_mode
        elif note is FFWD_NOTE:
            if value != 0 and not self.__rwd_pressed:
                if self.__shift_pressed:
                    self.song().jump_by(1)
                else:
                    self.song().jump_by(self.song().signature_denominator)
                    self.__ffwd_pressed = True
                    self.__spooling_counter = 0
            elif value == 0:
                self.__ffwd_pressed = False
        elif note is RWD_NOTE:
            if value != 0 and not self.__ffwd_pressed:
                if self.__shift_pressed:
                    self.song().jump_by(-1)
                else:
                    self.song().jump_by(-1 * self.song().signature_denominator)
                    self.__rwd_pressed = True
                    self.__spooling_counter = 0
            elif value == 0:
                self.__rwd_pressed = False

    def __jog_dial_message(self, cc_no, cc_value):
        """ Jog Dial: the function is based on the shift status and the active view """
        raise cc_value in range(128) or AssertionError
        moved_forward = cc_value in range(1, 64)
        if not self.__shift_pressed:
            if self.application().view.is_view_visible('Session'):
                index = list(self.song().scenes).index(self.song().view.selected_scene)
                if moved_forward:
                    if index < len(self.song().scenes) - 1:
                        index = index + 1
                elif index > 0:
                    index = index - 1
                self.song().view.selected_scene = self.song().scenes[index]
            else:
                value = cc_value
                if not moved_forward:
                    value -= 64
                    value *= -1
                self.song().jump_by(value)
        elif self.application().view.is_view_visible('Session'):
            tracks = self.song().visible_tracks
            index = list(tracks).index(self.song().view.selected_track)
            if moved_forward:
                if index < len(tracks) - 1:
                    index = index + 1
            elif index > 0:
                index = index - 1
            self.song().view.selected_track = tracks[index]
        else:
            value = cc_value
            if not moved_forward:
                value -= 64
                value *= -0.1
            self.song().tempo = self.song().tempo + 0.1 * value

    def __f_key_message(self, f_key, value):
        index = list(FIRE_ONE_F_KEYS).index(f_key)
        tracks = self.song().visible_tracks
        raise index >= 0 or AssertionError
        raise len(tracks) > index or AssertionError
        track = tracks[index]
        if not track != None:
            raise AssertionError
            if value > 0:
                if self.__shift_pressed:
                    track.arm = track.can_be_armed and not track.arm
            else:
                track.mute = not track.mute