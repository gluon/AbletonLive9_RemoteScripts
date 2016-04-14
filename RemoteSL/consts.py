#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/RemoteSL/consts.py
NOTE_OFF_STATUS = 128
NOTE_ON_STATUS = 144
CC_STATUS = 176
NUM_NOTES = 127
NUM_CC_NO = 127
NUM_CHANNELS = 15
NUM_CONTROLS_PER_ROW = 8
SL_MIDI_CHANNEL = 0
CC_VAL_BUTTON_PRESSED = 1
CC_VAL_BUTTON_RELEASED = 0
ABLETON_PID = 4
WELCOME_SYSEX_MESSAGE = (240,
 0,
 32,
 41,
 3,
 3,
 18,
 0,
 ABLETON_PID,
 0,
 1,
 1,
 247)
GOOD_BYE_SYSEX_MESSAGE = (240,
 0,
 32,
 41,
 3,
 3,
 18,
 0,
 ABLETON_PID,
 0,
 1,
 0,
 247)
ALL_LEDS_OFF_MESSAGE = (CC_STATUS + SL_MIDI_CHANNEL, 78, 0)
NUM_CHARS_PER_DISPLAY_STRIP = 9
NUM_CHARS_PER_DISPLAY_LINE = NUM_CHARS_PER_DISPLAY_STRIP * NUM_CONTROLS_PER_ROW

def __create_row_range(cc_base):
    return range(cc_base, cc_base + NUM_CONTROLS_PER_ROW)


FX_DISPLAY_PAGE_UP = 88
FX_DISPLAY_PAGE_DOWN = 89
fx_display_button_ccs = [FX_DISPLAY_PAGE_UP, FX_DISPLAY_PAGE_DOWN]
FX_SELECT_FIRST_BUTTON_ROW = 80
FX_SELECT_ENCODER_ROW = 81
FX_SELECT_SECOND_BUTTON_ROW = 82
FX_SELECT_POTIE_ROW = 83
FX_SELECT_DRUM_PAD_ROW = 84
fx_select_button_ccs = range(FX_SELECT_FIRST_BUTTON_ROW, FX_SELECT_DRUM_PAD_ROW + 1)
FX_RING_VOL_VALUE = 0
FX_RING_PAN_VALUE = 32
FX_RING_SIN_VALUE = 64
FX_UPPER_BUTTON_ROW_BASE_CC = 24
fx_upper_button_row_ccs = __create_row_range(FX_UPPER_BUTTON_ROW_BASE_CC)
FX_ENCODER_ROW_BASE_CC = 56
fx_encoder_row_ccs = __create_row_range(FX_ENCODER_ROW_BASE_CC)
FX_ENCODER_FEEDBACK_BASE_CC = 112
fx_encoder_feedback_ccs = __create_row_range(FX_ENCODER_FEEDBACK_BASE_CC)
FX_ENCODER_LED_MODE_BASE_CC = 120
fx_encoder_led_mode_ccs = __create_row_range(FX_ENCODER_LED_MODE_BASE_CC)
FX_LOWER_BUTTON_ROW_BASE_CC = 32
fx_lower_button_row_ccs = __create_row_range(FX_LOWER_BUTTON_ROW_BASE_CC)
FX_POTI_ROW_BASE_CC = 8
fx_poti_row_ccs = __create_row_range(FX_POTI_ROW_BASE_CC)
FX_DRUM_PAD_ROW_BASE_NOTE = 36
fx_drum_pad_row_notes = __create_row_range(FX_DRUM_PAD_ROW_BASE_NOTE)
fx_ccs = fx_display_button_ccs + fx_select_button_ccs + fx_upper_button_row_ccs + fx_encoder_row_ccs + fx_lower_button_row_ccs + fx_poti_row_ccs
fx_notes = fx_drum_pad_row_notes
fx_forwarded_ccs = fx_display_button_ccs + fx_select_button_ccs + fx_upper_button_row_ccs
fx_forwarded_notes = []
MX_DISPLAY_PAGE_UP = 90
MX_DISPLAY_PAGE_DOWN = 91
mx_display_button_ccs = [MX_DISPLAY_PAGE_UP, MX_DISPLAY_PAGE_DOWN]
MX_SELECT_SLIDER_ROW = 85
MX_SELECT_FIRST_BUTTON_ROW = 86
MX_SELECT_SECOND_BUTTON_ROW = 87
mx_select_button_ccs = range(MX_SELECT_SLIDER_ROW, MX_SELECT_SECOND_BUTTON_ROW + 1)
MX_SLIDER_ROW_BASE_CC = 16
mx_slider_row_ccs = __create_row_range(MX_SLIDER_ROW_BASE_CC)
MX_FIRST_BUTTON_ROW_BASE_CC = 40
mx_first_button_row_ccs = __create_row_range(MX_FIRST_BUTTON_ROW_BASE_CC)
MX_SECOND_BUTTON_ROW_BASE_CC = 48
mx_second_button_row_ccs = __create_row_range(MX_SECOND_BUTTON_ROW_BASE_CC)
TS_REWIND_CC = 72
TS_FORWARD_CC = 73
TS_STOP_CC = 74
TS_PLAY_CC = 75
TS_RECORD_CC = 76
TS_LOOP_CC = 77
TS_LOCK = 79
ts_ccs = [TS_REWIND_CC,
 TS_FORWARD_CC,
 TS_STOP_CC,
 TS_PLAY_CC,
 TS_RECORD_CC,
 TS_LOOP_CC,
 TS_LOCK,
 TS_LOCK + 1]
ts_notes = []
mx_ccs = mx_display_button_ccs + mx_select_button_ccs + mx_first_button_row_ccs + mx_second_button_row_ccs + mx_slider_row_ccs + ts_ccs
mx_notes = []
mx_forwarded_ccs = mx_display_button_ccs + mx_select_button_ccs + mx_first_button_row_ccs + mx_second_button_row_ccs
mx_forwarded_notes = []
PAD_TRANSLATION = ((0, 2, 36, 0),
 (1, 2, 37, 0),
 (2, 2, 38, 0),
 (3, 2, 39, 0),
 (0, 3, 40, 0),
 (1, 3, 41, 0),
 (2, 3, 42, 0),
 (3, 3, 43, 0))