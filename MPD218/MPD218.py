#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MPD218/MPD218.py
from _MPDMkIIBase.MPDMkIIBase import MPDMkIIBase
PAD_CHANNEL = 9
PAD_IDS = [[48,
  49,
  50,
  51],
 [44,
  45,
  46,
  47],
 [40,
  41,
  42,
  43],
 [36,
  37,
  38,
  39]]

class MPD218(MPDMkIIBase):

    def __init__(self, *a, **k):
        super(MPD218, self).__init__(PAD_IDS, PAD_CHANNEL, *a, **k)