# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/consts.py
# Compiled at: 2016-06-20 08:10:51
from __future__ import absolute_import, print_function
import sys
import Live
from ableton.v2.control_surface import DEFAULT_PRIORITY
DISPLAY_LENGTH = 72
SIDE_BUTTON_COLORS = dict(color='DefaultButton.On', disabled_color='DefaultButton.Disabled')
PROTO_FAST_DEVICE_NAVIGATION = False
PROTO_AUDIO_NOTE_MODE = False
PROTO_SONG_IS_ROOT = False
PROTO_TOUCH_ENCODER_TO_STRIP = False
SHARED_PRIORITY = DEFAULT_PRIORITY
M4L_PRIORITY = DEFAULT_PRIORITY + 7
USER_BUTTON_PRIORITY = DEFAULT_PRIORITY + 6
MESSAGE_BOX_PRIORITY = DEFAULT_PRIORITY + 5
MOMENTARY_DIALOG_PRIORITY = DEFAULT_PRIORITY + 4
SETUP_DIALOG_PRIORITY = DEFAULT_PRIORITY + 3
DIALOG_PRIORITY = DEFAULT_PRIORITY + 2
NOTIFICATION_PRIORITY = DEFAULT_PRIORITY + 1
BACKGROUND_PRIORITY = DEFAULT_PRIORITY - 3
GLOBAL_MAP_MODE = Live.MidiMap.MapMode.relative_smooth_two_compliment
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
GRAPH_VOL = ('\x03\x06\x06\x06\x06\x06\x06\x06', '\x05\x06\x06\x06\x06\x06\x06\x06',
             '\x05\x03\x06\x06\x06\x06\x06\x06', '\x05\x05\x06\x06\x06\x06\x06\x06',
             '\x05\x05\x03\x06\x06\x06\x06\x06', '\x05\x05\x05\x06\x06\x06\x06\x06',
             '\x05\x05\x05\x03\x06\x06\x06\x06', '\x05\x05\x05\x05\x06\x06\x06\x06',
             '\x05\x05\x05\x05\x03\x06\x06\x06', '\x05\x05\x05\x05\x05\x06\x06\x06',
             '\x05\x05\x05\x05\x05\x03\x06\x06', '\x05\x05\x05\x05\x05\x05\x06\x06',
             '\x05\x05\x05\x05\x05\x05\x03\x06', '\x05\x05\x05\x05\x05\x05\x05\x06',
             '\x05\x05\x05\x05\x05\x05\x05\x03', '\x05\x05\x05\x05\x05\x05\x05\x05')
GRAPH_PAN = ('\x05\x05\x05\x05\x06\x06\x06\x06', '\x04\x05\x05\x05\x06\x06\x06\x06',
             '\x06\x05\x05\x05\x06\x06\x06\x06', '\x06\x04\x05\x05\x06\x06\x06\x06',
             '\x06\x06\x05\x05\x06\x06\x06\x06', '\x06\x06\x04\x05\x06\x06\x06\x06',
             '\x06\x06\x06\x05\x06\x06\x06\x06', '\x06\x06\x06\x04\x06\x06\x06\x06',
             '\x06\x06\x06\x04\x03\x06\x06\x06', '\x06\x06\x06\x06\x03\x06\x06\x06',
             '\x06\x06\x06\x06\x05\x06\x06\x06', '\x06\x06\x06\x06\x05\x03\x06\x06',
             '\x06\x06\x06\x06\x05\x05\x06\x06', '\x06\x06\x06\x06\x05\x05\x03\x06',
             '\x06\x06\x06\x06\x05\x05\x05\x06', '\x06\x06\x06\x06\x05\x05\x05\x03',
             '\x06\x06\x06\x06\x05\x05\x05\x05')
GRAPH_SIN = ('\x03\x06\x06\x06\x06\x06\x06\x06', '\x04\x06\x06\x06\x06\x06\x06\x06',
             '\x06\x03\x06\x06\x06\x06\x06\x06', '\x06\x04\x06\x06\x06\x06\x06\x06',
             '\x06\x06\x03\x06\x06\x06\x06\x06', '\x06\x06\x04\x06\x06\x06\x06\x06',
             '\x06\x06\x06\x03\x06\x06\x06\x06', '\x06\x06\x06\x04\x06\x06\x06\x06',
             '\x06\x06\x06\x06\x03\x06\x06\x06', '\x06\x06\x06\x06\x04\x06\x06\x06',
             '\x06\x06\x06\x06\x06\x03\x06\x06', '\x06\x06\x06\x06\x06\x04\x06\x06',
             '\x06\x06\x06\x06\x06\x06\x03\x06', '\x06\x06\x06\x06\x06\x06\x04\x06',
             '\x06\x06\x06\x06\x06\x06\x06\x03', '\x06\x06\x06\x06\x06\x06\x06\x04')
