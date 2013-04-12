#Embedded file name: C:\ProgramData\Ableton\Live 9 Beta\Resources\MIDI Remote Scripts\Maschine_Mk2\MIDI_Map.py
from PadScale import PadScale
msg_sender = None

def register_sender(sender):
    global msg_sender
    msg_sender = sender


def debug_out(message):
    msg_sender.log_message(message)


USE_DISPLAY = False
PM_OFF = 0
PM_ON = 1
SCENE_MODE = 1
CLIP_MODE = 2
PAD_MODE = 3
CONTROL_MODE = 4
STEP1 = 1
STEP4 = 4
MODE_PRESS_NONE = 0
MODE_PRESS_SELECT = 1
MODE_PRESS_SOLO = 2
SCENE_MODE_NORMAL = 0
SCENE_MODE_MUTE = 1
SCENE_MODE_SELECT = 2
SCENE_MODE_SOLO = 3
SCENE_MODE_ARM = 4
SCENE_MODE_STOP = 5
SCENE_MODE_CONTROL = 6
SCENE_MODE_XFADE = 7
BASIC_CHANNEL = 3
DEVICE_CC_OFF = 40
DEVICE_BUTTON_CC_OFF = 100
LEVEL_CC_OFF = 10
PAN_CC_OFF = 20
SEND_CC_OFF = 30
STOP_CC_OFF = 50
MUTE_CC_OFF = 80
SOLO_CC_OFF = 90
ARM_CC_OFF = 60
SELECT_CC_OFF = 70
CONTROL_LEVEL = 0
CONTROL_PAN = 1
CONTROL_SEND = 2
CONTROL_DEVICE = 3
SHIFT_INC = 4
INIT_SLOT = 10
CLICK_TIME = 500
ND_BASE_OTHER = 0
ND_KEYBOARD1 = 1
ND_INTERVAL = 2
SENDS = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P')
BASE_NOTE = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
VIEWS_ALL = ('Session', 'Detail/Clip', 'Detail/DeviceChain', 'Browser', 'Arranger')
VIEWS = ('Browser', 'Detail/Clip', 'Detail/DeviceChain', 'Session')
CLIPNOTEMAP = ((24, 25, 26, 27),
 (20, 21, 22, 23),
 (16, 17, 18, 19),
 (12, 13, 14, 15))
SCALES = (PadScale('Chromatic', (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)),
 PadScale('Ionian/Major', (0, 2, 4, 5, 7, 9, 11)),
 PadScale('Aeolian/Minor', (0, 2, 3, 5, 7, 8, 10)),
 PadScale('Pentatonic', (0, 2, 4, 7, 9)),
 PadScale('Pentatonic Minor', (0, 3, 5, 7, 10)),
 PadScale('Dorian (B/g)', (0, 2, 3, 5, 7, 9, 10)),
 PadScale('Phrygian (A-flat/f)', (0, 1, 3, 5, 7, 8, 10)),
 PadScale('Lydian (D/e)', (0, 2, 4, 6, 7, 9, 11)),
 PadScale('Mixolydian (F/d)', (0, 2, 4, 5, 7, 9, 10)),
 PadScale('Locrian (D-flat/b-flat)', (0, 1, 3, 5, 6, 8, 10)),
 PadScale('Diminish', (0, 2, 3, 5, 6, 8, 9, 10, 11)),
 PadScale('Major Blues', (0, 3, 4, 7, 9, 10)),
 PadScale('Minor Blues', (0, 3, 4, 6, 7, 10)),
 PadScale('Whole', (0, 2, 4, 6, 8, 10)),
 PadScale('Arabian', (0, 2, 4, 5, 6, 8, 10)),
 PadScale('Egyptian', (0, 2, 5, 7, 10)),
 PadScale('Gypsi', (0, 2, 3, 6, 7, 8, 11)),
 PadScale('Spanish Scale', (0, 1, 3, 4, 5, 7, 8, 10)),
 PadScale('Raga Bhairav', (0, 1, 4, 5, 7, 8, 11)),
 PadScale('Raga Gamanasrama', (0, 1, 4, 6, 7, 9, 11)),
 PadScale('Rag Todi', (0, 1, 3, 6, 7, 8, 11)),
 PadScale('3rd (C,E,G#)', (0, 4, 8)),
 PadScale('4th (C,F,A#)', (0, 5, 10)),
 PadScale('5th', (0, 7)),
 PadScale('Octave', tuple([0])))
PADCHANNEL = 0
DRUM_PADS = (-1, 12, 13, 14, 15, 8, 9, 10, 11, 4, 5, 6, 7, 0, 1, 2, 3)
KEY_COLOR_MODES_STRINGS = ('Intervals', 'Individual Colors')
COLOR_HUE_NAV = 84
COLOR_BRIGHTNESS_OFF = 30
KEY_COLOR_MAP = {0: ((0, 127, 127), (0, 127, 50)),
 1: ((0, 100, 115), (0, 100, 30)),
 2: ((8, 127, 127), (8, 127, 50)),
 3: ((8, 127, 115), (8, 100, 30)),
 4: ((20, 127, 127), (20, 127, 50)),
 5: ((40, 127, 127), (40, 127, 30)),
 6: ((48, 100, 115), (48, 100, 30)),
 7: ((60, 127, 127), (60, 127, 50)),
 8: ((75, 90, 115), (75, 90, 50)),
 9: ((86, 127, 127), (86, 127, 50)),
 10: ((100, 10, 115), (100, 10, 30)),
 11: ((115, 127, 127), (115, 127, 50))}
