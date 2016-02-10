#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Arturia/ArturiaControlSurface.py
from __future__ import with_statement
from functools import partial
from _Framework import Task
from _Framework.ControlSurface import ControlSurface
SETUP_MSG_PREFIX = (240, 0, 32, 107, 127, 66)
SETUP_MSG_SUFFIX = (247,)
WRITE_COMMAND = 2
WORKING_MEMORY_ID = 0
MODE_PROPERTY = 1
CHANNEL_PROPERTY = 2
IDENTIFIER_PROPERTY = 3
MINIMUM_PROPERTY = 4
MAXIMUM_PROPERTY = 5
MODE_OPTION_PROPERTY = 6
ENCODER_CC_MODE = 1
ENCODER_RELATIVE_CC_MODE = 2
BUTTON_CC_MODE = 8
BUTTON_NOTE_MODE = 9
BUTTON_MOMENTARY_MODE_OPTION = 1
ENCODER_BINARY_OFFSET_MODE_OPTION = 1
ENCODER_TWOS_COMPLEMENT_MODE_OPTION = 2
BUTTON_MSG_TYPES = {'note': BUTTON_NOTE_MODE,
 'cc': BUTTON_CC_MODE}
SETUP_HARDWARE_DELAY = 1.0
INDIVIDUAL_MESSAGE_DELAY = 0.001

def split_list(l, size):
    for i in xrange(0, len(l), size):
        yield l[i:i + size]


class ArturiaControlSurface(ControlSurface):

    def __init__(self, *a, **k):
        super(ArturiaControlSurface, self).__init__(*a, **k)
        self._messages_to_send = []
        self._setup_hardware_task = self._tasks.add(Task.sequence(Task.run(self._collect_setup_messages), Task.wait(SETUP_HARDWARE_DELAY), Task.run(self._setup_hardware)))
        self._setup_hardware_task.kill()
        with self.component_guard():
            self._collect_setup_messages()
            self._setup_hardware()

    def _collect_setup_messages(self):
        """
        Override to set up controls on the hardware
        """
        raise NotImplementedError

    def _setup_hardware_encoder(self, hardware_id, identifier, channel = 0):
        """
        Set up a relative encoder using a twos complement coding scheme
        """
        self._set_encoder_cc_msg_type(hardware_id)
        self._set_identifier(hardware_id, identifier)
        self._set_channel(hardware_id, channel)
        self._set_twos_complement_mode(hardware_id)

    def _setup_hardware_slider(self, hardware_id, identifier, channel = 0):
        """
        Set up a simple hardware fader
        """
        self._set_encoder_cc_msg_type(hardware_id)
        self._set_identifier(hardware_id, identifier)
        self._set_channel(hardware_id, channel)

    def _setup_hardware_button(self, hardware_id, identifier, channel = 0, is_momentary = True, msg_type = 'note'):
        """
        Set up a momentary button sending MIDI notes
        """
        raise msg_type in BUTTON_MSG_TYPES.keys() or AssertionError
        self._set_button_msg_type(hardware_id, msg_type)
        self._set_identifier(hardware_id, identifier)
        self._set_channel(hardware_id, channel)
        self._set_momentary_mode(hardware_id, is_momentary)

    def _set_encoder_cc_msg_type(self, hardware_id, is_relative = False):
        self._collect_setup_message(MODE_PROPERTY, hardware_id, ENCODER_CC_MODE if not is_relative else ENCODER_RELATIVE_CC_MODE)

    def _set_button_msg_type(self, hardware_id, msg_type):
        self._collect_setup_message(MODE_PROPERTY, hardware_id, BUTTON_MSG_TYPES[msg_type])

    def _set_identifier(self, hardware_id, identifier):
        self._collect_setup_message(IDENTIFIER_PROPERTY, hardware_id, identifier)

    def _set_momentary_mode(self, hardware_id, is_momentary):
        self._collect_setup_message(MODE_OPTION_PROPERTY, hardware_id, int(is_momentary))

    def _set_channel(self, hardware_id, channel):
        self._collect_setup_message(CHANNEL_PROPERTY, hardware_id, channel)

    def _set_binary_offset_mode(self, hardware_id):
        self._collect_setup_message(MODE_OPTION_PROPERTY, hardware_id, ENCODER_BINARY_OFFSET_MODE_OPTION)

    def _set_twos_complement_mode(self, hardware_id):
        self._collect_setup_message(MODE_OPTION_PROPERTY, hardware_id, ENCODER_TWOS_COMPLEMENT_MODE_OPTION)

    def _set_value_minimum(self, hardware_id):
        self._collect_setup_message(MINIMUM_PROPERTY, hardware_id, 0)

    def _set_value_maximum(self, hardware_id):
        self._collect_setup_message(MAXIMUM_PROPERTY, hardware_id, 127)

    def _collect_setup_message(self, property, hardware_id, value):
        raise property is not None or AssertionError
        raise hardware_id is not None or AssertionError
        raise value is not None or AssertionError
        msg = SETUP_MSG_PREFIX + (WRITE_COMMAND,
         WORKING_MEMORY_ID,
         property,
         hardware_id,
         value) + SETUP_MSG_SUFFIX
        self._messages_to_send.append(msg)

    def _setup_hardware(self):
        sequence_to_run = [None] * (len(self._messages_to_send) * 2)
        sequence_to_run[::2] = [ Task.run(partial(self._send_midi, msg)) for msg in self._messages_to_send ]
        sequence_to_run[1::2] = [ Task.wait(INDIVIDUAL_MESSAGE_DELAY) for _ in self._messages_to_send ]
        for subsequence in split_list(sequence_to_run, 40):
            self._tasks.add(Task.sequence(*subsequence))

        self._messages_to_send = []

    def port_settings_changed(self):
        super(ArturiaControlSurface, self).port_settings_changed()
        self._setup_hardware_task.restart()