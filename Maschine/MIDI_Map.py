#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\MIDI_Map.py
import Live
import re
from PadScale import PadScale
RecordingQuantization = Live.Song.RecordingQuantization
_color_table = {}
msg_sender = None

def register_sender(sender):
    global msg_sender
    msg_sender = sender


def debug_out(message):
    msg_sender.log_message(message)


def vindexof(list, element):
    index = 0
    for ele in list:
        if ele == element:
            return index
        index = index + 1


def arm_exclusive(song, track = None):
    if not track:
        track = song.view.selected_track
    if track and track.can_be_armed and not track.arm:
        tracks = song.tracks
        for songtrack in tracks:
            if songtrack != track and songtrack and songtrack.can_be_armed and songtrack.arm:
                songtrack.arm = False

        track.arm = True


def track_index(song, track):
    if track == song.master_track:
        return (0, TYPE_TRACK_MASTER)
    list = song.tracks
    index = 0
    for tr in list:
        if tr == track:
            return (index, TYPE_TRACK_SESSION)
        index += 1

    list = song.return_tracks
    index = 0
    for tr in list:
        if tr == track:
            return (index, TYPE_TRACK_RETURN)
        index += 1


def toHSB(rgb_val):
    if _color_table.has_key(rgb_val):
        return _color_table[rgb_val]
    rv = rgb_val / 65536
    rp = rv * 65536
    gv = (rgb_val - rp) / 256
    gp = gv * 256
    bv = rgb_val - rp - gp
    rgb_max = max(max(rv, gv), bv)
    rgb_min = min(min(rv, gv), bv)
    bright = rgb_max
    if bright == 0:
        color = ((10, 10, 60), (10, 60, 10))
        _color_table[rgb_val] = color
        return color
    sat = 255 * (rgb_max - rgb_min) / bright
    if sat == 0:
        sat = 0
        hue = 0
        color = ((hue, sat, min(bright / 2, 127)), (hue, sat, bright / 4))
        _color_table[rgb_val] = color
        return color
    hue = 0
    if rgb_max == rv:
        hue = 0 + 43 * (gv - bv) / (rgb_max - rgb_min)
    elif rgb_max == gv:
        hue = 85 + 43 * (bv - rv) / (rgb_max - rgb_min)
    else:
        hue = 171 + 43 * (rv - gv) / (rgb_max - rgb_min)
    if hue < 0:
        hue = 256 + hue
    color = ((hue / 2, min(sat / 2 + 20, 127), bright / 2), (hue / 2, min(sat / 2 + 15, 127), max(bright / 2 - 90, 5)))
    _color_table[rgb_val] = color
    return color


TYPE_TRACK_SESSION = 0
TYPE_TRACK_RETURN = 1
TYPE_TRACK_MASTER = 2
USE_DISPLAY = True
PM_OFF = 0
PM_ON = 1
OTHER_MODE = 0
SCENE_MODE = 1
CLIP_MODE = 2
PAD_MODE = 3
CONTROL_MODE = 4
STEP1 = 1
STEP4 = 4
MODE_PRESS_NONE = 0
MODE_PRESS_SELECT = 1
MODE_PRESS_SOLO = 2
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
QUANT_CONST = [RecordingQuantization.rec_q_no_q,
 RecordingQuantization.rec_q_quarter,
 RecordingQuantization.rec_q_eight,
 RecordingQuantization.rec_q_eight_triplet,
 RecordingQuantization.rec_q_eight_eight_triplet,
 RecordingQuantization.rec_q_sixtenth,
 RecordingQuantization.rec_q_sixtenth_triplet,
 RecordingQuantization.rec_q_sixtenth_sixtenth_triplet,
 RecordingQuantization.rec_q_thirtysecond]
QUANT_STRING = ['None',
 '1/4',
 '1/8',
 '1/8T',
 '1/8+1/8T',
 '1/16',
 '1/16T',
 '1/16+1/16T',
 '1/32']
