#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MPD226/MPD226.py
from __future__ import with_statement
from itertools import cycle, izip
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _MPDMkIIBase.MPDMkIIBase import MPDMkIIBase
from _MPDMkIIBase.ControlElementUtils import make_button, make_encoder, make_slider
PAD_CHANNEL = 1
PAD_IDS = [[81,
  83,
  84,
  86],
 [74,
  76,
  77,
  79],
 [67,
  69,
  71,
  72],
 [60,
  62,
  64,
  65]]

class MPD226(MPDMkIIBase):

    def __init__(self, *a, **k):
        super(MPD226, self).__init__(PAD_IDS, PAD_CHANNEL, *a, **k)
        with self.component_guard():
            self._create_device()
            self._create_transport()
            self._create_mixer()

    def _create_controls(self):
        super(MPD226, self)._create_controls()
        self._encoders = ButtonMatrixElement(rows=[[ make_encoder(identifier, 0 if index < 4 else 1, 'Encoder_%d' % index) for index, identifier in izip(xrange(8), cycle(xrange(22, 26))) ]])
        self._sliders = ButtonMatrixElement(rows=[[ make_slider(identifier, 0 if index < 4 else 1, 'Slider_%d' % index) for index, identifier in izip(xrange(8), cycle(xrange(12, 16))) ]])
        self._control_buttons = ButtonMatrixElement(rows=[[ make_button(identifier, 0 if index < 4 else 1, 'Control_Button_%d' % index) for index, identifier in izip(xrange(8), cycle(xrange(32, 36))) ]])
        self._play_button = make_button(118, 0, 'Play_Button')
        self._stop_button = make_button(117, 0, 'Stop_Button')
        self._record_button = make_button(119, 0, 'Record_Button')