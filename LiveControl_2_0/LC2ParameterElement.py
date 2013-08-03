#Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/LiveControl_2_0/LC2ParameterElement.py
from _Framework.SliderElement import SliderElement
from _Framework.InputControlElement import *
from LC2Sysex import LC2Sysex
import time

class LC2ParameterElement(SliderElement):

    @staticmethod
    def set_select_param(func):
        LC2ParameterElement.select_parameter = func

    def __init__(self, type, ch, msg, report = False):
        self._report_name_val = report
        self._last_time = 0
        SliderElement.__init__(self, type, ch, msg)

    def connect_to(self, param):
        if self._parameter_to_map_to is not None:
            try:
                self._parameter_to_map_to.remove_value_listener(self._on_value_changed)
            except:
                pass

        SliderElement.connect_to(self, param)
        if param is not None:
            if not self._parameter_to_map_to.value_has_listener(self._on_value_changed):
                self._parameter_to_map_to.add_value_listener(self._on_value_changed)
        self._send_param_val(True)

    def release_parameter(self):
        SliderElement.release_parameter(self)
        self._send_param_val(True)

    def disconnect(self):
        if self._parameter_to_map_to is not None:
            if hasattr(self._parameter_to_map_to, 'name'):
                self._parameter_to_map_to.remove_value_listener(self._on_value_changed)
        SliderElement.disconnect(self)

    def _on_value_changed(self):
        if self._report_name_val:
            self._send_param_val()

    def _send_param_val(self, force = False):
        if self._parameter_to_map_to is not None:
            if hasattr(self, 'select_parameter'):
                if self._report_name_val:
                    self.select_parameter(self._parameter_to_map_to)
        if time.clock() > self._last_time + 0.01 or force:
            if hasattr(self._parameter_to_map_to, 'name'):
                sysex = LC2Sysex('PARAM_VALS')
                if self.message_type() == MIDI_PB_TYPE:
                    sysex.byte(16)
                    sysex.byte(self.message_channel())
                else:
                    sysex.byte(self.message_channel())
                    sysex.byte(self.message_identifier())
                if self._parameter_to_map_to is not None:
                    sysex.ascii(unicode(self._parameter_to_map_to.name))
                    sysex.ascii(unicode(self._parameter_to_map_to))
                    sysex.byte(self._parameter_to_map_to.is_enabled)
                else:
                    sysex.ascii(' ')
                    sysex.ascii(' ')
                    sysex.byte(0)
                    self.send_value(0)
                sysex.send()
            self._last_time = time.clock()

    def settings(self):
        if self._parameter_to_map_to is not None:
            parent = self._parameter_to_map_to.canonical_parent
            if not hasattr(parent, 'name'):
                parent = parent.canonical_parent
            return [unicode(parent.name), unicode(self._parameter_to_map_to.name)]
        else:
            return ['', '']