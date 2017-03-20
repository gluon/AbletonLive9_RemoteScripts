# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/colors.py
# Compiled at: 2016-11-16 18:13:20
from __future__ import absolute_import, print_function
from ableton.v2.base import depends, in_range, listens, liveobj_valid, nop
from ableton.v2.control_surface.elements.color import DynamicColorBase, DynamicColorFactory
from pushbase.colors import Blink, FallbackColor, Pulse, PushColor, TransparentColor
from .device_util import find_chain_or_track
WHITE_MIDI_VALUE = 122
TRANSLATED_WHITE_INDEX = 4
WHITE_COLOR_INDEX_FROM_LIVE = 59
UNCOLORED_INDEX = WHITE_COLOR_INDEX_FROM_LIVE
HALFLIT_WHITE_MIDI = 14
DISPLAY_BUTTON_SHADE_LEVEL = 1

def make_pulsing_track_color(track, pulse_to_color):
    return Pulse(pulse_to_color, IndexedColor.from_live_index(track.color_index), 48)


def make_blinking_track_color(track, blink_to_color):
    return Blink(blink_to_color, IndexedColor.from_live_index(track.color_index), 24)


def determine_shaded_color_index(color_index, shade_level):
    if not in_range(color_index, 1, 27):
        assert color_index == WHITE_MIDI_VALUE
        assert 0 <= shade_level <= 2
        return shade_level == 0 and color_index
    else:
        if color_index == WHITE_MIDI_VALUE:
            return color_index + shade_level
        return (color_index - 1) * 2 + 64 + shade_level


class IndexedColor(PushColor):
    needs_rgb_interface = True
    midi_value = None

    def __init__(self, index=None, *a, **k):
        super(IndexedColor, self).__init__(midi_value=index, *a, **k)

    @staticmethod
    def from_push_index(index, shade_level=0):
        return IndexedColor(determine_shaded_color_index(index, shade_level))

    @staticmethod
    def from_live_index(index, shade_level=0):
        return IndexedColor(determine_shaded_color_index(translate_color_index(index), shade_level))


def translate_color_index(index):
    """
    Translates a color index coming from Live into the reduced color palette of Push
    """
    try:
        if index > -1:
            return COLOR_INDEX_TO_PUSH_INDEX[index]
        return TRANSLATED_WHITE_INDEX
    except:
        return TRANSLATED_WHITE_INDEX


def inverse_translate_color_index(translated_index):
    """
    Translates a color index coming with the reduced palette of Push [1..26] to the best
    matching color of Live [0..59].
    """
    assert 1 <= translated_index <= len(PUSH_INDEX_TO_COLOR_INDEX)
    return PUSH_INDEX_TO_COLOR_INDEX[translated_index - 1] - 1


class SelectedDrumPadColor(DynamicColorBase):
    """
    Dynamic color that sets the color of the currently selected drum pad.
    The drum rack is used from the percussion_instrument_finder.
    """

    @depends(percussion_instrument_finder=nop)
    def __init__(self, song=None, percussion_instrument_finder=None, *a, **k):
        assert liveobj_valid(song)
        super(SelectedDrumPadColor, self).__init__(*a, **k)
        self.song = song
        if percussion_instrument_finder is not None:
            self.__on_selected_track_color_index_changed.subject = self.song.view
            self.__on_instrument_changed.subject = percussion_instrument_finder
            self.__on_instrument_changed()
        return

    @listens('instrument')
    def __on_instrument_changed(self):
        drum_group = self.__on_instrument_changed.subject.drum_group
        if liveobj_valid(drum_group):
            self.__on_selected_drum_pad_chains_changed.subject = drum_group.view
            self.__on_selected_drum_pad_chains_changed()

    @listens('selected_drum_pad.chains')
    def __on_selected_drum_pad_chains_changed(self):
        drum_pad = self.__on_selected_drum_pad_chains_changed.subject.selected_drum_pad
        if liveobj_valid(drum_pad) and drum_pad.chains:
            self.__on_color_index_changed.subject = drum_pad.chains[0]
            self.__on_color_index_changed()
        else:
            self._update_midi_value(self.song.view.selected_track)

    @listens('color_index')
    def __on_color_index_changed(self):
        chain = self.__on_color_index_changed.subject
        self._update_midi_value(chain)

    @listens('selected_track.color_index')
    def __on_selected_track_color_index_changed(self):
        drum_group = self.__on_selected_drum_pad_chains_changed.subject
        drum_pad = drum_group.selected_drum_pad if liveobj_valid(drum_group) else None
        if not liveobj_valid(drum_pad) or not drum_pad.chains:
            self._update_midi_value(self.song.view.selected_track)
        return


