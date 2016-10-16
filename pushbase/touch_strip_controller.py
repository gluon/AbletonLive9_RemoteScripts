#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/touch_strip_controller.py
from __future__ import absolute_import, print_function
from ableton.v2.control_surface import Component
from ableton.v2.control_surface.control import ToggleButtonControl
from . import consts
from .message_box_component import Messenger
from .touch_encoder_element import TouchEncoderObserver
from .touch_strip_element import DEFAULT_BEHAVIOUR, MODWHEEL_BEHAVIOUR, SimpleBehaviour, TouchStripModes, TouchStripStates

class TouchStripControllerComponent(Component):

    def __init__(self, *a, **k):
        super(TouchStripControllerComponent, self).__init__(*a, **k)
        self._touch_strip = None
        self._parameter = None

    def set_parameter(self, parameter):
        self._parameter = parameter
        self._update_strip_state()

    def set_touch_strip(self, touch_strip):
        self._touch_strip = touch_strip
        self._update_strip_state()

    def _update_strip_state(self):
        if self._touch_strip != None:
            if self._parameter != None:
                self._touch_strip.behaviour = SimpleBehaviour(self._calculate_strip_mode())
                self._touch_strip.connect_to(self._parameter)
            else:
                self._touch_strip.release_parameter()

    def _calculate_strip_mode(self):
        if self._parameter.min == -1 * self._parameter.max:
            mode = TouchStripModes.CUSTOM_PAN
        else:
            mode = TouchStripModes.CUSTOM_DISCRETE if self._parameter.is_quantized else TouchStripModes.CUSTOM_VOLUME
        return mode


class TouchStripEncoderConnection(Component, TouchEncoderObserver):

    def __init__(self, strip_controller, touch_button, *a, **k):
        super(TouchStripEncoderConnection, self).__init__(*a, **k)
        self._strip_controller = strip_controller
        self._touch_button = touch_button
        self._encoder = None

    def disconnect(self):
        self._set_touched_encoder(None)
        super(TouchStripEncoderConnection, self).disconnect()

    def on_encoder_touch(self, encoder):
        self._on_encoder_change(encoder)

    def on_encoder_parameter(self, encoder):
        self._on_encoder_change(encoder)

    def _on_encoder_change(self, encoder):
        if consts.PROTO_TOUCH_ENCODER_TO_STRIP and self._encoder in (encoder, None):
            self._set_touched_encoder(encoder if self._can_use_touch_encoder(encoder) else None)

    def _can_use_touch_encoder(self, encoder):
        is_useable = encoder.is_pressed() and encoder.mapped_parameter() != None
        can_be_initial_encoder = self._encoder == None and not self._touch_button.is_pressed()
        should_trigger_update = self._encoder == encoder
        return is_useable and (can_be_initial_encoder or should_trigger_update)

    def _set_touched_encoder(self, encoder):
        self._encoder = encoder
        parameter = encoder.mapped_parameter() if encoder != None else None
        self._strip_controller.set_parameter(parameter)
        self._strip_controller.set_enabled(parameter != None)


class TouchStripPitchModComponent(Component, Messenger):
    touch_strip_toggle = ToggleButtonControl()

    def __init__(self, *a, **k):
        super(TouchStripPitchModComponent, self).__init__(*a, **k)
        self._touch_strip = None
        self._touch_strip_indication = None

    def set_touch_strip(self, control):
        self._touch_strip = control
        self._update_touch_strip()

    def _update_touch_strip(self):
        if self._touch_strip:
            self._touch_strip.behaviour = MODWHEEL_BEHAVIOUR if self.touch_strip_toggle.is_toggled else DEFAULT_BEHAVIOUR

    @touch_strip_toggle.toggled
    def touch_strip_toggle(self, toggled, button):
        self._update_touch_strip()
        self._update_touch_strip_indication()
        self.show_notification(consts.MessageBoxText.TOUCHSTRIP_MODWHEEL_MODE if toggled else consts.MessageBoxText.TOUCHSTRIP_PITCHBEND_MODE)

    def set_touch_strip_indication(self, control):
        self._touch_strip_indication = control
        self._update_touch_strip_indication()

    def _update_touch_strip_indication(self):
        if self._touch_strip_indication:
            self._touch_strip_indication.set_mode(TouchStripModes.CUSTOM_FREE)
            self._touch_strip_indication.send_state([ (TouchStripStates.STATE_FULL if self.touch_strip_toggle.is_toggled else TouchStripStates.STATE_HALF) for _ in xrange(self._touch_strip_indication.state_count) ])

    def update(self):
        super(TouchStripPitchModComponent, self).update()
        if self.is_enabled():
            self._update_touch_strip()
            self._update_touch_strip_indication()