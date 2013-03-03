#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/ConfigurableButtonElement.py
from _Framework.ButtonElement import ButtonElement
from Skin import Skin, SkinColorMissingError
from Colors import Basic
from MatrixMaps import NON_FEEDBACK_CHANNEL

class ConfigurableButtonElement(ButtonElement):
    """
    Special button class that can be configured with custom on-
    and off-values.
    
    A ConfigurableButtonElement can have states other than True or
    False, which can be defined by setting the 'states' property.
    Thus 'set_light' can take any state or skin color.
    """

    class Colors:

        class DefaultButton:
            On = Basic.ON
            Off = Basic.HALF
            Disabled = Basic.OFF
            Alert = Basic.FULL_BLINK_FAST

    default_skin = Skin(Colors)
    default_states = {True: 'DefaultButton.On',
     False: 'DefaultButton.Off'}
    num_delayed_messages = 2
    send_depends_on_forwarding = False

    def __init__(self, is_momentary, msg_type, channel, identifier, skin = None, is_rgb = False, default_states = None, *a, **k):
        super(ConfigurableButtonElement, self).__init__(is_momentary, msg_type, channel, identifier, *a, **k)
        if default_states is not None:
            self.default_states = default_states
        self.states = dict(self.default_states)
        self.is_rgb = is_rgb
        self._skin = skin or self.default_skin
        self._is_enabled = True
        self._force_next_value = False
        self.set_channel(NON_FEEDBACK_CHANNEL)

    @property
    def _on_value(self):
        return self.states[True]

    @property
    def _off_value(self):
        return self.states[False]

    @property
    def on_value(self):
        return self._try_fetch_skin_value(self._on_value)

    @property
    def off_value(self):
        return self._try_fetch_skin_value(self._off_value)

    def _try_fetch_skin_value(self, value):
        try:
            return self._skin[value]
        except SkinColorMissingError:
            return value

    def reset(self):
        self.states = dict(self.default_states)
        self.set_light('DefaultButton.Disabled')
        self.set_identifier(self._original_identifier)
        self.set_channel(NON_FEEDBACK_CHANNEL)
        self.set_enabled(True)

    def set_on_off_values(self, on_value, off_value):
        self.states[True] = on_value
        self.states[False] = off_value

    def set_force_next_value(self):
        self._force_next_value = True

    def set_enabled(self, enabled):
        if self._is_enabled != enabled:
            self._is_enabled = enabled
            self._request_rebuild()

    def is_enabled(self):
        return self._is_enabled

    def set_light(self, value):
        self._set_skin_light(self.states.get(value, value))

    def _set_skin_light(self, value):
        try:
            color = self._skin[value]
            color.draw(self)
        except SkinColorMissingError:
            super(ConfigurableButtonElement, self).set_light(value)

    def turn_on(self):
        self._skin[self._on_value].draw(self)

    def turn_off(self):
        self._skin[self._off_value].draw(self)

    def script_wants_forwarding(self):
        return self._is_enabled