class SelectedDrumPadColorFactory(DynamicColorFactory):

    def instantiate(self, song):
        return SelectedDrumPadColor(song=song, transformation=self._transform)


class SelectedDeviceChainColor(DynamicColorBase):

    @depends(device_provider=nop)
    def __init__(self, device_provider=None, *a, **k):
        super(SelectedDeviceChainColor, self).__init__(*a, **k)
        if device_provider is not None:
            self.__on_device_changed.subject = device_provider
            self.__on_device_changed()
        return

    @listens('device')
    def __on_device_changed(self):
        device = self.__on_device_changed.subject.device
        chain = find_chain_or_track(device)
        self.__on_chain_color_index_changed.subject = chain
        self.__on_chain_color_index_changed()

    @listens('color_index')
    def __on_chain_color_index_changed(self):
        chain = self.__on_chain_color_index_changed.subject
        if liveobj_valid(chain):
            self._update_midi_value(chain)


class SelectedDeviceChainColorFactory(DynamicColorFactory):

    def instantiate(self, song):
        return SelectedDeviceChainColor(transformation=self._transform)


def make_color_factory_func(factory_class):

    def make_color_factory(shade_level=0):
        return factory_class(transformation=lambda color_index: determine_shaded_color_index(translate_color_index(color_index), shade_level))

    return make_color_factory


class Rgb:
    AMBER = IndexedColor(3)
    AMBER_SHADE = IndexedColor(69)
    AMBER_SHADE_TWO = IndexedColor(70)
    YELLOW = IndexedColor(6)
    YELLOW_SHADE = IndexedColor(75)
    YELLOW_SHADE_TWO = IndexedColor(76)
    YELLOW_HIGHLIGHT = IndexedColor(40)
    PURPLE = IndexedColor(49)
    OCEAN = IndexedColor(33)
    DEEP_OCEAN = IndexedColor(95)
    SKY = IndexedColor(46)
    GREEN = IndexedColor(126)
    GREEN_SHADE = IndexedColor(32)
    RED = IndexedColor(127)
    RED_SHADE = IndexedColor(27)
    RED_SHADE_TWO = IndexedColor(66)
    BLUE = IndexedColor(125)
    LIGHT_GREY = IndexedColor(123)
    DARK_GREY = IndexedColor(124)
    BLACK = IndexedColor(0)
    WHITE = IndexedColor(WHITE_MIDI_VALUE)


class Basic:
    HALF = FallbackColor(Rgb.DARK_GREY, HALFLIT_WHITE_MIDI)
    OFF = FallbackColor(Rgb.BLACK, 0)
    ON = FallbackColor(Rgb.WHITE, 127)
    FULL_BLINK_SLOW = Blink(FallbackColor(Rgb.WHITE, 127), FallbackColor(Rgb.BLACK, 0), 24)
    FULL_PULSE_SLOW = Pulse(FallbackColor(Rgb.DARK_GREY, HALFLIT_WHITE_MIDI), FallbackColor(Rgb.WHITE, 127), 48)
    FAST_PULSE = Pulse(FallbackColor(Rgb.DARK_GREY, HALFLIT_WHITE_MIDI), FallbackColor(Rgb.WHITE, 127), 24)
    TRANSPARENT = TransparentColor()


COLOR_INDEX_TO_PUSH_INDEX = (1, 4, 4, 10, 9, 13, 17, 16, 17, 18, 4, 4, 1, 5, 10, 10,
                             9, 12, 15, 16, 20, 22, 24, 4, 3, 7, 8, 8, 11, 14, 14,
                             15, 19, 20, 21, 25, 3, 6, 6, 6, 4, 9, 12, 15, 17, 2,
                             23, 2, 2, 5, 7, 10, 4, 11, 15, 19, 26, 4, 4, 4)
