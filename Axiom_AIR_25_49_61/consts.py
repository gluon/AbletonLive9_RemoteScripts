#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Axiom_AIR_25_49_61/consts.py
SYSEX_START = (240, 0, 1, 5, 32, 127)
IDENTITY_REQUEST = (240, 126, 127, 6, 1, 247)
AXIOM_AIR_RESPONSE = (240, 126, 127, 6, 2, 0, 1, 5, 99, 14)
AXIOM_REV4_RESPONSE = (49, 48, 49)
AXIOM_R4_FULL_RESPONSE = (240, 126, 127, 6, 2, 0, 1, 5, 99, 14, 51, 64, 49, 48, 49, 48, 247)
ENGAGE_HYPERCONTROL = (32, 62, 247)
ENGAGE_HYPERCL_NO_PADS = (32, 58, 247)
SPECIAL_HYPERCONTROL = (33, 9, 247)
DISABLE_HYPERCONTROL = (32, 0, 247)
REQUEST_HYPERCONTROL = (240, 0, 1, 5, 34, 127, 7, 2)
LCD_ALL_ON = (22, 31, 127, 127, 127, 247)
LCD_ALL_OFF = (22, 0, 0, 0, 0, 0)
LCD_HC_DEFAULT = (22, 18, 4, 64, 1, 247)
CLEAR_ALL = (16, 247)
CLEAR_VALUE = (187, 21, 0)
CLEAR_BANK = (187, 22, 0)
CLEAR_PAD = (187, 23, 0)
CLEAR_KNOB = (187, 24, 0)
CLEAR_NAME = (187, 25, 0)
DISPLAY_WORD_ON = (240, 0, 1, 5, 32, 127, 20, 49, 48, 50, 53, 0, 247)
DISPLAY_WORD_OFF = (240, 0, 1, 5, 32, 127, 20, 49, 48, 50, 52, 0, 247)
HC_BYTE = 62
ENCODERS = 2
PADS = 4
FADERS = 8
NAVIGATION = 16
TRANSPORT = 32
KEYBOARD = 64
IS_MOMENTARY = True
NUM_TRACKS = 8
GLOBAL_CHANNEL = 15
GLOBAL_SEND_CHANNEL = 12
INITIAL_DISPLAY_DELAY = 15
STANDARD_DISPLAY_DELAY = 15
PAD_TRANSLATIONS = ((0, 0, 85, 14),
 (1, 0, 86, 14),
 (2, 0, 87, 14),
 (3, 0, 88, 14),
 (0, 1, 81, 14),
 (1, 1, 82, 14),
 (2, 1, 83, 14),
 (3, 1, 84, 14),
 (0, 2, 85, 15),
 (1, 2, 86, 15),
 (2, 2, 87, 15),
 (3, 2, 88, 15),
 (0, 3, 81, 15),
 (1, 3, 82, 15),
 (2, 3, 83, 15),
 (3, 3, 84, 15))
ETCHINGS = ['track',
 'inst_fx',
 'memory',
 'parameter',
 'value',
 'pan',
 'l',
 'r',
 'program',
 'volume',
 'edit',
 'channel',
 'strip',
 'hyper',
 'page',
 'send',
 'bank',
 'pad',
 'knob',
 'fader',
 'button']
LED_OFF = 0
GRN_LOW = 1
RED_LOW = 2
AMB_LOW = 3
GRN_HALF = 17
RED_HALF = 18
AMB_HALF = 19
GRN_HIGH = 33
RED_HIGH = 34
AMB_HIGH = 35
GRN_FULL = 49
RED_FULL = 50
AMB_FULL = 51