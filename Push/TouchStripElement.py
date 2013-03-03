#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/TouchStripElement.py
import Live
import Sysex
from _Framework.Util import group, in_range
from _Framework.InputControlElement import InputControlElement, MIDI_PB_TYPE

class TouchStripElement(InputControlElement):
    """ Takes care of the different touch strip modes """
    MODE_CUSTOM_PITCHBEND = 0
    MODE_CUSTOM_VOLUME = 1
    MODE_CUSTOM_PAN = 2
    MODE_CUSTOM_DISCRETE = 3
    MODE_CUSTOM_FREE = 4
    MODE_PITCHBEND = 5
    MODE_VOLUME = 6
    MODE_PAN = 7
    MODE_DISCRETE = 8
    MODE_COUNT = 9
    STATE_OFF = 0
    STATE_HALF = 1
    STATE_FULL = 3
    STATE_COUNT = 24

    def __init__(self, *a, **k):
        super(TouchStripElement, self).__init__(MIDI_PB_TYPE, 0, 0, *a, **k)
        self.mode = self.MODE_PITCHBEND
        self._touch_button = None

    def message_map_mode(self):
        return Live.MidiMap.MapMode.absolute_14_bit

    def _set_mode(self, mode):
        raise in_range(mode, 0, self.MODE_COUNT) or AssertionError
        self._mode = mode
        self._send_midi(Sysex.START + (99,
         0,
         1,
         mode,
         247))

    def _get_mode(self):
        return self._mode

    mode = property(_get_mode, _set_mode)

    def set_touch_button(self, touch_button):
        self._touch_button = touch_button

    def is_pressed(self):
        return self._touch_button != None and self._touch_button.is_pressed()

    def reset(self):
        self.mode = self.MODE_PITCHBEND

    def turn_on_index(self, index, on_state = STATE_FULL, off_state = STATE_OFF):
        raise in_range(index, 0, self.STATE_COUNT) or AssertionError
        states = [off_state] * self.STATE_COUNT
        states[index] = on_state
        self.send_state(states)

    def turn_off(self, off_state = STATE_OFF):
        self.send_state((off_state,) * self.STATE_COUNT)

    def send_state(self, state):
        if not (self.mode == self.MODE_CUSTOM_FREE and len(state) == self.STATE_COUNT):
            raise AssertionError
            group_size = 3
            bytes = [ reduce(lambda byte, (i, state): byte | state << 2 * i, enumerate(state_group), 0) for state_group in group(state, group_size) ]
            self._send_midi(Sysex.START + (100, 0, 8) + tuple(bytes) + (247,))