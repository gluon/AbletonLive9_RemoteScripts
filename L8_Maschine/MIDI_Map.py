#Embedded file name: C:\ProgramData\Ableton\Live 8\Resources\MIDI Remote Scripts\Maschine_Mk1\MIDI_Map.py
from PadScale import PadScale
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
COLOR_OFF = 0
COLOR_ON = 1
COLOR_BLINK = 2
COLOR_FBLINK = 3
CONTROL_LEVEL = 0
CONTROL_PAN = 1
CONTROL_SEND = 2
CONTROL_DEVICE = 3
CLICK_TIME = 500
SHIFT_INC = 4
INIT_SLOT = 10
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