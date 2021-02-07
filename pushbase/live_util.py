# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/live_util.py
# Compiled at: 2016-05-20 03:43:52
from __future__ import absolute_import, print_function

def get_position_for_new_track(song, selected_track_index):
    """
    Returns the index for a new track. The track will always be added to the
    right of the selected track. If a group track is selected, it will be added
    after the group.
    """
    if not -1 <= selected_track_index < len(song.tracks):
        raise IndexError('Index %i needs to be in [-1..%i]' % (
         selected_track_index, len(song.tracks)))
    if selected_track_index == -1:
        index = -1
    else:
        index = selected_track_index + 1
        if song.tracks[selected_track_index].is_foldable:
            while index < len(song.tracks) and song.tracks[index].is_grouped:
                index += 1

    return index