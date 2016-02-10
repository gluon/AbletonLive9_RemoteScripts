#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad_Pro/MultiButtonElement.py
from .ConfigurableButtonElement import ConfigurableButtonElement

class MultiButtonElement(ConfigurableButtonElement):
    """
    Special button element for use with a button on a controller that sends
    the same MIDI message on different MIDI channels at different times.
    
    Inits a list of slave button elements that it forwards all sent values to
    and also receives values from.
    """

    def __init__(self, slave_channels, is_momentary, msg_type, channel, identifier, skin = None, default_states = None, name = '', color_slaves = False, *a, **k):
        super(MultiButtonElement, self).__init__(is_momentary, msg_type, channel, identifier, skin, default_states, *a, **k)
        self.name = name
        self._slave_buttons = [ SlaveButtonElement(self, is_momentary, msg_type, slave_channel, identifier, skin, (default_states if color_slaves else None), name=(name + '_ch_' + str(slave_channel + 1)), *a, **k) for slave_channel in slave_channels ]

    def reset(self):
        super(MultiButtonElement, self).reset()
        for button in self._slave_buttons:
            button.reset()

    def set_on_off_values(self, on_value, off_value):
        super(MultiButtonElement, self).set_on_off_values(on_value, off_value)
        for button in self._slave_buttons:
            button.set_on_off_values(on_value, off_value)

    def set_light(self, value):
        super(MultiButtonElement, self).set_light(value)
        for button in self._slave_buttons:
            button.set_light(value)

    def send_value(self, value, **k):
        super(MultiButtonElement, self).send_value(value, **k)
        for button in self._slave_buttons:
            button.send_value(value, **k)


class SlaveButtonElement(ConfigurableButtonElement):
    """
    Special button element that forwards all values it receives back
    to its associated master button.
    """

    def __init__(self, master, is_momentary, msg_type, channel, identifier, skin = None, default_states = None, *a, **k):
        super(SlaveButtonElement, self).__init__(is_momentary, msg_type, channel, identifier, skin, default_states, *a, **k)
        self._master_button = master

    def receive_value(self, value):
        super(SlaveButtonElement, self).receive_value(value)
        self._master_button.receive_value(value)