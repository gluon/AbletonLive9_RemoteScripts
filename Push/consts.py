#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/consts.py
from _Framework.Resource import PrioritizedResource
DISPLAY_LENGTH = 72
TAPPING_DELAY = 0.4
SCROLL_SIDE_BUTTON_STATES = {'Pressed': 'DefaultButton.On',
 'Enabled': 'DefaultButton.Off',
 True: 'DefaultButton.On',
 False: 'DefaultButton.Disabled'}
MUSICAL_MODES = ['Major',
 [0,
  2,
  4,
  5,
  7,
  9,
  11],
 'Minor',
 [0,
  2,
  3,
  5,
  7,
  8,
  10],
 'Dorian',
 [0,
  2,
  3,
  5,
  7,
  9,
  10],
   'raga-sorati',
 [0,
  2,
  5,
  7,
  9,
  10,
  11],
 'Mixolydian',
 [0,
  2,
  4,
  5,
  7,
  9,
  10],
 'Lydian',
 [0,
  2,
  4,
  6,
  7,
  9,
  11],
 'Phrygian',
 [0,
  1,
  3,
  5,
  7,
  8,
  10],
 'Locrian',
 [0,
  1,
  3,
  5,
  6,
  8,
  10],
 'Diminished',
 [0,
  1,
  3,
  4,
  6,
  7,
  9,
  10],
 'Whole-half',
 [0,
  2,
  3,
  5,
  6,
  8,
  9,
  11],
 'Whole Tone',
 [0,
  2,
  4,
  6,
  8,
  10],
 'Minor Blues',
 [0,
  3,
  5,
  6,
  7,
  10],
 'Minor Pentatonic',
 [0,
  3,
  5,
  7,
  10],
 'Major Pentatonic',
 [0,
  2,
  4,
  7,
  9],
 'Harmonic Minor',
 [0,
  2,
  3,
  5,
  7,
  8,
  11],
 'Melodic Minor',
 [0,
  2,
  3,
  5,
  7,
  9,
  11],
 'Super Locrian',
 [0,
  1,
  3,
  4,
  6,
  8,
  10],
 'Bhairav',
 [0,
  1,
  4,
  5,
  7,
  8,
  11],
 'Hungarian Minor',
 [0,
  2,
  3,
  6,
  7,
  8,
  11],
 'Minor Gypsy',
 [0,
  1,
  4,
  5,
  7,
  8,
  10],
 'Hirojoshi',
 [0,
  2,
  3,
  7,
  8],
 'In-Sen',
 [0,
  1,
  5,
  7,
  10],
 'Iwato',
 [0,
  1,
  5,
  6,
  10],
 'Kumoi',
 [0,
  2,
  3,
  7,
  9],
 'Pelog',
 [0,
  1,
  3,
  4,
  7,
  8],
 'Spanish',
 [0,
  1,
  3,
  4,
  5,
  6,
  8,
  10]]
