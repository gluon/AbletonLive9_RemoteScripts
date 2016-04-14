import Live
import MidiRemoteScript
from EffectController import EffectController
from MixerController import MixerController
from DisplayController import DisplayController
from consts import *
from _Generic.util import DeviceAppointer

class RemoteSL:
    """ Automap script for the Novation Remote SL.
    TODO: Add some general comments about the mappings, FX, MX left/right side...
    """


    def __init__(self, c_instance):
        self.__c_instance = c_instance
        self.__automap_has_control = False
        self.__display_controller = DisplayController(self)
        self.__effect_controller = EffectController(self, self.__display_controller)
        self.__mixer_controller = MixerController(self, self.__display_controller)
        self.__components = [self.__effect_controller, self.__mixer_controller, self.__display_controller]
        self.__update_hardware_delay = -1
        self._device_appointer = DeviceAppointer(song=self.song(), appointed_device_setter=self._set_appointed_device)



    def disconnect(self):
        """Called right before we get disconnected from Live
        """
        for c in self.__components:
            c.disconnect()

        self._device_appointer.disconnect()
        self.send_midi(ALL_LEDS_OFF_MESSAGE)
        self.send_midi(GOOD_BYE_SYSEX_MESSAGE)



    def application(self):
        """returns a reference to the application that we are running in
        """
        return Live.Application.get_application()



    def song(self):
        """returns a reference to the Live song instance that we do control
        """
        return self.__c_instance.song()



    def suggest_input_port(self):
        """Live -> Script
        Live can ask the script for an input port name to find a suitable one.
        """
        return 'RemoteSL'



    def suggest_output_port(self):
        """Live -> Script
        Live can ask the script for an output port name to find a suitable one.
        """
        return 'RemoteSL'



    def can_lock_to_devices(self):
        """Live -> Script
        Live can ask the script whether it can be locked to devices
        """
        return True



    def lock_to_device(self, device):
        """Live -> Script
        Live can tell the script to lock to a given device
        """
        self.__effect_controller.lock_to_device(device)



    def unlock_from_device(self, device):
        """Live -> Script
        Live can tell the script to unlock from a given device
        """
        self.__effect_controller.unlock_from_device(device)



    def _set_appointed_device(self, device):
        """Live -> Script
        Live can tell the script which device to use if it is not locked
        This is a substitute mechanism for the listeners used by older scripts
        """
        self.__effect_controller.set_appointed_device(device)



    def toggle_lock(self):
        """Script -> Live
        Use this function to toggle the script's lock on devices
        """
        self.__c_instance.toggle_lock()



    def suggest_map_mode(self, cc_no, channel):
        """Live -> Script
        Live can ask the script to suggest a map mode for the given CC
        """
        result = Live.MidiMap.MapMode.absolute
        if cc_no in fx_encoder_row_ccs:
            result = Live.MidiMap.MapMode.relative_smooth_signed_bit
        return result



    def restore_bank(self, bank):
        self.__effect_controller.restore_bank(bank)



    def supports_pad_translation(self):
        return True



    def show_message(self, message):
        self.__c_instance.show_message(message)



    def instance_identifier(self):
        return self.__c_instance.instance_identifier()



    def connect_script_instances(self, instanciated_scripts):
        """
        Called by the Application as soon as all scripts are initialized.
        You can connect yourself to other running scripts here, as we do it
        connect the extension modules (MackieControlXTs).
        """
        pass



    def request_rebuild_midi_map(self):
        """When the internal MIDI controller has changed in a way that you need to rebuild
        the MIDI mappings, request a rebuild by calling this function
        This is processed as a request, to be sure that its not too often called, because
        its time-critical.
        """
        self.__c_instance.request_rebuild_midi_map()



    def send_midi(self, midi_event_bytes):
        """Use this function to send MIDI events through Live to the _real_ MIDI devices
        that this script is assigned to.
        """
        if not self.__automap_has_control:
            self.__c_instance.send_midi(midi_event_bytes)



    def refresh_state(self):
        """Send out MIDI to completely update the attached MIDI controller.
        Will be called when requested by the user, after for example having reconnected
        the MIDI cables...
        """
        self.__update_hardware_delay = 5



    def __update_hardware(self):
        self.__automap_has_control = False
        self.send_midi(WELCOME_SYSEX_MESSAGE)
        for c in self.__components:
            c.refresh_state()




    def build_midi_map(self, midi_map_handle):
        """Build DeviceParameter Mappings, that are processed in Audio time, or
        forward MIDI messages explicitly to our receive_midi_functions.
        Which means that when you are not forwarding MIDI, nor mapping parameters, you will
        never get any MIDI messages at all.
        """
        if not self.__automap_has_control:
            for c in self.__components:
                c.build_midi_map(self.__c_instance.handle(), midi_map_handle)

        self.__c_instance.set_pad_translation(PAD_TRANSLATION)



    def update_display(self):
        """Aka on_timer. Called every 100 ms and should be used to update display relevant
        parts of the controller only...
        """
        if self.__update_hardware_delay > 0:
            self.__update_hardware_delay -= 1
            if self.__update_hardware_delay == 0:
                self.__update_hardware()
                self.__update_hardware_delay = -1
        for c in self.__components:
            c.update_display()




    def receive_midi(self, midi_bytes):
        """MIDI messages are only received through this function, when explicitly
        forwarded in 'build_midi_map'.
        """
        if midi_bytes[0] & 240 in (NOTE_ON_STATUS, NOTE_OFF_STATUS):
            channel = midi_bytes[0] & 15
            note = midi_bytes[1]
            velocity = midi_bytes[2]
            if note in fx_notes:
                self.__effect_controller.receive_midi_note(note, velocity)
            elif note in mx_notes:
                self.__mixer_controller.receive_midi_note(note, velocity)
            else:
                print 'unknown MIDI message %s' % str(midi_bytes)
        elif midi_bytes[0] & 240 == CC_STATUS:
            channel = midi_bytes[0] & 15
            cc_no = midi_bytes[1]
            cc_value = midi_bytes[2]
            if cc_no in fx_ccs:
                self.__effect_controller.receive_midi_cc(cc_no, cc_value)
            elif cc_no in mx_ccs:
                self.__mixer_controller.receive_midi_cc(cc_no, cc_value)
            else:
                print 'unknown MIDI message %s' % str(midi_bytes)
        elif midi_bytes[0] == 240:
            if len(midi_bytes) == 13 and midi_bytes[1:4] == (0, 32, 41):
                if midi_bytes[8] == ABLETON_PID and midi_bytes[10] == 1:
                    self.__automap_has_control = midi_bytes[11] == 0
                    support_mkII = midi_bytes[6] * 100 + midi_bytes[7] >= 1800
                    if not self.__automap_has_control:
                        self.send_midi(ALL_LEDS_OFF_MESSAGE)
                    for c in self.__components:
                        c.set_support_mkII(support_mkII)
                        if not self.__automap_has_control:
                            c.refresh_state()

                    self.request_rebuild_midi_map()
        else:
            print 'unknown MIDI message %s' % str(midi_bytes)




