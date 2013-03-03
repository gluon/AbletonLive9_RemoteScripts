#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/MelodicComponent.py
NOTE_NAMES = ('C', 'D\x1b', 'D', 'E\x1b', 'E', 'F', 'G\x1b', 'G', 'A\x1b', 'A', 'B\x1b', 'B')

def pitch_index_to_string(index):
    return NOTE_NAMES[index % 12] + str(index / 12 - 1)


class Scale(object):

    def __init__(self, name, notes, *a, **k):
        super(Scale, self).__init__(*a, **k)
        self.name = name
        self.notes = notes


class Modus(Scale):

    def __init__(self, *a, **k):
        super(Modus, self).__init__(*a, **k)

    def scale(self, base_note):
        return Scale(NOTE_NAMES[base_note], [ base_note + x for x in self.notes ])

    def scales(self, base_notes):
        return [ self.scale(b) for b in base_notes ]


class MelodicPattern(object):

    def __init__(self, steps = [0, 0], scale = range(12), base_note = 0, origin = [0, 0], valid_notes = xrange(128), base_note_color = 'Instrument.NoteBase', scale_note_color = 'Instrument.NoteScale', foreign_note_color = 'Instrument.NoteOff', invalid_note_color = 'Instrument.NoteInactive', chromatic_mode = False, *a, **k):
        super(MelodicPattern, self).__init__(*a, **k)
        self.steps = steps
        self.scale = scale
        self.base_note = base_note
        self.origin = origin
        self.valid_notes = valid_notes
        self.base_note_color = base_note_color
        self.scale_note_color = scale_note_color
        self.foreign_note_color = foreign_note_color
        self.invalid_note_color = invalid_note_color
        self.chromatic_mode = chromatic_mode

    class NoteInfo:

        def __init__(self, index, channel, color):
            self.index, self.channel, self.color = index, channel, color

    @property
    def _extended_scale(self):
        if self.chromatic_mode:
            first_note = self.scale[0]
            return range(first_note, first_note + 12)
        else:
            return self.scale

    def _octave_and_note(self, x, y):
        index = self.steps[0] * (self.origin[0] + x) + self.steps[1] * (self.origin[1] + y)
        scale = self._extended_scale
        scale_size = len(scale)
        octave = index / scale_size
        note = scale[index % scale_size]
        return (octave, note)

    def _color_for_note(self, note):
        if note == self.scale[0]:
            return self.base_note_color
        elif note in self.scale:
            return self.scale_note_color
        else:
            return self.foreign_note_color

    def note(self, x, y):
        octave, note = self._octave_and_note(x, y)
        index = 12 * octave + note + self.base_note
        if index in self.valid_notes:
            return self.NoteInfo(index, x + 5, self._color_for_note(note))
        else:
            return self.NoteInfo(None, x + 5, self.invalid_note_color)