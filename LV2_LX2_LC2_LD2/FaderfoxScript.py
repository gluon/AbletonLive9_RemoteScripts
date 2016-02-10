#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/LV2_LX2_LC2_LD2/FaderfoxScript.py
import Live
from consts import *
import sys
from FaderfoxHelper import FaderfoxHelper
from ParamMap import ParamMap
from Devices import *
from _Generic.util import DeviceAppointer

class FaderfoxScript:
    __filter_funcs__ = ['update_display', 'log', 'song']
    __module__ = __name__
    __doc__ = 'Automap script for Faderfox controllers'
    __version__ = 'V1.1'
    __name__ = 'Generic Faderfox Script'

    def __init__(self, c_instance):
        self.suffix = ''
        self.is_lv1 = False
        FaderfoxScript.realinit(self, c_instance)

    def realinit(self, c_instance):
        self.c_instance = c_instance
        self.helper = FaderfoxHelper(self)
        self.param_map = ParamMap(self)
        self.mixer_controller = None
        self.device_controller = None
        self.transport_controller = None
        self.components = []
        live = 'Live 6 & 7'
        if self.is_live_5():
            live = 'Live 5'
        self.show_message(self.__name__ + ' ' + self.__version__ + ' for ' + live)
        self.is_lv1 = False
        self._device_appointer = DeviceAppointer(song=self.song(), appointed_device_setter=self._set_appointed_device)

    def is_live_5(self):
        return hasattr(Live, 'is_live_5')

    def log(self, string):
        pass

    def logfmt(self, fmt, *args):
        pass

    def disconnect(self):
        for c in self.components:
            c.disconnect()

        self._device_appointer.disconnect()

    def application(self):
        return Live.Application.get_application()

    def song(self):
        return self.c_instance.song()

    def suggest_input_port(self):
        return str('')

    def suggest_output_port(self):
        return str('')

    def can_lock_to_devices(self):
        return True

    def lock_to_device(self, device):
        if self.device_controller:
            self.device_controller.lock_to_device(device)

    def unlock_to_device(self, device):
        if self.device_controller:
            self.device_controller.unlock_from_device(device)

    def _set_appointed_device(self, device):
        if self.device_controller:
            self.device_controller.set_appointed_device(device)

    def toggle_lock(self):
        self.c_instance.toggle_lock()

    def suggest_map_mode(self, cc_no, channel):
        return Live.MidiMap.MapMode.absolute

    def restore_bank(self, bank):
        pass

    def show_message(self, message):
        if hasattr(self.c_instance, 'show_message'):
            self.c_instance.show_message(message)

    def instance_identifier(self):
        return self.c_instance.instance_identifier()

    def connect_script_instances(self, instanciated_scripts):
        pass

    def request_rebuild_midi_map(self):
        self.c_instance.request_rebuild_midi_map()

    def send_midi(self, midi_event_bytes):
        self.c_instance.send_midi(midi_event_bytes)

    def refresh_state(self):
        for c in self.components:
            c.refresh_state()

    def build_midi_map(self, midi_map_handle):
        self.log('script build midi map')
        script_handle = self.c_instance.handle()
        self.param_map.remove_mappings()
        for c in self.components:
            self.log('build midi map on %s' % c)
            c.build_midi_map(script_handle, midi_map_handle)

    def update_display(self):
        for c in self.components:
            c.update_display()

    def receive_midi(self, midi_bytes):
        channel = midi_bytes[0] & CHAN_MASK
        status = midi_bytes[0] & STATUS_MASK
        if status == CC_STATUS:
            cc_no = midi_bytes[1]
            cc_value = midi_bytes[2]
            for c in self.components:
                c.receive_midi_cc(channel, cc_no, cc_value)

            self.param_map.receive_midi_cc(channel, cc_no, cc_value)
        elif status == NOTEON_STATUS or status == NOTEOFF_STATUS:
            note_no = midi_bytes[1]
            note_vel = midi_bytes[2]
            for c in self.components:
                c.receive_midi_note(channel, status, note_no, note_vel)

            self.param_map.receive_midi_note(channel, status, note_no, note_vel)
        else:
            raise False or AssertionError('Unknown MIDI message %s' % str(midi_bytes))