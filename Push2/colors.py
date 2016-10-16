#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/colors.py
from __future__ import absolute_import, print_function
from ableton.v2.base.util import in_range
from pushbase.colors import Blink, FallbackColor, Pulse, PushColor
WHITE_MIDI_VALUE = 122
TRANSLATED_WHITE_INDEX = 5
WHITE_COLOR_INDEX_FROM_LIVE = 59
UNCOLORED_INDEX = WHITE_COLOR_INDEX_FROM_LIVE
HALFLIT_WHITE_MIDI = 14

def make_pulsing_track_color(track, pulse_to_color):
    return Pulse(pulse_to_color, IndexedColor(translate_color_index(track.color_index)), 48)


def make_blinking_track_color(track, blink_to_color):
    return Blink(blink_to_color, IndexedColor(translate_color_index(track.color_index)), 24)


def determine_shaded_color_index(color_index, shade_level):
    raise in_range(color_index, 1, 27) or AssertionError
    raise shade_level in (1, 2) or AssertionError
    return (color_index - 1) * 2 + 64 + shade_level


class TransparentColor(object):
    """
    Color that does not transmit any MIDI data.
    """

    def draw(self, interface):
        pass


class IndexedColor(PushColor):
    needs_rgb_interface = True
    midi_value = None

    def __init__(self, index = None, *a, **k):
        super(IndexedColor, self).__init__(midi_value=index, *a, **k)


def translate_color_index(index):
    try:
        if index > -1:
            return COLOR_INDEX_TO_PUSH_INDEX[index]
        return TRANSLATED_WHITE_INDEX
    except:
        return TRANSLATED_WHITE_INDEX


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


COLOR_INDEX_TO_PUSH_INDEX = (1, 1, 4, 10, 9, 13, 17, 16, 17, 18, 19, 16, 1, 5, 10, 10, 9, 12, 15, 19, 20, 22, 24, 1, 1, 7, 8, 8, 11, 14, 14, 15, 19, 20, 21, 25, 3, 6, 6, 6, 4, 9, 12, 15, 17, 2, 23, 26, 2, 5, 7, 10, 9, 11, 15, 19, 26, 14, 26, 5)
COLOR_TABLE = ((0, 0, 0),
 (1, 16720932, 2),
 (2, 15874572, 4),
 (3, 16750848, 6),
 (4, 10914134, 8),
 (5, 15595866, 10),
 (6, 12688648, 12),
 (7, 16776960, 14),
 (8, 5685011, 16),
 (9, 2917379, 18),
 (10, 2386724, 20),
 (11, 1703728, 22),
 (12, 1414515, 24),
 (13, 1534800, 26),
 (14, 65535, 28),
 (15, 29948, 30),
 (16, 2576332, 32),
 (17, 17548, 34),
 (18, 6572761, 36),
 (19, 5062560, 38),
 (20, 8847615, 40),
 (21, 15095779, 42),
 (22, 6684825, 44),
 (23, 16711833, 46),
 (24, 10570847, 48),
 (25, 16731588, 50),
 (26, 15436769, 52),
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
 (65, 5049099, 93),
 (66, 1704964, 94),
 (67, 5050884, 94),
 (68, 1705473, 95),
 (69, 5058048, 96),
 (70, 1707776, 96),
 (71, 4207649, 97),
 (72, 1709325, 97),
 (73, 5064991, 98),
 (74, 1710090, 98),
 (75, 4207362, 99),
 (76, 1709313, 99),
 (77, 5065984, 100),
 (78, 1710592, 101),
 (79, 1851399, 101),
 (80, 727555, 102),
 (81, 1127169, 102),
 (82, 265472, 103),
 (83, 1127185, 103),
 (84, 265476, 104),
 (85, 675082, 104),
 (86, 203269, 105),
 (87, 471847, 106),
 (88, 134410, 106),
 (89, 1068345, 107),
 (90, 199946, 107),
 (91, 19789, 108),
 (92, 6682, 108),
 (93, 9037, 109),
 (94, 3098, 109),
 (95, 792896, 110),
 (96, 132365, 110),
 (97, 9549, 111),
 (98, 3098, 112),
 (99, 2300493, 112),
 (100, 788762, 113),
 (101, 2432589, 113),
 (102, 789018, 114),
 (103, 3539046, 114),
 (104, 851994, 115),
 (105, 5053772, 115),
 (106, 1706521, 116),
 (107, 3342413, 117),
 (108, 1114138, 117),
 (109, 5046318, 118),
 (110, 1703951, 118),
 (111, 5055533, 119),
 (112, 1707023, 119),
 (113, 5052219, 120),
 (114, 1706004, 120),
 (115, 5057865, 121),
 (116, 1707800, 122),
 (117, 0, 122),
 (118, 5855577, 123),
 (119, 1710618, 123),
 (120, 16777215, 124),
 (121, 5855577, 124),
 (122, 16777215, 125),
 (123, 5855577, 125),
 (124, 1710618, 126),
 (125, 255, 126),
 (126, 65280, 127),
 (127, 16711680, 127))