#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_static/midi-remote-scripts/Launch_Control/Sysex.py
MODE_CHANGE_PREFIX = (240, 0, 32, 41, 2, 10, 119)
MIXER_MODE = (240, 0, 32, 41, 2, 10, 119, 8, 247)
SESSION_MODE = (240, 0, 32, 41, 2, 10, 119, 9, 247)
DEVICE_MODE = (240, 0, 32, 41, 2, 10, 119, 10, 247)

def make_automatic_flashing_message(channel):
    return (176 + channel, 0, 40)