#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Axiom_25_Classic/Axiom.py
from _Axiom.consts import *
from _Axiom.Transport import Transport
from _Axiom.Pads import Pads
from _Axiom.Encoders import Encoders
from _Generic.util import DeviceAppointer
import Live
import MidiRemoteScript

class Axiom:
    """ A controller script for the M-Audio Axiom Keyboard/Controller series """

    def __init__(self, c_instance):
        self.__c_instance = c_instance
        self.__current_track = self.song().view.selected_track
        self.__current_device = self.__current_track.view.selected_device
        self.song().add_visible_tracks_listener(self.__tracks_changed)
        self.__transport_unit = Transport(self)
        self.__encoder_unit = Encoders(self, False)
        self.__pad_unit = Pads(self)
        self._device_appointer = DeviceAppointer(song=self.song(), appointed_device_setter=self._set_appointed_device)

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
        self.song().remove_visible_tracks_listener(self.__tracks_changed)
        self._device_appointer.disconnect()
        self.__encoder_unit.disconnect()

    def can_lock_to_devices(self):
        return True

    def suggest_input_port(self):
        """Live -> Script
        Live can ask the script for an input port name to find a suitable one.
        """
        return str('USB Axiom 25')

    def suggest_output_port(self):
        """Live -> Script
        Live can ask the script for an output port name to find a suitable one.
        """
        return str('USB Axiom 25')

    def suggest_map_mode(self, cc_no, channel):
        """Live -> Script
        Live can ask the script for a suitable mapping mode for a given CC.
        """
        suggested_map_mode = Live.MidiMap.MapMode.absolute
        if cc_no in AXIOM_ENCODERS:
            suggested_map_mode = Live.MidiMap.MapMode.relative_smooth_binary_offset
        return suggested_map_mode

    def show_message(self, message):
        self.__c_instance.show_message(message)

    def supports_pad_translation(self):
        return True

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
        pass

    def build_midi_map(self, midi_map_handle):
        """Live -> Script
        Build DeviceParameter Mappings, that are processed in Audio time, or
        forward MIDI messages explicitly to our receive_midi_functions.
        Which means that when you are not forwarding MIDI, nor mapping parameters, you will
        never get any MIDI messages at all.
        """
        script_handle = self.__c_instance.handle()
        for channel in range(4):
            Live.MidiMap.forward_midi_cc(script_handle, midi_map_handle, channel, EXP_PEDAL_CC)

        self.__transport_unit.build_midi_map(script_handle, midi_map_handle)
        self.__encoder_unit.build_midi_map(script_handle, midi_map_handle)
        self.__pad_unit.build_midi_map(script_handle, midi_map_handle)
        self.__c_instance.set_pad_translation(PAD_TRANSLATION)

    def update_display(self):
        """Live -> Script
        Aka on_timer. Called every 100 ms and should be used to update display relevant
        parts of the controller
        """
        if self.__transport_unit:
            self.__transport_unit.refresh_state()

    def receive_midi(self, midi_bytes):
        """Live -> Script
        MIDI messages are only received through this function, when explicitly
        forwarded in 'build_midi_map'.
        """
        if midi_bytes[0] & 240 == CC_STATUS:
            channel = midi_bytes[0] & 15
            cc_no = midi_bytes[1]
            cc_value = midi_bytes[2]
            if list(AXIOM_TRANSPORT).count(cc_no) > 0:
                self.__transport_unit.receive_midi_cc(cc_no, cc_value)
            elif list(AXIOM_ENCODERS).count(cc_no) > 0:
                self.__encoder_unit.receive_midi_cc(cc_no, cc_value, channel)
            elif list(AXIOM_PADS).count(cc_no) > 0:
                self.__pad_unit.receive_midi_cc(cc_no, cc_value, channel)
            elif cc_no == EXP_PEDAL_CC:
                self.__encoder_unit.set_modifier(cc_value == 0)
                self.request_rebuild_midi_map()
        elif midi_bytes[0] == 240:
            pass

    def lock_to_device(self, device):
        self.__encoder_unit.lock_to_device(device)

    def unlock_from_device(self, device):
        self.__encoder_unit.unlock_from_device(device)

    def _set_appointed_device(self, device):
        self.__encoder_unit.set_appointed_device(device)

    def __tracks_changed(self):
        self.request_rebuild_midi_map()

    def bank_changed(self, new_bank):
        if self.__encoder_unit.set_bank(new_bank):
            self.request_rebuild_midi_map()

    def restore_bank(self, bank):
        self.__encoder_unit.restore_bank(bank)
        self.request_rebuild_midi_map()

    def instance_identifier(self):
        return self.__c_instance.instance_identifier()