PUSH_INDEX_TO_COLOR_INDEX = (1, 48, 37, 41, 50, 38, 26, 28, 17, 16, 29, 18, 6, 31,
                             19, 20, 7, 10, 33, 21, 35, 22, 47, 23, 36, 57)
COLOR_TABLE = (
 (0, 0, 0),
 (1, 15865344, 2),
 (2, 16728114, 4),
 (3, 16541952, 6),
 (4, 9331486, 8),
 (5, 16440379, 10),
 (6, 16762134, 12),
 (7, 11992846, 14),
 (8, 7995160, 16),
 (9, 3457558, 18),
 (10, 5212676, 20),
 (11, 6487893, 22),
 (12, 2719059, 24),
 (13, 2843699, 26),
 (14, 3255807, 28),
 (15, 3564540, 30),
 (16, 1717503, 32),
 (17, 1391001, 34),
 (18, 1838310, 36),
 (19, 3749887, 38),
 (20, 5710591, 40),
 (21, 9907199, 42),
 (22, 8724856, 44),
 (23, 16715826, 46),
 (24, 11022396, 48),
 (25, 16722900, 50),
 (26, 15427065, 52),
 (27, 10892321, 54),
 (28, 10049064, 56),
 (29, 8873728, 58),
 (30, 9470495, 60),
 (31, 4884224, 62),
 (32, 32530, 64),
 (33, 1594290, 66),
 (34, 6441901, 68),
 (35, 7551591, 70),
 (36, 16301231, 72),
 (37, 16751478, 74),
 (38, 16760671, 76),
 (39, 14266225, 78),
 (40, 16774272, 80),
 (41, 12565097, 80),
 (42, 12373128, 81),
 (43, 11468697, 81),
 (44, 8183199, 82),
 (45, 9024637, 82),
 (46, 8451071, 83),
 (47, 8048380, 83),
 (48, 6857171, 84),
 (49, 8753090, 85),
 (50, 12298994, 85),
 (51, 13482980, 86),
 (52, 15698864, 86),
 (53, 8756620, 87),
 (54, 7042414, 87),
 (55, 8687771, 88),
 (56, 6975605, 88),
 (57, 8947101, 89),
 (58, 7105141, 90),
 (59, 10323356, 90),
 (60, 7629428, 91),
 (61, 10263941, 91),
 (62, 7632234, 92),
 (63, 10323076, 92),
 (64, 7694954, 93),
 (65, 6293504, 93),
 (66, 2032128, 94),
 (67, 6691092, 94),
 (68, 2164742, 95),
 (69, 6564352, 96),
 (70, 2100480, 96),
 (71, 4665615, 97),
 (72, 1839878, 97),
 (73, 6576151, 98),
 (74, 2104327, 98),
 (75, 6704648, 99),
 (76, 2169090, 99),
 (77, 4744709, 100),
 (78, 1515777, 101),
 (79, 3171849, 101),
 (80, 991491, 102),
 (81, 1330440, 102),
 (82, 399618, 103),
 (83, 2045697, 103),
 (84, 659712, 104),
 (85, 2582050, 104),
 (86, 794891, 105),
 (87, 1326633, 106),
 (88, 530704, 106),
 (89, 1389081, 107),
 (90, 529418, 107),
 (91, 1262950, 108),
 (92, 398881, 108),
 (93, 1386340, 109),
 (94, 461856, 109),
 (95, 660582, 110),
 (96, 198177, 110),
 (97, 662604, 111),
 (98, 264990, 112),
 (99, 722012, 112),
 (100, 196893, 113),
 (101, 1447526, 113),
 (102, 460577, 114),
 (103, 2231654, 114),
 (104, 721953, 115),
 (105, 3936614, 115),
 (106, 1246497, 116),
 (107, 3476784, 117),
 (108, 1115151, 117),
 (109, 6686228, 118),
 (110, 2163206, 118),
 (111, 4395800, 119),
 (112, 1377799, 119),
 (113, 6689108, 120),
 (114, 2163995, 120),
 (115, 6170723, 121),
 (116, 1969440, 122),
 (117, 0, 122),
 (118, 5855577, 123),
 (119, 1710618, 123),
 (120, 16777215, 124),
 (121, 5855577, 124),
 (122, 13421772, 125),
 (123, 4210752, 125),
 (124, 1315860, 126),
 (125, 255, 126),
 (126, 65280, 127),
 (127, 16711680, 127))