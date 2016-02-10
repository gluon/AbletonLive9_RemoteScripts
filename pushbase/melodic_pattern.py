#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/melodic_pattern.py
from __future__ import absolute_import, print_function
from ableton.v2.base import NamedTuple, lazy_attribute, memoize, find_if
from . import consts
from .matrix_maps import FEEDBACK_CHANNELS
CIRCLE_OF_FIFTHS = tuple([ 7 * k % 12 for k in range(12) ])
ROOT_NOTES = CIRCLE_OF_FIFTHS[0:6] + CIRCLE_OF_FIFTHS[-1:5:-1]
NOTE_NAMES = (u'C', u'D\u266d', u'D', u'E\u266d', u'E', u'F', u'G\u266d', u'G', u'A\u266d', u'A', u'B\u266d', u'B')

def pitch_index_to_string(index):
    if 0 <= index < 128:
        return NOTE_NAMES[index % 12] + str(index / 12 - 2)
    return consts.CHAR_ELLIPSIS


class Scale(NamedTuple):
    name = ''
    notes = []

    def to_root_note(self, root_note):
        return Scale(name=NOTE_NAMES[root_note], notes=[ root_note + x for x in self.notes ])

    @memoize
    def scale_for_notes(self, notes):
        return [ self.to_root_note(b) for b in notes ]

    def __unicode__(self):
        return self.name

    def __str__(self):
        return unicode(self).encode('utf-8')


SCALES = (Scale(name='Major', notes=[0,
  2,
  4,
  5,
  7,
  9,
  11]),
 Scale(name='Minor', notes=[0,
  2,
  3,
  5,
  7,
  8,
  10]),
 Scale(name='Dorian', notes=[0,
  2,
  3,
  5,
  7,
  9,
  10]),
 Scale(name='Mixolydian', notes=[0,
  2,
  4,
  5,
  7,
  9,
  10]),
 Scale(name='Lydian', notes=[0,
  2,
  4,
  6,
  7,
  9,
  11]),
 Scale(name='Phrygian', notes=[0,
  1,
  3,
  5,
  7,
  8,
  10]),
 Scale(name='Locrian', notes=[0,
  1,
  3,
  5,
  6,
  8,
  10]),
 Scale(name='Diminished', notes=[0,
  1,
  3,
  4,
  6,
  7,
  9,
  10]),
 Scale(name='Whole-half', notes=[0,
  2,
  3,
  5,
  6,
  8,
  9,
  11]),
 Scale(name='Whole Tone', notes=[0,
  2,
  4,
  6,
  8,
  10]),
 Scale(name='Minor Blues', notes=[0,
  3,
  5,
  6,
  7,
  10]),
 Scale(name='Minor Pentatonic', notes=[0,
  3,
  5,
  7,
  10]),
 Scale(name='Major Pentatonic', notes=[0,
  2,
  4,
  7,
  9]),
 Scale(name='Harmonic Minor', notes=[0,
  2,
  3,
  5,
  7,
  8,
  11]),
 Scale(name='Melodic Minor', notes=[0,
  2,
  3,
  5,
  7,
  9,
  11]),
 Scale(name='Super Locrian', notes=[0,
  1,
  3,
  4,
  6,
  8,
  10]),
 Scale(name='Bhairav', notes=[0,
  1,
  4,
  5,
  7,
  8,
  11]),
 Scale(name='Hungarian Minor', notes=[0,
  2,
  3,
  6,
  7,
  8,
  11]),
 Scale(name='Minor Gypsy', notes=[0,
  1,
  4,
  5,
  7,
  8,
  10]),
 Scale(name='Hirojoshi', notes=[0,
  2,
  3,
  7,
  8]),
 Scale(name='In-Sen', notes=[0,
  1,
  5,
  7,
  10]),
 Scale(name='Iwato', notes=[0,
  1,
  5,
  6,
  10]),
 Scale(name='Kumoi', notes=[0,
  2,
  3,
  7,
  9]),
 Scale(name='Pelog', notes=[0,
  1,
  3,
  4,
  7,
  8]),
 Scale(name='Spanish', notes=[0,
  1,
  3,
  4,
  5,
  6,
  8,
  10]))

def scale_by_name(name):
    return find_if(lambda m: m.name == name, SCALES)


class NoteInfo(NamedTuple):
    index = None
    channel = 0
    color = 'NoteInvalid'


class MelodicPattern(NamedTuple):
    steps = [0, 0]
    scale = range(12)
    root_note = 0
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
        return not self.origin[0] and not self.origin[1] and abs(self.root_note) % 12 == self.extended_scale[0]

    def note(self, x, y):
        return self._get_note_info(self._octave_and_note(x, y), self.root_note, x + FEEDBACK_CHANNELS[0])

    def __getitem__(self, i):
        root_note = self.root_note
        if root_note <= -12:
            root_note = 0 if self.is_aligned else -12
        return self._get_note_info(self._octave_and_note_linear(i), root_note)

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

    def _get_note_info(self, (octave, note), root_note, channel = 0):
        note_index = 12 * octave + note + root_note
        if 0 <= note_index <= 127:
            return NoteInfo(index=note_index, channel=channel, color=self._color_for_note(note))
        else:
            return NoteInfo()

    def _octave_and_note_linear(self, i):
        origin = self.origin[0] or self.origin[1]
        index = origin + i
        return self._octave_and_note_by_index(index)