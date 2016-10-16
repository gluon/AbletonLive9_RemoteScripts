#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/MackieControl.py
from consts import *
from MainDisplay import MainDisplay
from MainDisplayController import MainDisplayController
from TimeDisplay import TimeDisplay
from ChannelStrip import ChannelStrip, MasterChannelStrip
from ChannelStripController import ChannelStripController
from SoftwareController import SoftwareController
from Transport import Transport
import Live
import MidiRemoteScript

class MackieControl:
    """Main class that establishes the Mackie Control <-> Live interaction. It acts
       as a container/manager for all the Mackie Control sub-components like ChannelStrips,
       Displays and so on.
       Futher it is glued to Lives MidiRemoteScript C instance, which will forward some
       notifications to us, and lets us forward some requests that are needed beside the
       general Live API (see 'send_midi' or 'request_rebuild_midi_map').
    """

    def __init__(self, c_instance):
        self.__c_instance = c_instance
        self.__components = []
        self.__main_display = MainDisplay(self)
        self.__components.append(self.__main_display)
        self.__main_display_controller = MainDisplayController(self, self.__main_display)
        self.__components.append(self.__main_display_controller)
        self.__time_display = TimeDisplay(self)
        self.__components.append(self.__time_display)
        self.__software_controller = SoftwareController(self)
        self.__components.append(self.__software_controller)
        self.__transport = Transport(self)
        self.__components.append(self.__transport)
        self.__channel_strips = [ ChannelStrip(self, i) for i in range(NUM_CHANNEL_STRIPS) ]
        for s in self.__channel_strips:
            self.__components.append(s)

        self.__master_strip = MasterChannelStrip(self)
        self.__components.append(self.__master_strip)
        self.__channel_strip_controller = ChannelStripController(self, self.__channel_strips, self.__master_strip, self.__main_display_controller)
        self.__components.append(self.__channel_strip_controller)
        self.__shift_is_pressed = False
        self.__option_is_pressed = False
        self.__ctrl_is_pressed = False
        self.__alt_is_pressed = False
        self.is_pro_version = False
        self._received_firmware_version = False
        self._refresh_state_next_time = 0

    def disconnect(self):
        for c in self.__components:
            c.destroy()

    def connect_script_instances(self, instanciated_scripts):
        """Called by the Application as soon as all scripts are initialized.
           You can connect yourself to other running scripts here, as we do it
           connect the extension modules (MackieControlXTs).
        """
        try:
            from MackieControlXT.MackieControlXT import MackieControlXT
        except:
            print 'failed to load the MackieControl XT script (might not be installed)'

        found_self = False
        right_extensions = []
        left_extensions = []
        for s in instanciated_scripts:
            if s is self:
                found_self = True
            elif isinstance(s, MackieControlXT):
                s.set_mackie_control_main(self)
                if found_self:
                    right_extensions.append(s)
                else:
                    left_extensions.append(s)

        raise found_self or AssertionError
        self.__main_display_controller.set_controller_extensions(left_extensions, right_extensions)
        self.__channel_strip_controller.set_controller_extensions(left_extensions, right_extensions)

    def request_firmware_version(self):
        if not self._received_firmware_version:
            self.send_midi((240,
             0,
             0,
             102,
             SYSEX_DEVICE_TYPE,
             19,
             0,
             247))

    def application(self):
        """returns a reference to the application that we are running in"""
        return Live.Application.get_application()

    def song(self):
        """returns a reference to the Live Song that we do interact with"""
        return self.__c_instance.song()

    def handle(self):
        """returns a handle to the c_interface that is needed when forwarding MIDI events
           via the MIDI map
        """
        return self.__c_instance.handle()

    def refresh_state(self):
        for c in self.__components:
            c.refresh_state()

        self.request_firmware_version()
        self._refresh_state_next_time = 30

    def is_extension(self):
        return False

    def request_rebuild_midi_map(self):
        """ To be called from any components, as soon as their internal state changed in a
        way, that we do need to remap the mappings that are processed directly by the
        Live engine.
        Dont assume that the request will immediately result in a call to
        your build_midi_map function. For performance reasons this is only
        called once per GUI frame."""
        self.__c_instance.request_rebuild_midi_map()

    def build_midi_map(self, midi_map_handle):
        """New MIDI mappings can only be set when the scripts 'build_midi_map' function
        is invoked by our C instance sibling. Its either invoked when we have requested it
        (see 'request_rebuild_midi_map' above) or when due to a change in Lives internal state,
        a rebuild is needed."""
        for s in self.__channel_strips:
            s.build_midi_map(midi_map_handle)

        self.__master_strip.build_midi_map(midi_map_handle)
        for i in range(SID_FIRST, SID_LAST + 1):
            if i not in function_key_control_switch_ids:
                Live.MidiMap.forward_midi_note(self.handle(), midi_map_handle, 0, i)

        Live.MidiMap.forward_midi_cc(self.handle(), midi_map_handle, 0, JOG_WHEEL_CC_NO)

    def update_display(self):
        if self._refresh_state_next_time > 0:
            self._refresh_state_next_time -= 1
            if self._refresh_state_next_time == 0:
                for c in self.__components:
                    c.refresh_state()

                self.request_firmware_version()
        for c in self.__components:
            c.on_update_display_timer()

    def send_midi(self, midi_event_bytes):
        """Use this function to send MIDI events through Live to the _real_ MIDI devices
        that this script is assigned to."""
        self.__c_instance.send_midi(midi_event_bytes)

    def receive_midi(self, midi_bytes):
        if midi_bytes[0] & 240 == NOTE_ON_STATUS or midi_bytes[0] & 240 == NOTE_OFF_STATUS:
            note = midi_bytes[1]
            value = BUTTON_PRESSED if midi_bytes[2] > 0 else BUTTON_RELEASED
            if note in range(SID_FIRST, SID_LAST + 1):
                if note in display_switch_ids:
                    self.__handle_display_switch_ids(note, value)
                if note in channel_strip_switch_ids + fader_touch_switch_ids:
                    for s in self.__channel_strips:
                        s.handle_channel_strip_switch_ids(note, value)

                if note in channel_strip_control_switch_ids:
                    self.__channel_strip_controller.handle_assignment_switch_ids(note, value)
                if note in function_key_control_switch_ids:
                    self.__software_controller.handle_function_key_switch_ids(note, value)
                if note in software_controls_switch_ids:
                    self.__software_controller.handle_software_controls_switch_ids(note, value)
                if note in transport_control_switch_ids:
                    self.__transport.handle_transport_switch_ids(note, value)
                if note in marker_control_switch_ids:
                    self.__transport.handle_marker_switch_ids(note, value)
                if note in jog_wheel_switch_ids:
                    self.__transport.handle_jog_wheel_switch_ids(note, value)
        elif midi_bytes[0] & 240 == CC_STATUS:
            cc_no = midi_bytes[1]
            cc_value = midi_bytes[2]
            if cc_no == JOG_WHEEL_CC_NO:
                self.__transport.handle_jog_wheel_rotation(cc_value)
            elif cc_no in range(FID_PANNING_BASE, FID_PANNING_BASE + NUM_CHANNEL_STRIPS):
                for s in self.__channel_strips:
                    s.handle_vpot_rotation(cc_no - FID_PANNING_BASE, cc_value)

        elif midi_bytes[0] == 240 and len(midi_bytes) == 12 and midi_bytes[5] == 20:
            version_bytes = midi_bytes[6:-2]
            major_version = version_bytes[1]
            self.is_pro_version = major_version > 50
            self._received_firmware_version = True

    def can_lock_to_devices(self):
        return False

    def suggest_input_port(self):
        return ''

    def suggest_output_port(self):
        return ''

    def suggest_map_mode(self, cc_no, channel):
        result = Live.MidiMap.MapMode.absolute
        if cc_no in range(FID_PANNING_BASE, FID_PANNING_BASE + NUM_CHANNEL_STRIPS):
            result = Live.MidiMap.MapMode.relative_signed_bit
        return result

    def shift_is_pressed(self):
        return self.__shift_is_pressed

    def set_shift_is_pressed(self, pressed):
        self.__shift_is_pressed = pressed

    def option_is_pressed(self):
        return self.__option_is_pressed

    def set_option_is_pressed(self, pressed):
        self.__option_is_pressed = pressed

    def control_is_pressed(self):
        return self.__control_is_pressed

    def set_control_is_pressed(self, pressed):
        self.__control_is_pressed = pressed

    def alt_is_pressed(self):
        return self.__alt_is_pressed

    def set_alt_is_pressed(self, pressed):
        self.__alt_is_pressed = pressed

    def __handle_display_switch_ids(self, switch_id, value):
        if switch_id == SID_DISPLAY_NAME_VALUE:
            if value == BUTTON_PRESSED:
                self.__channel_strip_controller.toggle_meter_mode()
        elif switch_id == SID_DISPLAY_SMPTE_BEATS:
            if value == BUTTON_PRESSED:
                self.__time_display.toggle_mode()