#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/touch_strip_element.py
from __future__ import absolute_import, print_function
import Live
from ableton.v2.base import SlotManager, in_range, nop, NamedTuple, clamp
from ableton.v2.control_surface import InputControlElement, MIDI_PB_TYPE
MAX_PITCHBEND = 16384.0

class TouchStripModes:
    CUSTOM_PITCHBEND, CUSTOM_VOLUME, CUSTOM_PAN, CUSTOM_DISCRETE, CUSTOM_FREE, PITCHBEND, VOLUME, PAN, DISCRETE, MODWHEEL, COUNT = range(11)


class TouchStripStates:
    STATE_OFF, STATE_HALF, STATE_FULL = range(3)


class TouchStripBehaviour(object):
    mode = NotImplemented

    def handle_touch(self, value):
        raise NotImplementedError

    def handle_value(self, value, notify):
        raise NotImplementedError


class SimpleBehaviour(TouchStripBehaviour):
    """
    Behaviour with custom mode.
    """

    def __init__(self, mode = TouchStripModes.PITCHBEND, *a, **k):
        super(SimpleBehaviour, self).__init__(*a, **k)
        self._mode = mode

    @property
    def mode(self):
        return self._mode

    def handle_value(self, value, notify):
        notify(value)

    def handle_touch(self, value):
        pass


class TouchStripHandle(NamedTuple):
    range = (0, 2048)
    position = 0


class SelectingBehaviour(TouchStripBehaviour):
    """
    Behaviour for selecting objects at arbitrary parts of the touch-strip. A handle can
    be used to prevent jumping around the current value of the controlled parameter.
    """
    handle = TouchStripHandle()
    mode = TouchStripModes.CUSTOM_FREE
    _offset = 0
    _grabbed = False

    def handle_value(self, value, notify):
        range, position = self.handle.range, self.handle.position
        if not self._grabbed and range[0] <= value - position < range[1]:
            self._offset = value - position
            self._grabbed = True
        else:
            notify(clamp(value - self._offset, 0, MAX_PITCHBEND))

    def handle_touch(self, value):
        self._offset = 0
        self._grabbed = False


class DraggingBehaviour(SelectingBehaviour):
    """
    Can only be dragged when starting within the handle
    """

    def handle_value(self, value, notify):

        def notify_if_dragging(value):
            if self._grabbed:
                notify(value)

        super(DraggingBehaviour, self).handle_value(value, notify_if_dragging)


DEFAULT_BEHAVIOUR = SimpleBehaviour()
MODWHEEL_BEHAVIOUR = SimpleBehaviour(mode=TouchStripModes.MODWHEEL)

class TouchStripElement(InputControlElement, SlotManager):
    """
    Represents the Push TouchStrip.
    """

    class ProxiedInterface(InputControlElement.ProxiedInterface):
        set_mode = nop
        turn_off = nop
        turn_on_index = nop
        send_state = nop
        is_pressed = nop
        behaviour = DEFAULT_BEHAVIOUR
        state_count = 24

    state_count = 24

    def __init__(self, touch_button = None, mode_element = None, light_element = None, *a, **k):
        raise mode_element is not None or AssertionError
        raise light_element is not None or AssertionError
        super(TouchStripElement, self).__init__(MIDI_PB_TYPE, 0, 0, *a, **k)
        self._mode_element = mode_element
        self._light_element = light_element
        self._touch_button = touch_button
        self._touch_slot = self.register_slot(touch_button, None, 'value')
        self._behaviour = None
        self.behaviour = None

    @property
    def touch_button(self):
        return self._touch_button

    def _get_mode(self):
        if self._behaviour != None:
            return self._behaviour.mode

    def set_mode(self, mode):
        if not in_range(mode, 0, TouchStripModes.COUNT):
            raise IndexError('Invalid Touch Strip Mode %d' % mode)
        self.behaviour = SimpleBehaviour(mode=mode)

    mode = property(_get_mode, set_mode)

    def _set_behaviour(self, behaviour):
        behaviour = behaviour or DEFAULT_BEHAVIOUR
        if behaviour != self._behaviour:
            self._behaviour = behaviour
            self._touch_slot.listener = behaviour.handle_touch
            self._mode_element.send_value(behaviour.mode)

    def _get_behaviour(self):
        return self._behaviour

    behaviour = property(_get_behaviour, _set_behaviour)

    def message_map_mode(self):
        return Live.MidiMap.MapMode.absolute_14_bit

    def is_pressed(self):
        return self._touch_button != None and self._touch_button.is_pressed()

    def reset(self):
        self.behaviour = None

    def notify_value(self, value):
        notify = super(TouchStripElement, self).notify_value
        self._behaviour.handle_value(value, notify)

    def turn_on_index(self, index, on_state = TouchStripStates.STATE_FULL, off_state = TouchStripStates.STATE_OFF):
        raise in_range(index, 0, self.state_count) or AssertionError
        states = [off_state] * self.state_count
        states[index] = on_state
        self.send_state(states)

    def turn_off(self, off_state = TouchStripStates.STATE_OFF):
        self.send_state((off_state,) * self.state_count)

    def send_state(self, state):
        if not (self._behaviour.mode == TouchStripModes.CUSTOM_FREE and len(state) == self.state_count):
            raise AssertionError
            self._light_element.send_value(state)