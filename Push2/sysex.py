#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/sysex.py
from __future__ import absolute_import, print_function
from ableton.v2.base import chunks
from ableton.v2.control_surface import midi
from pushbase.sysex import LIVE_MODE, USER_MODE
from pushbase.touch_strip_element import TouchStripStates, TouchStripModes
PAD_VELOCITY_CURVE_CHUNK_SIZE = 16
MODE_SWITCH_MESSAGE_ID = 10

def make_aftertouch_mode_message(mode_id):
    raise mode_id in ('polyphonic', 'mono') or AssertionError
    mode_byte = 0 if mode_id == 'mono' else 1
    return make_message(30, (mode_byte,))


def make_mode_switch_messsage(mode_id):
    raise mode_id[0] in (LIVE_MODE, USER_MODE) or AssertionError
    return make_message(MODE_SWITCH_MESSAGE_ID, mode_id)


def make_rgb_palette_entry_message(index, hex_color, white_balance):
    r, g, b = _make_rgb_from_hex(hex_color)
    return make_message(3, (index,) + to_7L1M(r) + to_7L1M(g) + to_7L1M(b) + to_7L1M(white_balance))


def _make_rgb_from_hex(hex_value):
    r = hex_value >> 16
    g = hex_value >> 8 & 255
    b = hex_value & 255
    return (r, g, b)


def make_reapply_palette_message():
    return make_message(5)


def make_touch_strip_mode_message(mode):
    """
    The behavior of the touch strip is defined by a number of flags
    put together into a 7 bit touch strip configuration setting.
    
        -----------------------------
    bit | 6 | 5 | 4 | 3 | 2 | 1 | 0 |
        ----------------------------- value              |   0         |  1
          |   |   |   |   |   |   |   -------------------+-------------+-----------
          |   |   |   |   |   |   --- LEDs controlled by |  push2      | host
          |   |   |   |   |   ------- host sends         |  values     | sysex
          |   |   |   |   ----------- values sent as     |  pitch bend | mod wheel
          |   |   |   --------------- LEDs show          |  a bar      | a point
          |   |   ------------------- bar starts at      |  bottom     | center
          |   ----------------------- do autoreturn      |  no         | yes
          --------------------------- autoreturn to      |  bottom     | center
    """
    mode_bytes = ()
    if mode == TouchStripModes.CUSTOM_PITCHBEND:
        mode_bytes = int('1111001', 2)
    elif mode == TouchStripModes.CUSTOM_VOLUME:
        mode_bytes = int('0000001', 2)
    elif mode == TouchStripModes.CUSTOM_PAN:
        mode_bytes = int('0010001', 2)
    elif mode == TouchStripModes.CUSTOM_DISCRETE:
        mode_bytes = int('0011001', 2)
    elif mode == TouchStripModes.CUSTOM_FREE:
        mode_bytes = int('0001011', 2)
    elif mode == TouchStripModes.MODWHEEL:
        mode_bytes = int('0000100', 2)
    elif mode == TouchStripModes.PITCHBEND:
        mode_bytes = int('1111000', 2)
    else:
        raise RuntimeError('Touch strip mode %i not supported' % mode)
    return make_message(23, (mode_bytes,))


TOUCHSTRIP_STATE_TO_BRIGHTNESS = {TouchStripStates.STATE_OFF: 0,
 TouchStripStates.STATE_HALF: 1,
 TouchStripStates.STATE_FULL: 6}

def _make_touch_strip_light(state):
    if len(state) == 2:
        return state[0] | state[1] << 3
    return state[0]


def make_touch_strip_light_message(states):
    """
    The 31 touch strip LEDs are set with 3 bits per LED. The brightness is
    encoded with 3 bits. The brightness of range 0 ... 127 is the "input brightness",
    comparable to the one set for the white LEDs by control change CC3, for example.
    As will all LEDs, compression, white balance, overall brightness and USB power
    brightness limitation are applied afterwards.
    """
    states = [ TOUCHSTRIP_STATE_TO_BRIGHTNESS[state] for state in states ]
    return make_message(25, tuple([ _make_touch_strip_light(state) for state in chunks(states, 2) ]))


def make_pad_velocity_curve_message(index, velocities):
    """
    Updates a chunk of velocities in the voltage to velocity table.
    The index refers to the first entry in the velocities list.
    """
    raise len(velocities) == PAD_VELOCITY_CURVE_CHUNK_SIZE or AssertionError
    return make_message(32, (index,) + tuple(velocities))


def make_pad_threshold_message(threshold1, threshold2, lower_channel_pressure_threshold, upper_channel_pressure_threshold):
    """
    These parameters determine the lower note threshold and the
    channel pressure ("aftertouch") thresholds of the pads.
    The parameters affect all pads.
    """
    args = to_7L5M(threshold1) + to_7L5M(threshold2) + to_7L5M(lower_channel_pressure_threshold) + to_7L5M(upper_channel_pressure_threshold)
    return make_message(27, args)


def make_led_brightness_message(brightness):
    """
    Sets a new brightness and reapplies the color palette. The effective
    brightness may be limited to a maximum value (e.g. 32) internally
    when power supply is not connected.
    """
    raise 0 <= brightness <= 127 or AssertionError
    return make_message(6, (brightness,))


def make_display_brightness_message(brightness):
    """
    The display brightness is influenced by various parameters like
    absolute maximum backlight LED current, relative backlight LED
    brightness, VCOM default level and the gamma curve.
    
    Only the relative backlight LED brightness can be configured
    via MIDI, the remaining values are set by the firmware, depending
    on the power source.
    """
    raise 0 <= brightness <= 255 or AssertionError
    return make_message(8, to_7L1M(brightness))


def extract_identity_response_info(data):
    """
    Extracts the arguments from the identity response:
    - major version
    - minor version
    - build number
    - serial number
    - board revision
    """
    major = data[12]
    minor = data[13]
    build = from_7L7M(data[14], data[15])
    sn = from_7L7777M(data[16:21])
    board_revision = data[21] if len(data) > 22 else 0
    return (major,
     minor,
     build,
     sn,
     board_revision)


MANUFACTURER_ID = (0, 33, 29)
MESSAGE_START = (midi.SYSEX_START,) + MANUFACTURER_ID + (1, 1)
IDENTITY_RESPONSE_PRODUCT_ID_BYTES = MANUFACTURER_ID + (103, 50, 2, 0)

def make_message(command_id, arguments = tuple()):
    """
    Create a sysex message from a command id and the optional arguments
    
    command_id - command or reply id (in the future, for 16 bit values, prepend zero)
    arguments  - a number of 7 bit values depending on command or reply id
                 the maximum number of arguments is 16 (except for the printf reply)
    """
    return MESSAGE_START + (command_id,) + arguments + (midi.SYSEX_END,)


def make_message_identifier(command_id):
    """
    Return the unique initial part of the sysex message without any arguments, to
    identify a sysex message.
    """
    return MESSAGE_START + (command_id,)


def to_7L1M(value):
    """ Returns a list with the 7 lower bits of the value followed by the 1 higher bit
    """
    return (value & 127, value >> 7 & 1)


def to_7L5M(value):
    """ Returns a list with the 7 lower bits of the value followed by the 5 higher bits
    """
    return (value & 127, value >> 7 & 31)


def from_7L7M(lsb, msb):
    """ Combines 7 lower and 7 higher bits into a value """
    return lsb + (msb << 7)


def from_7L7777M(data):
    """ Combines 5 times 7 bits into a value, lsb first """
    return data[0] + (data[1] << 7) + (data[2] << 14) + (data[3] << 21) + (data[4] << 28)