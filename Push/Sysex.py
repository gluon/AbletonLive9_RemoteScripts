#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/Push/Sysex.py
START = (240, 71, 127, 21)
CLEAR_LINE1 = START + (28, 0, 0, 247)
CLEAR_LINE2 = START + (29, 0, 0, 247)
CLEAR_LINE3 = START + (30, 0, 0, 247)
CLEAR_LINE4 = START + (31, 0, 0, 247)
WRITE_LINE1 = START + (24, 0, 69, 0)
WRITE_LINE2 = START + (25, 0, 69, 0)
WRITE_LINE3 = START + (26, 0, 69, 0)
WRITE_LINE4 = START + (27, 0, 69, 0)
SET_AFTERTOUCH_MODE = START + (92, 0, 1)
POLY_AFTERTOUCH = (0,)
MONO_AFTERTOUCH = (1,)
CONTRAST_PREFIX = START + (122, 0, 1)
CONTRAST_ENQUIRY = START + (122, 0, 0, 247)
BRIGHTNESS_PREFIX = START + (124, 0, 1)
BRIGHTNESS_ENQUIRY = START + (124, 0, 0, 247)
ALL_PADS_SENSITIVITY_PREFIX = START + (93, 0, 32)
PAD_SENSITIVITY_PREFIX = START + (90, 0, 33)

def to_sysex_int(number, unused_parameter_name):
    return (number >> 12 & 15,
     number >> 8 & 15,
     number >> 4 & 15,
     number & 15)


CALIBRATION_SET = START + (87, 0, 20) + to_sysex_int(215, 'Preload Scale Factor') + to_sysex_int(1000, 'Recalibration Interval') + to_sysex_int(200, 'Stuck Pad Detection Threshold') + to_sysex_int(0, 'Stuck Pad NoteOff Threshold Adder') + to_sysex_int(200, 'Pad Ignore Time') + (247,)
MODE_CHANGE = START + (98, 0, 1)
USER_MODE = 1
LIVE_MODE = 0
WELCOME_MESSAGE = START + (1, 1, 247)
GOOD_BYE_MESSAGE = START + (1, 0, 247)
IDENTITY_PREFIX = START + (6, 2)
IDENTITY_ENQUIRY = START + (6, 1, 247)
DONGLE_PREFIX = START + (80, 0)

def make_presentation_message(application):
    return START + (96,
     0,
     4,
     65,
     application.get_major_version(),
     application.get_minor_version(),
     application.get_bugfix_version(),
     247)


IDENTITY_ENQUIRY = (240, 126, 0, 6, 1, 247)
IDENTITY_PREFIX = (240, 126, 0, 6, 2, 71, 21, 0, 25)
DONGLE_ENQUIRY_PREFIX = START + (80,)
DONGLE_PREFIX = START + (81,)