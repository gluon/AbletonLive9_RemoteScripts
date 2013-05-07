#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/PhysicalDisplayElement.py
from ControlElement import ControlElement
from LogicalDisplaySegment import LogicalDisplaySegment, adjust_string
from Util import in_range
import Task

class PhysicalDisplayElement(ControlElement):
    """
    Class representing a display on the controller
    """
    _ascii_translations = {'0': 48,
     '1': 49,
     '2': 50,
     '3': 51,
     '4': 52,
     '5': 53,
     '6': 54,
     '7': 55,
     '8': 56,
     '9': 57,
     'A': 65,
     'B': 66,
     'C': 67,
     'D': 68,
     'E': 69,
     'F': 70,
     'G': 71,
     'H': 72,
     'I': 73,
     'J': 74,
     'K': 75,
     'L': 76,
     'M': 77,
     'N': 78,
     'O': 79,
     'P': 80,
     'Q': 81,
     'R': 82,
     'S': 83,
     'T': 84,
     'U': 85,
     'V': 86,
     'W': 87,
     'X': 88,
     'Y': 89,
     'Z': 90,
     'a': 97,
     'b': 98,
     'c': 99,
     'd': 100,
     'e': 101,
     'f': 102,
     'g': 103,
     'h': 104,
     'i': 105,
     'j': 106,
     'k': 107,
     'l': 108,
     'm': 109,
     'n': 110,
     'o': 111,
     'p': 112,
     'q': 113,
     'r': 114,
     's': 115,
     't': 116,
     'u': 117,
     'v': 118,
     'w': 119,
     'x': 120,
     'y': 121,
     'z': 122,
     '@': 64,
     ' ': 32,
     '!': 33,
     '"': 34,
     '.': 46,
     ',': 44,
     ':': 58,
     ';': 59,
     '?': 63,
     '<': 60,
     '>': 62,
     '[': 91,
     ']': 93,
     '_': 95,
     '-': 45,
     '|': 124,
     '&': 38,
     '^': 94,
     '~': 126,
     '`': 96,
     "'": 39,
     '%': 37,
     '(': 40,
     ')': 41,
     '/': 47,
     '\\': 92,
     '*': 42,
     '+': 43}

    def __init__(self, width_in_chars = None, num_segments = 1, *a, **k):
        super(PhysicalDisplayElement, self).__init__(*a, **k)
        raise width_in_chars is not None or AssertionError
        raise num_segments is not None or AssertionError
        self._width = width_in_chars
        self._logical_segments = []
        self._translation_table = self._ascii_translations
        self.set_num_segments(num_segments)
        self._message_header = None
        self._message_tail = None
        self._message_part_delimiter = None
        self._message_clear_all = None
        self._message_to_send = None
        self._last_sent_message = None
        self._block_messages = False
        self._send_message_task = self._tasks.add(Task.run(self._send_message))
        self._send_message_task.kill()

    def disconnect(self):
        self._disconnect_segments()
        super(PhysicalDisplayElement, self).disconnect()

    def _disconnect_segments(self):
        for segment in self._logical_segments:
            segment.disconnect()

    @property
    def num_segments(self):
        return len(self._logical_segments)

    def set_num_segments(self, num_segments, use_delimiters = True):
        if not in_range(num_segments, 1, self._width - num_segments + 1):
            raise AssertionError
            if num_segments != len(self._logical_segments):
                self._disconnect_segments()
                width_without_delimiters = use_delimiters and self._width - num_segments + 1
            else:
                width_without_delimiters = self._width
            width_per_segment = int(width_without_delimiters / num_segments)
            self._logical_segments = [ LogicalDisplaySegment(width_per_segment, self.update) for _ in xrange(num_segments) ]

    def set_data_sources(self, sources):
        """
        Given a sequences of data sources, divides the display into
        the number of segments neded to accomodate them and connects
        the logical segments to the data sources.
        """
        if not sources:
            self.set_num_segments(1)
            self.reset()
        else:
            self.set_num_segments(len(sources))
            for segment, source in zip(self._logical_segments, sources):
                segment.set_data_source(source)

    def set_translation_table(self, translation_table):
        raise '?' in translation_table['?'] or AssertionError
        self._translation_table = translation_table

    def set_message_parts(self, header, tail, delimiter = tuple()):
        """
        Takes message parts as tuples containing the sysex bytes for
        each part of the message.
        """
        self._message_header = header
        self._message_tail = tail
        self._message_part_delimiter = delimiter

    def set_clear_all_message(self, message):
        self._message_clear_all = message

    def set_block_messages(self, block):
        if block != self._block_messages:
            self._block_messages = block
        self.clear_send_cache()

    def segment(self, index):
        return self._logical_segments[index]

    def update(self):
        if not self._message_header is not None:
            raise AssertionError
            self._message_to_send = len(self._logical_segments) > 0 and not self._block_messages and None
            self._request_send_message()

    def display_message(self, message):
        if not self._block_messages:
            message = adjust_string(message, self._width)
            self._message_to_send = self._message_header + self._translate_string(message) + self._message_tail
            self._request_send_message()

    def reset(self):
        if not (self._message_clear_all is not None or self._message_header is not None):
            raise AssertionError
            for segment in self._logical_segments:
                segment.set_data_source(None)

            if not self._block_messages:
                self._message_to_send = self._message_clear_all != None and self._message_clear_all
            else:
                self._message_to_send = self._message_header + self._translate_string(' ' * self._width) + self._message_tail
            self._request_send_message()

    def send_midi(self, midi_bytes):
        if midi_bytes != self._last_sent_message:
            ControlElement.send_midi(self, midi_bytes)
            self._last_sent_message = midi_bytes

    def clear_send_cache(self):
        self._last_sent_message = None
        self._request_send_message()

    def _request_send_message(self):
        self._send_message_task.restart()

    def _send_message(self):
        if not self._block_messages:
            if self._message_to_send is None:
                self._build_message_from_segments()
            self.send_midi(self._message_to_send)

    def _translate_char(self, char_to_translate):
        result = 63
        if char_to_translate in self._translation_table.keys():
            result = self._translation_table[char_to_translate]
        else:
            result = self._translation_table['?']
        return result

    def _translate_string(self, string):
        return tuple([ self._translate_char(c) for c in string ])

    def _build_message_from_segments(self):
        message = self._message_header
        for segment in self._logical_segments:
            message += segment.position_identifier()
            message += self._translate_string(segment.display_string())
            if self._message_part_delimiter != None and segment != self._logical_segments[-1]:
                message += self._message_part_delimiter

        message += self._message_tail
        self._message_to_send = message