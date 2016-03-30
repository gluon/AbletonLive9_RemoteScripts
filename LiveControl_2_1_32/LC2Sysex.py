#Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/LiveControl_2_1_31/LC2Sysex.py
import Live

class LC2Sysex:
    CLIP = [0, 0]
    SCENE = [0, 1]
    TRACK = [0, 2]
    CLIP_POSITION = [0, 8]
    TRACK_METERS = [0, 9]
    SET_OFFSETS = [0, 10]
    TRACK_DEVICE_NAME = [0, 11]
    SET_WIDTH = [0, 12]
    SNAPSHOT_STATES = [0, 13]
    RETURN_NAMES = [0, 14]
    TRACK_ROUTING = [0, 15]
    TRACK_ROUTING_LIST = [0, 16]
    STEPS = [1, 0]
    SEQ_POSITION = [1, 1]
    SEQ_FADERS = [1, 2]
    SEQ_TIMELINE = [1, 3]
    SEQ_NOTELINE = [1, 4]
    SEQ_OFFSETS = [1, 5]
    STEPS2 = [1, 6]
    SEQ_NOTELINE = [1, 7]
    SEQ_MUTES = [1, 8]
    CLIP_TITLE = [1, 9]
    SEQ_FOLD = [1, 10]
    SEQ_QUANT = [1, 11]
    SEQ_CLOSE = [1, 12]
    SEQ_SEND_SELECTION = [1, 13]
    SEQ_SAVE_NOTE = [1, 14]
    PARAM_VALS = [2, 0]
    DEVICE_NAME = [2, 1]
    XY_ID_NAME = [2, 2]
    TRACK_DEVICES = [2, 3]
    CHAIN_NAMES = [2, 4]
    CHAIN_DEVICES = [2, 5]
    XY_MAP = [2, 6]
    TEMPO = [5, 1]
    TIME = [5, 0]
    RESET = [5, 2]

    @staticmethod
    def l9():
        return Live.Application.get_application().get_major_version() >= 9

    @staticmethod
    def set_midi_callback(callback):
        raise dir(callback).count('im_func') is 1 or AssertionError
        LC2Sysex._midi_callback = callback

    @staticmethod
    def set_log(func):
        raise dir(func).count('im_func') is 1 or AssertionError
        LC2Sysex.log_message = func

    @staticmethod
    def release_attributes():
        LC2Sysex.log_message = None
        LC2Sysex._midi_callback = None

    def __init__(self, type):
        self._msg = [240] + getattr(self, type)

    def msg(self):
        return tuple(self._msg + [247])

    def int(self, int):
        self._msg += [int >> 7 & 127, int & 127]

    def int2(self, int):
        b1 = int >> 14 & 127
        b2 = int >> 7 & 127
        b3 = int & 127
        self._msg += [b1, b2, b3]

    def ascii(self, string):
        self._msg += [ ord(c) > 127 and 32 or ord(c) for c in string ]
        if len(string) == 0:
            self._msg += [0]
        self._msg.append(127)

    def trim(self, display_string, length):
        if len(display_string) < length:
            self.ascii(display_string)
            return
        if len(display_string.strip()) > length and display_string.endswith('dB') and display_string.find('.') != -1:
            display_string = display_string[:-2]
        if len(display_string) > length:
            for um in [' ',
             'i',
             'o',
             'u',
             'e',
             'a']:
                while len(display_string) > length and display_string.rfind(um, 1) != -1:
                    um_pos = display_string.rfind(um, 1)
                    display_string = display_string[:um_pos] + display_string[um_pos + 1:]

        self.ascii(display_string[0:length])

    def byte(self, byte):
        self._msg.append(byte)

    def bool(self, val):
        if val:
            self._msg.append(1)
        else:
            self._msg.append(0)

    def rgb(self, rgb, inv = 0):
        byte1 = rgb >> 21 & 127
        byte2 = rgb >> 14 & 127
        byte3 = rgb >> 7 & 127
        byte4 = rgb & 127
        self._msg += [byte1,
         byte2,
         byte3,
         byte4]

    def send(self):
        if self._midi_callback is not None:
            valid = True
            if max(self.msg()[1:-2]) > 127:
                valid = False
            if valid:
                self._midi_callback(self.msg())
            else:
                self.log_message('INVALID SYSEX MESSAGE' + str(self.msg()))


class LC2SysexParser:

    def __init__(self, msg):
        self._msg = msg

    def _int(self, start):
        if start < len(self._msg) - 1:
            return (self._msg[start] << 7) + self._msg[start + 1]
        else:
            return 0

    def _byte(self, id):
        if id < len(self._msg):
            return self._msg[id]
        else:
            return 0

    def parse(self, types):
        out = []
        i = 0
        sysex_types = {'b': [self._byte, 1],
         'i': [self._int, 2]}
        for c in types:
            if c in sysex_types:
                fn, size = sysex_types[c]
                out.append(fn(i))
                i += size

        return len(out) > 1 and out or out[0]