INTERVAL_COLOR_MAP = {0: ((0, 127, 127), (0, 127, 30)),
 1: ((0, 40, 100), (0, 40, 30)),
 2: ((8, 127, 127), (8, 127, 30)),
 3: ((16, 127, 127), (16, 127, 30)),
 4: ((40, 127, 127), (40, 127, 30)),
 5: ((30, 127, 127), (30, 127, 30)),
 6: ((60, 127, 127), (60, 127, 30)),
 7: ((120, 127, 127), (120, 127, 30)),
 8: ((60, 60, 127), (60, 60, 30)),
 9: ((85, 127, 127), (85, 127, 30)),
 10: ((75, 127, 127), (75, 127, 30)),
 11: ((100, 127, 127), (100, 127, 30))}

def enum(**enums):
    return type('Enum', (), enums)


PColor = enum(CLIP_PLAY=((36, 127, 127), (36, 100, 30)), CLIP_STOPPED=((14, 127, 127), (14, 100, 30)), CLIP_RECORD=((0, 127, 127), (0, 127, 30)), CLIP_GROUP_PLAY=((43, 127, 110), (43, 127, 10)), CLIP_GROUP_CONTROL=((6, 127, 110), (6, 127, 10)), CLIP_GROUP_TRIGGER=((36, 127, 110), (36, 127, 10)), XFADE_A=((10, 127, 127), (10, 127, 127)), XFADE_BOTH=((65, 127, 5), (65, 127, 5)), XFADE_B=((4, 127, 127), (4, 127, 127)), STOP_G_PLAY=((96, 127, 127), (96, 127, 20)), STOP_G_NO_PLAY=((9, 127, 127), (9, 127, 20)), STOP_PLAY=((80, 127, 127), (80, 127, 20)), STOP_NO_PLAY=((14, 127, 127), (14, 127, 20)), STOP_NO_CLIPS=((16, 100, 40), (16, 100, 20)), ARM_MIDI=((0, 127, 127), (0, 127, 20)), ARM_AUDIO=((125, 127, 127), (125, 127, 20)), ARM_OTHER=((2, 127, 127), (0, 127, 20)), ARM_NO_ARM=((2, 80, 30), (2, 80, 30)), MUTE_TRACK=((22, 127, 127), (22, 127, 20)), SOLO_TRACK=((85, 127, 127), (85, 127, 25)), SELECT=((64, 127, 127), (64, 127, 10)), DEVICE_ON_OFF=((97, 80, 120), (97, 80, 50)), DEVICE_LEFT=((3, 127, 127), (3, 127, 110)), DEVICE_RIGHT=((5, 127, 127), (5, 127, 110)), BANK_LEFT=((90, 127, 127), (90, 127, 20)), BANK_RIGHT=((90, 127, 127), (90, 127, 20)), MIX_SELECT_SEND=((21, 127, 127), (21, 127, 20)), SCENE_PLAYING=((36, 127, 127), (36, 100, 25)), SCENE_HASCLIPS=((27, 127, 127), (27, 127, 25)), SCENE_NO_CLIPS=((65, 127, 127), (65, 127, 8)), MIX_SEL_VOLUME=((45, 127, 127), (45, 127, 20)), MIX_SEL_PANNING=((3, 127, 127), (3, 127, 20)), MIX_SEL_SEND=((70, 127, 127), (70, 127, 20)), MIX_SEL_DEVICE=((110, 127, 127), (110, 100, 20)), MIX_MODE_VOLUME=((32, 127, 127), (32, 127, 8)), MIX_MODE_PANNING=((0, 127, 127), (0, 127, 8)), MIX_MODE_SEND=((60, 127, 127), (60, 127, 8)), MIX_MODE_DEVICE=((95, 127, 127), (95, 100, 8)))

def device_get_color(mode, ind):
    if mode == CONTROL_LEVEL:
        return PColor.MIX_SEL_VOLUME[ind]
    elif mode == CONTROL_PAN:
        return PColor.MIX_SEL_PANNING[ind]
    elif mode == CONTROL_SEND:
        return PColor.MIX_SEL_SEND[ind]
    elif mode == CONTROL_DEVICE:
        return PColor.MIX_SEL_DEVICE[ind]


def device_get_mode_color(mode, ind):
    if mode == CONTROL_LEVEL:
        return PColor.MIX_MODE_VOLUME[ind]
    elif mode == CONTROL_PAN:
        return PColor.MIX_MODE_PANNING[ind]
    elif mode == CONTROL_SEND:
        return PColor.MIX_MODE_SEND[ind]
    elif mode == CONTROL_DEVICE:
        return PColor.MIX_MODE_DEVICE[ind]