#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/matrix_maps.py
"""
Pad Translations for Drum Rack (pad_x, pad_y, note, channel)
"""
from __future__ import absolute_import, print_function
PAD_TRANSLATIONS = ((0, 0, 60, 13),
 (1, 0, 61, 13),
 (2, 0, 62, 13),
 (3, 0, 63, 13),
 (0, 1, 52, 13),
 (1, 1, 53, 13),
 (2, 1, 54, 13),
 (3, 1, 55, 13),
 (0, 2, 44, 13),
 (1, 2, 45, 13),
 (2, 2, 46, 13),
 (3, 2, 47, 13),
 (0, 3, 36, 13),
 (1, 3, 37, 13),
 (2, 3, 38, 13),
 (3, 3, 39, 13))
NON_FEEDBACK_CHANNEL = 0
FEEDBACK_CHANNELS = range(8, 16)
PAD_FEEDBACK_CHANNEL = FEEDBACK_CHANNELS[-1]
PLAYHEAD_FEEDBACK_CHANNELS = range(1, 8)