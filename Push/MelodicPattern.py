#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/MelodicPattern.py
from _Framework.Util import NamedTuple, lazy_attribute, memoize
import consts
NOTE_NAMES = ('C', 'D\x1b', 'D', 'E\x1b', 'E', 'F', 'G\x1b', 'G', 'A\x1b', 'A', 'B\x1b', 'B')

def pitch_index_to_string(index):
    if 0 <= index < 128:
        return NOTE_NAMES[index % 12] + str(index / 12 - 2)
    return consts.CHAR_ELLIPSIS


class Scale(NamedTuple):
    name = ''
    notes = []


class Modus(Scale):

    def __str__(self):
        return self.name

    def scale(self, base_note):
        return Scale(name=NOTE_NAMES[base_note], notes=[ base_note + x for x in self.notes ])

    @memoize
    def scales(self, base_notes):
        return [ self.scale(b) for b in base_notes ]


class NoteInfo(NamedTuple):
    index = None
    channel = 0
    color = 'NoteInvalid'


class MelodicPattern(NamedTuple):
    steps = [0, 0]
    scale = range(12)
    base_note = 0
    origin = [0, 0]
    chromatic_mode = False

    @lazy_attribute
    def extended_scale(self):
        if self.chromatic_mode:
            first_note = self.scale[0]
            return range(first_note, first_note + 12)
        else:
            return self.scale

    @property
    def is_aligned(self):
        return not self.origin[0] and not self.origin[1] and abs(self.base_note) % 12 == self.extended_scale[0]

    def note(self, x, y):
        return self._get_note_info(self._octave_and_note(x, y), self.base_note, x + 5)

    def __getitem__(self, i):
        base_note = self.base_note
        if base_note <= -12:
            base_note = 0 if self.is_aligned else -12
        return self._get_note_info(self._octave_and_note_linear(i), base_note)

    def _octave_and_note_by_index(self, index):
        scale = self.extended_scale
        scale_size = len(scale)
        octave = index / scale_size
        note = scale[index % scale_size]
        return (octave, note)

    def _octave_and_note(self, x, y):
        index = self.steps[0] * (self.origin[0] + x) + self.steps[1] * (self.origin[1] + y)
        return self._octave_and_note_by_index(index)

    def _color_for_note(self, note):
        if note == self.scale[0]:
            return 'NoteBase'
        elif note in self.scale:
            return 'NoteScale'
        else:
            return 'NoteNotScale'

    def _get_note_info(self, (octave, note), base_note, channel = 0):
        note_index = 12 * octave + note + base_note
        if 0 <= note_index <= 127:
            return NoteInfo(index=note_index, channel=channel, color=self._color_for_note(note))
        else:
            return NoteInfo()

    def _octave_and_note_linear(self, i):
        origin = self.origin[0] or self.origin[1]
        index = origin + i
        return self._octave_and_note_by_index(index)