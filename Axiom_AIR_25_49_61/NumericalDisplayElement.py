#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Axiom_AIR_25_49_61/NumericalDisplayElement.py
from _Framework.PhysicalDisplayElement import PhysicalDisplayElement
from NumericalDisplaySegment import NumericalDisplaySegment

class NumericalDisplayElement(PhysicalDisplayElement):
    """ Special display element that only displays numerical values """
    _ascii_translations = {'0': 48,
     '1': 49,
     '2': 50,
     '3': 51,
     '4': 52,
     '5': 53,
     '6': 54,
     '7': 55,
     '8': 56,
     '9': 57}

    def __init__(self, width_in_chars, num_segments):
        PhysicalDisplayElement.__init__(self, width_in_chars, num_segments)
        self._logical_segments = []
        self._translation_table = NumericalDisplayElement._ascii_translations
        width_without_delimiters = self._width - num_segments + 1
        width_per_segment = int(width_without_delimiters / num_segments)
        for index in range(num_segments):
            new_segment = NumericalDisplaySegment(width_per_segment, self.update)
            self._logical_segments.append(new_segment)

    def display_message(self, message):
        if not self._message_header != None:
            raise AssertionError
            raise message != None or AssertionError
            raise isinstance(message, str) or AssertionError
            message = self._block_messages or NumericalDisplaySegment.adjust_string(message, self._width)
            self.send_midi(self._message_header + tuple([ self._translate_char(c) for c in message ]) + self._message_tail)

    def _translate_char(self, char_to_translate):
        if not char_to_translate != None:
            raise AssertionError
            raise isinstance(char_to_translate, str) or isinstance(char_to_translate, unicode) or AssertionError
            raise len(char_to_translate) == 1 or AssertionError
            result = char_to_translate in self._translation_table.keys() and self._translation_table[char_to_translate]
        else:
            result = self._translation_table['0']
        return result