DISTANT_FUTURE = 999999

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
    QUANTIZE_CLIP_PITCH = '                Quantized %(source)s to:   %(to)s, %(amount)s'
    DELETE_NOTES = '                  Notes deleted:    %s'
    CAPTURE_AND_INSERT_SCENE = '                      Duplicated to scene %s'
    DUPLICATE_LOOP = '                   New loop length: %(length)s'
    DELETE_SCENE = '                  Scene deleted:    %s'
    DUPLICATE_SCENE = '                  Scene duplicated: %s'
    DELETE_ENVELOPE = '                  Delete automation %(automation)s'
    DEFAULT_PARAMETER_VALUE = '                  Reset to default: %(automation)s'
    DELETE_DRUM_RACK_PAD = '                  Drum Pad deleted: %s'
    DELETE_SLICE = '       Slice %s   deleted'
    FIXED_LENGTH = '                      Fixed Length: %s'
    EMPTY_DEVICE_CHAIN = '\n\n               No Devices.    Press [Browse] to add a device.'
    STUCK_PAD_WARNING = '         Warning: Low threshold may cause stuck pads'
    UNDO = '            Undo:     Reverted last action'
    REDO = '            Redo: Re-performed last undone action'
    TRACK_FROZEN_INFO = '                    ' + 'Cannot modify a frozen track'
    SELECTED_CLIP_BLINK = ' Press            to edit playing   clip'
    PLAYING_CLIP_ABOVE_SELECTED_CLIP = ' Press Up Arrow   to edit playing   clip'
    PLAYING_CLIP_BELOW_SELECTED_CLIP = ' Press Down Arrow to edit playing   clip'
    TOUCHSTRIP_PITCHBEND_MODE = '                  Touchstrip Mode:  Pitchbend'
    TOUCHSTRIP_MODWHEEL_MODE = '                  Touchstrip Mode:  Modwheel'
    COPIED_DRUM_PAD = '     Pad %len=8,s copied.           Press destination pad to paste'
    PASTED_DRUM_PAD = '     Pad %len=8,s duplicated to     %len=8,s'
    CANNOT_COPY_EMPTY_DRUM_PAD = '                  Cannot copy empty drum pad'
    CANNOT_PASTE_TO_SOURCE_DRUM_PAD = '                    Cannot paste to source drum pad'
    COPIED_STEP = '     Note(s) copied.           Press destination step to paste'
    PASTED_STEP = '     Note(s) duplicated.'
    CANNOT_COPY_EMPTY_STEP = '                  Cannot copy empty step'
    CANNOT_PASTE_TO_SOURCE_STEP = '                    Cannot paste to source step'
    COPIED_CLIP = '         %len=8,s copied.     Press destination clip  slot to paste'
    PASTED_CLIP = '         %len=8,s duplicated to:    %len=17,s'
    CANNOT_COPY_EMPTY_CLIP = ' Cannot copy from empty clip slot'
    CANNOT_COPY_GROUP_SLOT = '      Group clips cannot be copied'
    CANNOT_COPY_RECORDING_CLIP = '      Cannot copy recording clip'
    CANNOT_COPY_AUDIO_CLIP_TO_MIDI_TRACK = '     Please paste this audio clip       into an audio track'
    CANNOT_COPY_MIDI_CLIP_TO_AUDIO_TRACK = '     Please paste this MIDI clip    into a MIDI track'
    CANNOT_PASTE_INTO_GROUP_SLOT = '    A clip cannot be pasted into a  group track'
    LAYOUT_DRUMS_LOOP = '          Drums:  Loop Selector'
    LAYOUT_DRUMS_LEVELS = '          Drums:  16 Velocities'
    LAYOUT_DRUMS_64_PADS = '          Drums:  64 Pads'
    LAYOUT_SLICING_LOOP = '        Slicing:  Loop Selector'
    LAYOUT_SLICING_LEVELS = '        Slicing:  16 Velocities'
    LAYOUT_SLICING_64_PADS = '        Slicing:  64 Slices'
    LAYOUT_MELODIC_PLAYING = '        Melodic:  64 Notes'
    LAYOUT_MELODIC_SEQUENCER = '        Melodic:  Sequencer'
    LAYOUT_SESSION_VIEW = ' Session View'
    LAYOUT_SESSION_OVERVIEW = ' Session Overview'


_test_mode = __builtins__.get('TEST_MODE', False)
if not _test_mode:
    try:
        _this_module = sys.modules[__name__]
        _proto_list = filter(lambda a: a.startswith('PROTO_'), dir(_this_module))
        for attr in _proto_list:
            try:
                _local_consts = __import__('local_consts', globals(), locals(), [attr], -1)
                setattr(_this_module, attr, getattr(_local_consts, attr))
            except AttributeError:
                pass

    except ImportError:
        pass