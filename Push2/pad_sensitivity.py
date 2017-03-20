# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/pad_sensitivity.py
# Compiled at: 2016-09-29 19:13:24
from __future__ import absolute_import, print_function
playing_profile = 0
default_profile = 1
loop_selector_profile = 2

def index_to_pad_coordinate(index):
    """
    Maps a linear range to appropriate x and y coordinates of the pad matrix.
    The coordinates are 1-based, since the pad sensitivity sysex commands expect this
    when setting individual pads.
    """
    x, y = divmod(index, 8)
    return (
     8 - x, y + 1)


def pad_parameter_sender(global_control, pad_control):
    """
    Sends the sensitivity parameters for a given pad, or all pads
    (pad == None) over the given SysexElement.
    """

    def do_send(sensitivity_value, pad=None):
        if pad is None:
            global_control.send_value(0, 0, sensitivity_value)
        else:
            scene, track = index_to_pad_coordinate(pad)
            pad_control.send_value(scene, track, sensitivity_value)
        return

    return do_send