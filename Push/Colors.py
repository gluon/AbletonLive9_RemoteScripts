#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/Colors.py
"""
Module for the color interfaces defining all posible ways of turning
on buttons on Push.
"""
from itertools import izip, repeat
from _Framework.ButtonElement import Color

class NotDrawableError(Exception):
    pass


class RgbColor(Color):
    """
    An a RGB color drawable in RGB pads represented.
    """
    _rgb_value = (0, 0, 0)

    def __init__(self, midi_value = None, rgb_value = None, *a, **k):
        super(RgbColor, self).__init__(midi_value=midi_value, *a, **k)
        if rgb_value is not None:
            self._rgb_value = rgb_value

    def shade(self, shade_level):
        """
        Generate a new shaded RGB from this color.
        """
        raise shade_level > 0 and shade_level <= 2 or AssertionError
        shade_factor = 1.0 / 2.0 * (2 - shade_level)
        return RgbColor(self.midi_value + shade_level, [ a * b for a, b in izip(self._rgb_value, repeat(shade_factor)) ])

    def highlight(self):
        """
        Generate a new highlighted RGB from this color.
        """
        return RgbColor(self.midi_value - 1, [ a * b for a, b in izip(self._rgb_value, repeat(1.5)) ])

    def draw(self, interface):
        if interface.is_rgb:
            super(RgbColor, self).draw(interface)
        else:
            raise NotDrawableError, 'Rgb color ' + str(self._rgb_value) + ' not drawable in ' + interface.name

    def __iter__(self):
        return iter(self._rgb_value)

    def __getitem__(self, index_or_slice):
        return self._rgb_value[index_or_slice]


class FallbackColor(Color):
    """
    Tries to draw the color with a default color object but uses the own midi value if
    it fails. This can be used to define a color that can be either used by a bi-led
    or rgb button.
    """

    def __init__(self, default_color = None, *a, **k):
        super(FallbackColor, self).__init__(*a, **k)
        self.default_color = default_color

    def draw(self, interface):
        try:
            self.default_color.draw(interface)
        except NotDrawableError:
            super(FallbackColor, self).draw(interface)


class AnimatedColor(Color):
    """
    Creates an animation between two RGB colors.
    The animation is defined by the channel2.
    """

    @property
    def midi_value(self):
        return self.convert_to_midi_value()

    def __init__(self, color1 = RgbColor(), color2 = RgbColor(), channel2 = 7, *a, **k):
        super(AnimatedColor, self).__init__(*a, **k)
        self.color1 = color1
        self.color2 = color2
        self.channel2 = channel2

    def draw(self, interface):
        raise interface.num_delayed_messages >= 2 or AssertionError
        interface.send_value(self.color1.midi_value)
        interface.send_value(self.color2.midi_value, channel=self.channel2)

    def convert_to_midi_value(self):
        raise NotImplementedError, 'Animations cannot be serialized'


class Pulse(AnimatedColor):
    """
    Smoothly pulsates between two colors.
    """

    def __init__(self, color1 = RgbColor(), color2 = RgbColor(), speed = 6, *a, **k):
        channel2 = [4,
         6,
         12,
         24,
         48].index(speed) + 6
        super(Pulse, self).__init__(color1=color1, color2=color2, channel2=channel2, *a, **k)


class Blink(AnimatedColor):
    """
    Blinks jumping between two colors.
    """

    def __init__(self, color1 = 0, color2 = 0, speed = 6, *a, **k):
        channel2 = [4,
         6,
         12,
         24,
         48].index(speed) + 11
        super(Blink, self).__init__(color1=color1, color2=color2, channel2=channel2, *a, **k)


class Basic:
    """
    Table of basic colors for side buttons.
    """
    HALF = Color(1)
    HALF_BLINK_SLOW = Color(2)
    HALF_BLINK_FAST = Color(3)
    FULL = Color(4)
    FULL_BLINK_SLOW = Color(5)
    FULL_BLINK_FAST = Color(6)
    OFF = Color(0)
    ON = Color(127)


class Rgb:
    """
    Table of RgbColors for main matrix.
    """
    BLACK = RgbColor(0)
    DARK_GREY = RgbColor(1)
    GREY = RgbColor(2)
    WHITE = RgbColor(3)
    RED = RgbColor(5)
    AMBER = RgbColor(9)
    YELLOW = RgbColor(13)
    LIME = RgbColor(17)
    GREEN = RgbColor(21)
    SPRING = RgbColor(25)
    TURQUOISE = RgbColor(29)
    CYAN = RgbColor(33)
    SKY = RgbColor(37)
    OCEAN = RgbColor(41)
    BLUE = RgbColor(45)
    ORCHID = RgbColor(49)
    MAGENTA = RgbColor(53)
    PINK = RgbColor(57)


