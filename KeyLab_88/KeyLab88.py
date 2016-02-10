#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/KeyLab_88/KeyLab88.py
from KeyLab.KeyLab import KeyLab

class KeyLab88(KeyLab):

    def _setup_hardware_encoder(self, hardware_id, identifier, channel = 0):
        self._set_encoder_cc_msg_type(hardware_id)
        self._set_identifier(hardware_id, identifier)
        self._set_channel(hardware_id, channel)
        self._set_binary_offset_mode(hardware_id)

    def _setup_hardware_button(self, hardware_id, identifier, channel = 0, **k):
        self._set_button_msg_type(hardware_id, 'cc')
        self._set_channel(hardware_id, channel)
        self._set_identifier(hardware_id, identifier)
        self._set_value_minimum(hardware_id)
        self._set_value_maximum(hardware_id)
        self._set_momentary_mode(hardware_id, is_momentary=True)