#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/PadSensitivity.py
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.Util import NamedTuple
MAX_32BIT_VALUE = 4294967295L

def bytes_from_value(value, byte_count):
    """
    turns the given value into tuple of 4bit bytes,
    ordered from most significant to least significant byte
    """
    value_bytes = []
    offset = 0
    while len(value_bytes) < byte_count:
        value_bytes.append(value >> offset & 15)
        offset += 4

    return tuple(reversed(value_bytes))


class PadParameters(NamedTuple):
    off_threshold = 0
    on_threshold = 0
    gain = 0
    curve1 = 0
    curve2 = 0
    name = ''

    def __str__(self):
        return self.name


class PadSensitivity(ControlSurfaceComponent):

    def __init__(self, value_control = None, *a, **k):
        super(PadSensitivity, self).__init__(*a, **k)
        raise value_control != None or AssertionError
        self._value_control = value_control
        self.parameters = PadParameters()

    def update(self):
        self._send_values()

    def _set_parameters(self, settings):
        self._parameter_bytes = ((settings.off_threshold, 4),
         (settings.on_threshold, 4),
         (settings.gain, 8),
         (settings.curve1, 8),
         (settings.curve2, 8))
        self.update()

    def _get_parameters(self):
        return PadParameters(off_threshold=self._parameter_bytes[0][0], on_threshold=self._parameter_bytes[1][0], gain=self._parameter_bytes[2][0], curve1=self._parameter_bytes[3][0], curve2=self._parameter_bytes[4][0])

    parameters = property(_get_parameters, _set_parameters)

    def _send_values(self):
        value_bytes = ()
        for value in self._parameter_bytes:
            value_bytes += bytes_from_value(value[0], value[1])

        self._value_control.send_value(value_bytes)