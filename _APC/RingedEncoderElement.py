#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_APC/RingedEncoderElement.py
from _Framework.EncoderElement import EncoderElement
from _Framework.ButtonElement import ButtonElement
RING_OFF_VALUE = 0
RING_SIN_VALUE = 1
RING_VOL_VALUE = 2
RING_PAN_VALUE = 3

class RingedEncoderElement(EncoderElement):
    """
    Class representing a continuous control on the controller enclosed with an LED ring
    """

    def __init__(self, msg_type, channel, identifier, map_mode, *a, **k):
        super(RingedEncoderElement, self).__init__(msg_type, channel, identifier, map_mode, *a, **k)
        self._ring_mode_button = None
        self.set_needs_takeover(False)

    def set_ring_mode_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            self._ring_mode_button != None and self._ring_mode_button.send_value(RING_OFF_VALUE, force=True)
        self._ring_mode_button = button
        self._update_ring_mode()

    def connect_to(self, parameter):
        if parameter != self._parameter_to_map_to and not self.is_mapped_manually():
            self._ring_mode_button.send_value(RING_OFF_VALUE, force=True)
        super(RingedEncoderElement, self).connect_to(parameter)

    def release_parameter(self):
        super(RingedEncoderElement, self).release_parameter()
        self._update_ring_mode()

    def install_connections(self, install_translation_callback, install_mapping_callback, install_forwarding_callback):
        super(RingedEncoderElement, self).install_connections(install_translation_callback, install_mapping_callback, install_forwarding_callback)
        if not self._is_mapped and self.value_listener_count() == 0:
            self._is_being_forwarded = install_forwarding_callback(self)
        self._update_ring_mode()

    def is_mapped_manually(self):
        return not self._is_mapped and not self._is_being_forwarded

    def _update_ring_mode(self):
        if self._ring_mode_button != None:
            if self.is_mapped_manually():
                self._ring_mode_button.send_value(RING_SIN_VALUE, force=True)
            elif self._parameter_to_map_to != None:
                param = self._parameter_to_map_to
                p_range = param.max - param.min
                value = (param.value - param.min) / p_range * 127
                self.send_value(int(value), force=True)
                if self._parameter_to_map_to.min == -1 * self._parameter_to_map_to.max:
                    self._ring_mode_button.send_value(RING_PAN_VALUE, force=True)
                elif self._parameter_to_map_to.is_quantized:
                    self._ring_mode_button.send_value(RING_SIN_VALUE, force=True)
                else:
                    self._ring_mode_button.send_value(RING_VOL_VALUE, force=True)
            else:
                self._ring_mode_button.send_value(RING_OFF_VALUE, force=True)