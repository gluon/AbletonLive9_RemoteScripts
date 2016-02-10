#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Tranzport/consts.py
NOTE_OFF_STATUS = 128
NOTE_ON_STATUS = 144
CC_STATUS = 176
NUM_NOTES = 127
NUM_CC_NO = 127
NUM_CHANNELS = 15
NUM_PAGES = 4
PAGES_NAMES = (('P', 'o', 's', 'i', 't', 'i', 'o', 'n', ' ', '&', ' ', 'T', 'e', 'm', 'p', 'o'),
 ('C', 'l', 'i', 'p', ' ', '&', ' ', 'T', 'e', 'm', 'p', 'o'),
 ('V', 'o', 'l', 'u', 'm', 'e', ' ', '&', ' ', 'P', 'a', 'n', 'n', 'i', 'n', 'g'),
 ('L', 'o', 'o', 'p', ' ', 'S', 'e', 't', 't', 'i', 'n', 'g', 's'),
 ('S', 'e', 'n', 'd', ' ', 'S', 'e', 't', 't', 'i', 'n', 'g', 's'))
TRANZ_NATIVE_MODE = (240, 0, 1, 64, 16, 1, 0, 247)
TRANZ_TRANS_SECTION = range(91, 96)
TRANZ_RWD = 91
TRANZ_FFWD = 92
TRANZ_STOP = 93
TRANZ_PLAY = 94
TRANZ_REC = 95
TRANZ_PREV_TRACK = 48
TRANZ_NEXT_TRACK = 49
TRANZ_ARM_TRACK = 0
TRANZ_MUTE_TRACK = 16
TRANZ_SOLO_TRACK = 8
TRANZ_ANY_SOLO = 115
TRANZ_TRACK_SECTION = (TRANZ_PREV_TRACK,
 TRANZ_NEXT_TRACK,
 TRANZ_ARM_TRACK,
 TRANZ_MUTE_TRACK,
 TRANZ_SOLO_TRACK,
 TRANZ_ANY_SOLO)
TRANZ_LOOP = 86
TRANZ_PUNCH_IN = 87
TRANZ_PUNCH_OUT = 88
TRANZ_PUNCH = 120
TRANZ_LOOP_SECTION = (TRANZ_LOOP,
 TRANZ_PUNCH_IN,
 TRANZ_PUNCH_OUT,
 TRANZ_PUNCH)
TRANZ_PREV_CUE = 84
TRANZ_ADD_CUE = 82
TRANZ_NEXT_CUE = 85
TRANZ_CUE_SECTION = (TRANZ_PREV_CUE, TRANZ_ADD_CUE, TRANZ_NEXT_CUE)
TRANZ_UNDO = 76
TRANZ_SHIFT = 121
TRANZ_DICT = {'0': 48,
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
 '.': 46,
 ',': 44,
 ':': 58,
 ';': 59,
 '<': 60,
 '>': 62,
 '[': 91,
 ']': 93,
 '_': 95,
 '-': 16,
 '|': 124,
 '&': 38}
SYSEX_START = (240, 0, 1, 64, 16, 0)
SYSEX_END = (247,)
CLEAR_LINE = (32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32)
LED_ON = 127
LED_OFF = 0