#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/PhysicalDisplayElement.py
from __future__ import absolute_import
from itertools import ifilter, izip, starmap, chain, imap
from functools import partial
from . import Task
from .ControlElement import ControlElement
from .DisplayDataSource import adjust_string
from .LogicalDisplaySegment import LogicalDisplaySegment
from .NotifyingControlElement import NotifyingControlElement
from .Resource import StackingResource, ProxyResource, ClientWrapper
from .Util import in_range, slicer, to_slice, slice_size, const, group, second, maybe, lazy_attribute, first, nop

class _DisplayCentralResource(StackingResource):
    """
    Resource to be used internallt by the PhysicalDisplayElement.  All
    sub-displays and the display itself will compete against this
    central resource.  The central resource will take into account
    wheter there is any free area in the display for a client, to
    decide wheter he gets it or not.
    """

    def __init__(self, root_display = None, *a, **k):
        super(_DisplayCentralResource, self).__init__(*a, **k)
        self._root_display = root_display

    def _actual_owners(self):
        remaining_indexes = set(self._root_display.display_indexes)

        def filter_client(((display, _), __)):
            result = remaining_indexes & display.display_indexes
            remaining_indexes.difference_update(display.display_indexes)
            return bool(result)

        return list(reversed(map(first, ifilter(filter_client, reversed(self._clients)))))


class DisplayError(Exception):
    pass


class DisplaySegmentationError(DisplayError):
    pass


class DisplayElement(ControlElement):
    """
    Base class for character-based displays.
    """

    class ProxiedInterface(ControlElement.ProxiedInterface):
        set_num_segments = nop
        set_data_sources = nop
        segment = const(LogicalDisplaySegment(1, nop))

    def __init__(self, width_in_chars = None, num_segments = 1, *a, **k):
        super(DisplayElement, self).__init__(*a, **k)
        raise width_in_chars is not None or AssertionError
        raise num_segments is not None or AssertionError
        self._width = width_in_chars
        self._logical_segments = []
        self.set_num_segments(num_segments)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.display_string)

    @property
    def display_string(self):
        return ''.join(imap(unicode, self._logical_segments))

    @property
    def width(self):
        return self._width

    @lazy_attribute
    def display_slice(self):
        return slicer(1)(nop)()[:]

    @lazy_attribute
    def display_indexes(self):
        """
        Indexes of the current display w.r.t. the parent display indexes.
        """
        return set(range(self._width))

    def disconnect(self):
        self._disconnect_segments()
        super(DisplayElement, self).disconnect()

    def _disconnect_segments(self):
        for segment in self._logical_segments:
            segment.disconnect()

    @property
    def num_segments(self):
        return len(self._logical_segments)

    def set_num_segments(self, num_segments):
        width = self._width
        if not in_range(num_segments, 1, width) or width % num_segments != 0:
            raise DisplaySegmentationError, 'Can not split display of size %d into %d segments' % (self.width, num_segments)
        if num_segments != len(self._logical_segments):
            self._disconnect_segments()
            self._width_per_segment = width / num_segments
            self._logical_segments = [ LogicalDisplaySegment(self._width_per_segment, self.update) for _ in xrange(num_segments) ]

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

    @property
    def segments(self):
        return tuple(self._logical_segments)

    def segment(self, index):
        return self._logical_segments[index]

    def reset(self):
        for segment in self._logical_segments:
            segment.set_data_source(None)

    def update(self):
        pass