class BiLed:
    """
    Table of colors for scene launch buttons.
    """
    GREEN = FallbackColor(RgbColor(122), 22)
    GREEN_HALF = FallbackColor(RgbColor(123), 19)
    GREEN_BLINK_SLOW = FallbackColor(Blink(RgbColor(122), Rgb.BLACK, 4), 23)
    GREEN_BLINK_FAST = FallbackColor(Blink(RgbColor(122), Rgb.BLACK, 24), 24)
    RED = FallbackColor(RgbColor(120), 4)
    RED_HALF = FallbackColor(RgbColor(121), 1)
    RED_BLINK_SLOW = FallbackColor(Blink(RgbColor(120), Rgb.BLACK, 4), 5)
    RED_BLINK_FAST = FallbackColor(Blink(RgbColor(120), Rgb.BLACK, 24), 6)
    YELLOW = FallbackColor(RgbColor(124), 16)
    YELLOW_HALF = FallbackColor(RgbColor(125), 13)
    YELLOW_BLINK_SLOW = FallbackColor(Blink(RgbColor(124), Rgb.BLACK, 4), 17)
    YELLOW_BLINK_FAST = FallbackColor(Blink(RgbColor(124), Rgb.BLACK, 24), 18)
    AMBER = FallbackColor(RgbColor(126), 10)
    AMBER_HALF = FallbackColor(RgbColor(127), 7)
    AMBER_BLINK_SLOW = FallbackColor(Blink(RgbColor(126), Rgb.BLACK, 4), 11)
    AMBER_BLINK_FAST = FallbackColor(Blink(RgbColor(126), Rgb.BLACK, 24), 12)
    OFF = FallbackColor(Rgb.BLACK, 0)
    ON = FallbackColor(Rgb.WHITE, 127)


CLIP_COLOR_TABLE = {15549221: 60,
 12411136: 61,
 11569920: 62,
 8754719: 63,
 5480241: 64,
 695438: 65,
 31421: 66,
 197631: 67,
 3101346: 68,
 6441901: 69,
 8092539: 70,
 3947580: 71,
 16712965: 72,
 12565097: 73,
 10927616: 74,
 8046132: 75,
 4047616: 76,
 49071: 77,
 1090798: 78,
 5538020: 79,
 8940772: 80,
 10701741: 81,
 12008809: 82,
 9852725: 83,
 16149507: 84,
 12581632: 85,
 8912743: 86,
 1769263: 87,
 2490280: 88,
 6094824: 89,
 1698303: 90,
 9160191: 91,
 9611263: 92,
 12094975: 93,
 14183652: 94,
 16726484: 95,
 16753961: 96,
 16773172: 97,
 14939139: 98,
 14402304: 99,
 12492131: 100,
 9024637: 101,
 8962746: 102,
 10204100: 103,
 8758722: 104,
 13011836: 105,
 15810688: 106,
 16749734: 107,
 16753524: 108,
 16772767: 109,
 13821080: 110,
 12243060: 111,
 11119017: 112,
 13958625: 113,
 13496824: 114,
 12173795: 115,
 13482980: 116,
 13684944: 117,
 14673637: 118,
 16777215: Rgb.WHITE}
RGB_COLOR_TABLE = ((0, 0),
 (1, 1973790),
 (2, 8355711),
 (3, 16777215),
 (4, 16731212),
 (5, 16711680),
 (6, 5832704),
 (7, 1638400),
 (8, 16760172),
 (9, 16733184),
 (10, 5840128),
 (11, 2562816),
 (12, 16777036),
 (13, 16776960),
 (14, 5855488),
 (15, 1644800),
 (16, 8978252),
 (17, 5570304),
 (18, 1923328),
 (19, 1321728),
 (20, 5046092),
 (21, 65280),
 (22, 22784),
 (23, 6400),
 (24, 5046110),
 (25, 65305),
 (26, 22797),
 (27, 6402),
 (28, 5046152),
 (29, 65365),
 (30, 22813),
 (31, 7954),
 (32, 5046199),
 (33, 65433),
 (34, 22837),
 (35, 6418),
 (36, 5030911),
 (37, 43519),
 (38, 16722),
 (39, 4121),
 (40, 5015807),
 (41, 22015),
 (42, 7513),
 (43, 2073),
 (44, 5000447),
 (45, 255),
 (46, 89),
 (47, 25),
 (48, 8867071),
 (49, 5505279),
 (50, 1638500),
 (51, 983088),
 (52, 16731391),
 (53, 16711935),
 (54, 5832793),
 (55, 1638425),
 (56, 16731271),
 (57, 16711764),
 (58, 5832733),
 (59, 2228243),
 (60, 16717056),
 (61, 10040576),
 (62, 7950592),
 (63, 4416512),
 (64, 211200),
 (65, 22325),
 (66, 21631),
 (67, 255),
 (68, 17743),
 (69, 2425036),
 (70, 8355711),
 (71, 2105376),
 (72, 16711680),
 (73, 12451629),
 (74, 11529478),
 (75, 6618889),
 (76, 1084160),
 (77, 65415),
 (78, 43519),
 (79, 11007),
 (80, 4129023),
 (81, 7995647),
 (82, 11672189),
 (83, 4202752),
 (84, 16730624),
 (85, 8970502),
 (86, 7536405),
 (87, 65280),
 (88, 3931942),
 (89, 5898097),
 (90, 3735500),
 (91, 5999359),
 (92, 3232198),
 (93, 8880105),
 (94, 13835775),
 (95, 16711773),
 (96, 16744192),
 (97, 12169216),
 (98, 9502464),
 (99, 8609031),
 (100, 3746560),
 (101, 1330192),
 (102, 872504),
 (103, 1381674),
 (104, 1450074),
 (105, 6896668),
 (106, 11010058),
 (107, 14569789),
 (108, 14182940),
 (109, 16769318),
 (110, 10412335),
 (111, 6796559),
 (112, 1973808),
 (113, 14483307),
 (114, 8454077),
 (115, 10131967),
 (116, 9332479),
 (117, 4210752),
 (118, 7697781),
 (119, 14745599),
 (120, 10485760),
 (121, 3473408),
 (122, 1757184),
 (123, 475648),
 (124, 12169216),
 (125, 4141312),
 (126, 11755264),
 (127, 4920578))