AUTO_NAME = ((re.compile('kick|bd|bassdrum', re.IGNORECASE), ((0, 127, 40), (0, 127, 127))),
 (re.compile('snare|sn|sd', re.IGNORECASE), ((82, 127, 40), (82, 127, 127))),
 (re.compile('tom|tm|strike', re.IGNORECASE), ((12, 127, 40), (12, 127, 127))),
 (re.compile('crash|crsh', re.IGNORECASE), ((100, 94, 40), (100, 94, 127))),
 (re.compile('ride|rd', re.IGNORECASE), ((90, 127, 40), (90, 127, 127))),
 (re.compile('hit|strike|metal', re.IGNORECASE), ((115, 127, 40), (115, 127, 127))),
 (re.compile('shaker|tamb', re.IGNORECASE), ((13, 127, 40), (13, 127, 127))),
 (re.compile('clp|clap|hand|slap', re.IGNORECASE), ((70, 100, 40), (70, 100, 127))),
 (re.compile('rim|rm|stick', re.IGNORECASE), ((85, 94, 40), (85, 94, 127))),
 (re.compile('(bell|tri|gong|clav)', re.IGNORECASE), ((67, 127, 40), (67, 127, 127))),
 (re.compile('(perc|cong|bong|ag)', re.IGNORECASE), ((127, 100, 40), (127, 100, 127))),
 (re.compile('(glitch|fx|noise)', re.IGNORECASE), ((21, 127, 40), (21, 127, 127))),
 (re.compile('((hat|hh)(.*)(cl))|((cl)(.*)(hihat|hh)|ch)', re.IGNORECASE), ((29, 127, 40), (29, 127, 127))),
 (re.compile('((hat|hh)(.*)(op))|((op)(.*)(hihat|hh)|oh)', re.IGNORECASE), ((40, 127, 40), (40, 127, 127))),
 (re.compile('(hh|hat|click)', re.IGNORECASE), ((47, 127, 40), (47, 127, 127))))
DEFAULT_DRUM_COLOR = ((10, 100, 40), (10, 100, 127))
PAD_TRANSLATIONS = ((0, 0, 24, 0),
 (1, 0, 25, 0),
 (2, 0, 26, 0),
 (3, 0, 27, 0),
 (0, 1, 20, 0),
 (1, 1, 21, 0),
 (2, 1, 22, 0),
 (3, 1, 23, 0),
 (0, 2, 16, 0),
 (1, 2, 17, 0),
 (2, 2, 18, 0),
 (3, 2, 19, 0),
 (0, 3, 12, 0),
 (1, 3, 13, 0),
 (2, 3, 14, 0),
 (3, 3, 15, 0))
FEEDBACK_CHANNELS = range(0, 4)
PAD_FEEDBACK_CHANNEL = 10
NON_FEEDBACK_CHANNEL = 15
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
COLOR_HUE_NAV4 = 98
COLOR_BRIGHTNESS_OFF = 30
KEY_COLOR_MAP = {0: ((0, 127, 127, 0, 0), (0, 127, 20, 1, 0)),
 1: ((0, 100, 115, 1, 0), (0, 100, 20, 0, 0)),
 2: ((8, 127, 127, 0, 0), (8, 127, 20, 1, 0)),
 3: ((8, 127, 115, 1, 0), (8, 100, 20, 0, 0)),
 4: ((20, 127, 127, 0, 0), (20, 127, 20, 1, 0)),
 5: ((40, 127, 127, 0, 0), (40, 127, 20, 1, 0)),
 6: ((48, 100, 115, 1, 0), (48, 100, 20, 0, 0)),
 7: ((60, 127, 127, 0, 0), (60, 127, 20, 1, 0)),
 8: ((75, 90, 115, 1, 0), (75, 90, 20, 0, 0)),
 9: ((86, 127, 127, 0, 0), (86, 127, 20, 1, 0)),
 10: ((100, 10, 115, 1, 0), (100, 10, 20, 0, 0)),
 11: ((115, 127, 127, 0, 0), (115, 127, 20, 1, 0))}
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