MIN_OFF_THRESHOLD = 10
MAX_OFF_THRESHOLD = 370
MIN_ON_THRESHOLD = 10
MAX_ON_THRESHOLD = 410
MIN_THRESHOLD_STEP = -20
MAX_THRESHOLD_STEP = 20
CRITICAL_THRESHOLD_LIMIT = 0
PROTO_FAST_DEVICE_NAVIGATION = False
PROTO_AUDIO_NOTE_MODE = False
PROTO_SONG_IS_ROOT = False
PROTO_TOUCH_ENCODER_TO_STRIP = False
DEFAULT_PRIORITY = PrioritizedResource.default_priority
SHARED_PRIORITY = DEFAULT_PRIORITY
M4L_PRIORITY = DEFAULT_PRIORITY + 6
MESSAGE_BOX_PRIORITY = DEFAULT_PRIORITY + 5
DIALOG_PRIORITY = DEFAULT_PRIORITY + 4
MODAL_DIALOG_PRIORITY = DEFAULT_PRIORITY + 3
BROWSER_PRIORITY = DEFAULT_PRIORITY + 2
NOTIFICATION_PRIORITY = DEFAULT_PRIORITY + 1
HIDDEN_SESSION_PRIORITY = DEFAULT_PRIORITY - 2
BACKGROUND_PRIORITY = DEFAULT_PRIORITY - 3
ENCODER_SENSITIVITY = 0.5
CONTINUOUS_MAPPING_SENSITIVITY = 2.0
QUANTIZED_MAPPING_SENSITIVITY = 1.0 / 15.0
CHAR_ARROW_UP = '\x00'
CHAR_ARROW_DOWN = '\x01'
CHAR_ARROW_RIGHT = '\x1e'
CHAR_ARROW_LEFT = '\x1f'
CHAR_RACK = '\x02'
CHAR_BAR_LEFT = '\x03'
CHAR_BAR_RIGHT = '\x04'
CHAR_SPLIT_BLOCK = '\x05'
CHAR_SPLIT_DASH = '\x06'
CHAR_FOLDER = '\x07'
CHAR_ELLIPSIS = '\x1c'
CHAR_FLAT_SIGN = '\x1b'
CHAR_ELLIPSIS = '\x1c'
CHAR_FULL_BLOCK = '\x1d'
CHAR_SELECT = '\x7f'
GRAPH_VOL = ('\x03\x06\x06\x06\x06\x06\x06\x06', '\x05\x06\x06\x06\x06\x06\x06\x06', '\x05\x03\x06\x06\x06\x06\x06\x06', '\x05\x05\x06\x06\x06\x06\x06\x06', '\x05\x05\x03\x06\x06\x06\x06\x06', '\x05\x05\x05\x06\x06\x06\x06\x06', '\x05\x05\x05\x03\x06\x06\x06\x06', '\x05\x05\x05\x05\x06\x06\x06\x06', '\x05\x05\x05\x05\x03\x06\x06\x06', '\x05\x05\x05\x05\x05\x06\x06\x06', '\x05\x05\x05\x05\x05\x03\x06\x06', '\x05\x05\x05\x05\x05\x05\x06\x06', '\x05\x05\x05\x05\x05\x05\x03\x06', '\x05\x05\x05\x05\x05\x05\x05\x06', '\x05\x05\x05\x05\x05\x05\x05\x03', '\x05\x05\x05\x05\x05\x05\x05\x05')
GRAPH_PAN = ('\x05\x05\x05\x05\x06\x06\x06\x06', '\x04\x05\x05\x05\x06\x06\x06\x06', '\x06\x05\x05\x05\x06\x06\x06\x06', '\x06\x04\x05\x05\x06\x06\x06\x06', '\x06\x06\x05\x05\x06\x06\x06\x06', '\x06\x06\x04\x05\x06\x06\x06\x06', '\x06\x06\x06\x05\x06\x06\x06\x06', '\x06\x06\x06\x04\x06\x06\x06\x06', '\x06\x06\x06\x04\x03\x06\x06\x06', '\x06\x06\x06\x06\x03\x06\x06\x06', '\x06\x06\x06\x06\x05\x06\x06\x06', '\x06\x06\x06\x06\x05\x03\x06\x06', '\x06\x06\x06\x06\x05\x05\x06\x06', '\x06\x06\x06\x06\x05\x05\x03\x06', '\x06\x06\x06\x06\x05\x05\x05\x06', '\x06\x06\x06\x06\x05\x05\x05\x03', '\x06\x06\x06\x06\x05\x05\x05\x05')
GRAPH_SIN = ('\x03\x06\x06\x06\x06\x06\x06\x06', '\x04\x06\x06\x06\x06\x06\x06\x06', '\x06\x03\x06\x06\x06\x06\x06\x06', '\x06\x04\x06\x06\x06\x06\x06\x06', '\x06\x06\x03\x06\x06\x06\x06\x06', '\x06\x06\x04\x06\x06\x06\x06\x06', '\x06\x06\x06\x03\x06\x06\x06\x06', '\x06\x06\x06\x04\x06\x06\x06\x06', '\x06\x06\x06\x06\x03\x06\x06\x06', '\x06\x06\x06\x06\x04\x06\x06\x06', '\x06\x06\x06\x06\x06\x03\x06\x06', '\x06\x06\x06\x06\x06\x04\x06\x06', '\x06\x06\x06\x06\x06\x06\x03\x06', '\x06\x06\x06\x06\x06\x06\x04\x06', '\x06\x06\x06\x06\x06\x06\x06\x03', '\x06\x06\x06\x06\x06\x06\x06\x04')

class MessageBoxText:
    LIVE_DIALOG = '\n                    Live is showing a dialog' + '\n                    that needs your attention.'
    CLIP_DUPLICATION_FAILED = '\n                     The clip could not be duplicated' + '\n                      because it is recording'
    SCENE_LIMIT_REACHED = '\n                  No more scene can be inserted' + '\n                   for this version of Live'
    SCENE_DUPLICATION_FAILED = '\n                  This scene cannot be duplicated' + '\n                      because it is recording'
    TRACK_LIMIT_REACHED = '\n                  No more track can be inserted' + '\n                   for this version of Live'
    MAX_RETURN_TRACKS_REACHED = '\n                  Maximum number of return tracks' + '\n                  reached'
    TRACK_DUPLICATION_FAILED = '\n                  This track cannot be duplicated' + '\n                      because it is recording'
    TRACK_DELETE_FAILED = '\n                  This track cannot be deleted' + '\n                      because it is recording'
    DELETE_TRACK = '                  Track deleted:    %s'
    DUPLICATE_TRACK = '                  Track duplicated: %s'
    DELETE_CLIP = '                  Clip deleted:     %s'
    DUPLICATE_CLIP = '                  Clip duplicated:  %s'
    QUANTIZE_CLIP = '                  Quantized to:     %(to)s, %(amount)s'
    QUANTIZE_CLIP_PITCH = '                  Quantized pad to: %(to)s, %(amount)s'
    CAPTURE_AND_INSERT_SCENE = '                      Duplicated to scene %s'
    DUPLICATE_LOOP = '                   New loop length: %(length)s'
    DELETE_SCENE = '                  Scene deleted:    %s'
    DUPLICATE_SCENE = '                  Scene duplicated: %s'
    DELETE_ENVELOPE = '                  Delete automation %(automation)s'
    EMPTY_DEVICE_CHAIN = '\n\n               No Devices.    Press [Browse] to add a device.'
    STUCK_PAD_WARNING = '         Warning: Low threshold may cause stuck pads'


try:
    _test_mode = __builtins__.get('TEST_MODE', False)
    if not _test_mode:
        from local_consts import PROTO_SONG_IS_ROOT, PROTO_AUDIO_NOTE_MODE, PROTO_FAST_DEVICE_NAVIGATION, PROTO_TOUCH_ENCODER_TO_STRIP
except ImportError:
    pass
