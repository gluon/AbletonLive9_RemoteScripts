#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/configurable_button_element.py
from __future__ import absolute_import, print_function
from ableton.v2.base import in_range
from ableton.v2.control_surface import Skin, SkinColorMissingError
from ableton.v2.control_surface.elements import ButtonElement, ON_VALUE, OFF_VALUE
from .colors import Basic
from .matrix_maps import NON_FEEDBACK_CHANNEL

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
        super(ConfigurableButtonElement, self).__init__(is_momentary, msg_type, channel, identifier, skin=(skin or self.default_skin), *a, **k)
        if default_states is not None:
            self.default_states = default_states
        self.states = dict(self.default_states)
        self.is_rgb = is_rgb
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

    def reset_state(self):
        super(ConfigurableButtonElement, self).reset_state()
        self.states = dict(self.default_states)

    def set_on_off_values(self, on_value, off_value):
        self.states[True] = on_value
        self.states[False] = off_value

    def set_force_next_value(self):
        self._force_next_value = True

    def set_enabled(self, enabled):
        self.suppress_script_forwarding = not enabled

    def is_enabled(self):
        return not self.suppress_script_forwarding

    def set_light(self, value):
        if type(value) in (int, long) and in_range(value, 0, 128):
            self.send_value(value)
        else:
            super(ConfigurableButtonElement, self).set_light(self.states.get(value, value))

    def send_value(self, value, **k):
        if value is ON_VALUE:
            self._do_send_on_value()
        elif value is OFF_VALUE:
            self._do_send_off_value()
        else:
            super(ConfigurableButtonElement, self).send_value(value, **k)

    def _do_send_on_value(self):
        self._skin[self._on_value].draw(self)

    def _do_send_off_value(self):
        self._skin[self._off_value].draw(self)

    def script_wants_forwarding(self):
        return not self.suppress_script_forwarding


class PadButtonElement(ConfigurableButtonElement):
    """
    Button element for holding Push pressure-sensitive pad. The pad_id
    parameter defines the Pad coordine id used in the sysex protocol.
    """

    def __init__(self, pad_id = None, pad_sensitivity_update = None, *a, **k):
        raise pad_id is not None or AssertionError
        super(PadButtonElement, self).__init__(*a, **k)
        self._sensitivity_profile = 'default'
        self._pad_id = pad_id
        self._pad_sensitivity_update = pad_sensitivity_update

    def _get_sensitivity_profile(self):
        return self._sensitivity_profile

    def _set_sensitivity_profile(self, profile):
        if profile != self._sensitivity_profile and self._pad_sensitivity_update is not None:
            self._sensitivity_profile = profile
            self._pad_sensitivity_update.set_pad(self._pad_id, profile)

    sensitivity_profile = property(_get_sensitivity_profile, _set_sensitivity_profile)

    def reset(self):
        self.sensitivity_profile = 'default'
        super(PadButtonElement, self).reset()