class PhysicalDisplayElement(DisplayElement, NotifyingControlElement):
    """
    A physical character based display control element.
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

    def __init__(self, *a, **k):
        self._central_resource = _DisplayCentralResource(root_display=self, on_received_callback=self._on_central_resource_received, on_lost_callback=self._on_central_resource_lost)
        super(PhysicalDisplayElement, self).__init__(resource_type=self.nested_display_resource_factory(self), *a, **k)
        self._translation_table = self._ascii_translations
        self._message_header = None
        self._message_tail = None
        self._message_clear_all = None
        self._message_to_send = None
        self._last_sent_message = None
        self._block_messages = False
        self._send_message_task = self._tasks.add(Task.run(self._send_message))
        self._send_message_task.kill()

    def nested_display_resource_factory(self, display):
        wrapper = ClientWrapper(wrap=lambda c: (display, c), unwrap=partial(maybe(second)))
        return const(ProxyResource(proxied_resource=self._central_resource, client_wrapper=wrapper))

    def _on_central_resource_received(self, (display, client)):
        client.set_control_element(display, True)
        self.update()

    def _on_central_resource_lost(self, (display, client)):
        client.set_control_element(display, False)
        self.update()

    @property
    @slicer(1)
    def subdisplay(self, char_slice):
        char_slice = to_slice(char_slice)
        return SubDisplayElement(sub_display_slice=char_slice, parent_display=self)

    def set_message_parts(self, header, tail):
        """
        Takes message parts as tuples containing the sysex bytes for
        each part of the message.
        """
        self._message_header = header
        self._message_tail = tail

    @property
    def message_header(self):
        return self._message_header

    @property
    def message_tail(self):
        return self._message_tail

    def set_clear_all_message(self, message):
        self._message_clear_all = message

    def set_translation_table(self, translation_table):
        raise '?' in translation_table['?'] or AssertionError
        self._translation_table = translation_table

    def set_block_messages(self, block):
        if block != self._block_messages:
            self._block_messages = block
        self.clear_send_cache()

    def display_message(self, message):
        if not self._block_messages:
            message = adjust_string(message, self._width)
            self._message_to_send = self._message_header + tuple(self._translate_string(message)) + self._message_tail
            self._request_send_message()

    def update(self):
        if not self._message_header is not None:
            raise AssertionError
            self._message_to_send = len(self._logical_segments) > 0 and not self._block_messages and None
            self._request_send_message()

    def clear_send_cache(self):
        self._last_sent_message = None
        self._request_send_message()

    def reset(self):
        if not (self._message_clear_all is not None or self._message_header is not None):
            raise AssertionError
            super(PhysicalDisplayElement, self).reset()
            if not self._block_messages:
                self._message_to_send = self._message_clear_all != None and self._message_clear_all
            else:
                self._message_to_send = tuple(chain(self._message_header, self._translate_string(' ' * self._width), self._message_tail))
            self._request_send_message()

    def send_midi(self, midi_bytes):
        if midi_bytes != self._last_sent_message:
            ControlElement.send_midi(self, midi_bytes)
            self._last_sent_message = midi_bytes

    def _request_send_message(self):
        self._send_message_task.restart()

    def _send_message(self):
        if not self._block_messages:
            if self._message_to_send is None:
                self._message_to_send = self._build_message(map(first, self._central_resource.owners))
            self.send_midi(self._message_to_send)

    def _translate_char(self, char_to_translate):
        result = 63
        if char_to_translate in self._translation_table.keys():
            result = self._translation_table[char_to_translate]
        else:
            result = self._translation_table['?']
        return result

    def _translate_string(self, string):
        return map(self._translate_char, string)

    def _build_display_message(self, display):
        message_string = display.display_string
        segments = display._logical_segments
        width_per_segment = display._width_per_segment

        def wrap_segment_message(message, segment):
            return chain(segment.position_identifier(), self._translate_string(message))

        return chain(*starmap(wrap_segment_message, izip(group(message_string, width_per_segment), segments)))

    def _build_inner_message(self, displays):
        message = list(self._build_display_message(self))
        for display in displays:
            message[display.display_slice] = self._build_display_message(display)

        return message

    def _build_message(self, displays):
        return tuple(chain(self._message_header, self._build_inner_message(displays), self._message_tail))


class SubDisplayElement(DisplayElement):

    def __init__(self, sub_display_slice = slice(1), parent_display = None, *a, **k):
        super(SubDisplayElement, self).__init__(width_in_chars=slice_size(sub_display_slice, parent_display.width), resource_type=parent_display.nested_display_resource_factory(self), *a, **k)
        self._sub_display_slice = sub_display_slice
        self._parent_display = parent_display

    @lazy_attribute
    def display_slice(self):
        return self._sub_display_slice

    @lazy_attribute
    def display_indexes(self):
        return set(range(*self._sub_display_slice.indices(self._parent_display.width)))

    def _is_visible(self):
        return self in map(first, self.resource.proxied_object.owners)

    def update(self):
        if self._is_visible():
            self._parent_display.update()