OFF_COLOR = (0, 0, 0, 0, 0)
PColor = enum(CLIP_PLAY=((36, 127, 127, 1, 1), (36, 100, 30, 1, 0)), CLIP_STOPPED=((14, 127, 127, 1, 0), (14, 100, 30, 1, 0)), CLIP_RECORD=((0, 127, 127, 1, 1), (0, 127, 30, 1, 0)), CLIP_RECORD_TRIGGER=((0, 127, 127, 1, 2), (0, 127, 30, 1, 0)), CLIP_GROUP_PLAY=((43, 127, 110, 1, 0), (43, 127, 10, 1, 0)), CLIP_GROUP_CONTROL=((6, 127, 110, 1, 0), (6, 127, 10, 1, 0)), CLIP_GROUP_TRIGGER=((36, 127, 110, 1, 2), (36, 127, 10, 1, 0)), CLIP_PLAY_TRIGGER=((36, 127, 127, 1, 2), (36, 100, 30, 1, 0)), XFADE_A=((10, 127, 127, 1, 2), (10, 127, 127, 1, 2)), XFADE_BOTH=((65, 127, 5, 1, 0), (65, 127, 5, 1, 0)), XFADE_B=((4, 127, 127, 1, 1), (4, 127, 127, 1, 1)), STOP_G_PLAY=((96, 127, 127, 1, 1), (96, 127, 20, 0, 0)), STOP_G_NO_PLAY=((9, 127, 127, 1, 0), (9, 127, 20, 0, 0)), STOP_PLAY=((80, 127, 127, 1, 1), (80, 127, 20, 0, 0)), STOP_NO_PLAY=((14, 127, 127, 1, 0), (14, 127, 20, 0, 0)), STOP_NO_CLIPS=((16, 100, 40, 0, 0), (16, 100, 20, 0, 0)), ARM_MIDI=((0, 127, 127, 1, 0), (0, 127, 20, 0, 0)), ARM_AUDIO=((125, 127, 127, 1, 0), (125, 127, 20, 0, 0)), ARM_OTHER=((2, 127, 127, 1, 0), (0, 127, 20, 0, 0)), ARM_NO_ARM=((2, 80, 30, 1, 0), (2, 80, 30, 0, 0)), MUTE_TRACK=((22, 127, 127, 1, 0), (22, 127, 20, 0, 0)), SOLO_TRACK=((85, 127, 127, 1, 0), (85, 127, 25, 0, 0)), SELECT=((64, 127, 127, 1, 0), (64, 127, 10, 0, 0)), DEVICE_ON_OFF=((97, 80, 120, 1, 0), (97, 80, 50, 0, 0)), DEVICE_LEFT=((3, 127, 127, 1, 0), (3, 127, 30, 0, 0)), DEVICE_RIGHT=((5, 127, 127, 1, 0), (5, 127, 30, 0, 0)), BANK_LEFT=((90, 127, 127, 1, 0), (90, 127, 20, 0, 0)), BANK_RIGHT=((90, 127, 127, 1, 0), (90, 127, 20, 0, 0)), MIX_SELECT_SEND=((21, 127, 127, 1, 0), (21, 127, 20, 0, 0)), SCENE_PLAYING=((36, 127, 127, 1, 1), (36, 100, 25, 0, 0)), SCENE_HASCLIPS=((27, 127, 127, 1, 0), (27, 127, 25, 0, 0)), SCENE_NO_CLIPS=((65, 127, 127, 0, 0), (65, 127, 8, 0, 0)), MIX_SEL_VOLUME=((45, 127, 127, 1, 0), (45, 127, 20, 0, 0)), MIX_SEL_PANNING=((3, 127, 127, 1, 0), (3, 127, 20, 0, 0)), MIX_SEL_SEND=((70, 127, 127, 1, 0), (70, 127, 20, 0, 0)), MIX_SEL_DEVICE=((110, 127, 127, 1, 0), (110, 100, 20, 0, 0)), MIX_MODE_VOLUME=((32, 127, 127, 1, 0), (32, 127, 8, 0, 0)), MIX_MODE_PANNING=((0, 127, 127, 1, 0), (0, 127, 8, 0, 0)), MIX_MODE_SEND=((60, 127, 127, 1, 0), (60, 127, 8, 0, 0)), MIX_MODE_DEVICE=((95, 127, 127, 1, 0), (95, 100, 8, 0, 0)), MIX_MODE_DEVICE_OFF=((95, 10, 127, 1, 0), (95, 10, 30, 0, 0)), OFF=((0, 0, 0, 0, 0), (0, 0, 0, 0, 0)))

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