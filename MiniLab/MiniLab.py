#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MiniLab/MiniLab.py
from __future__ import with_statement
from itertools import izip
import Live
from _Arturia.ArturiaControlSurface import ArturiaControlSurface
from _Arturia.SessionComponent import SessionComponent
from _Arturia.MixerComponent import MixerComponent
from _Framework.Layer import Layer
from _Framework.DeviceComponent import DeviceComponent
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
HARDWARE_ENCODER_IDS = (48, 1, 2, 9, 11, 12, 13, 14, 51, 3, 4, 10, 5, 6, 7, 8)
HARDWARE_BUTTON_IDS = xrange(112, 128)
ENCODER_MSG_IDS = (7, 74, 71, 76, 77, 93, 73, 75, 114, 18, 19, 16, 17, 91, 79, 72)
PAD_IDENTIFIER_OFFSET = 36
PAD_CHANNEL = 9

class MiniLab(ArturiaControlSurface):

    def __init__(self, *a, **k):
        super(MiniLab, self).__init__(*a, **k)
        with self.component_guard():
            self._create_controls()
            self._create_device()
            self._create_session()
            self._create_mixer()

    def _create_controls(self):
        self._device_controls = ButtonMatrixElement(rows=[ [ EncoderElement(MIDI_CC_TYPE, 0, identifier, Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Encoder_%d_%d' % (column_index, row_index)) for column_index, identifier in enumerate(row) ] for row_index, row in enumerate((ENCODER_MSG_IDS[:4], ENCODER_MSG_IDS[8:12])) ])
        self._horizontal_scroll_encoder = EncoderElement(MIDI_CC_TYPE, 0, 75, Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Horizontal_Scroll_Encoder')
        self._vertical_scroll_encoder = EncoderElement(MIDI_CC_TYPE, 0, 72, Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Vertical_Scroll_Encoder')
        self._volume_encoder = EncoderElement(MIDI_CC_TYPE, 0, 91, Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Volume_Encoder')
        self._pan_encoder = EncoderElement(MIDI_CC_TYPE, 0, 17, Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Pan_Encoder')
        self._send_a_encoder = EncoderElement(MIDI_CC_TYPE, 0, 77, Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Send_A_Encoder')
        self._send_b_encoder = EncoderElement(MIDI_CC_TYPE, 0, 93, Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Send_B_Encoder')
        self._send_encoders = ButtonMatrixElement(rows=[[self._send_a_encoder, self._send_b_encoder]])
        self._return_a_encoder = EncoderElement(MIDI_CC_TYPE, 0, 73, Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Return_A_Encoder')
        self._return_b_encoder = EncoderElement(MIDI_CC_TYPE, 0, 79, Live.MidiMap.MapMode.relative_smooth_two_compliment, name='Return_B_Encoder')
        self._return_encoders = ButtonMatrixElement(rows=[[self._return_a_encoder, self._return_b_encoder]])
        self._pads = ButtonMatrixElement(rows=[ [ ButtonElement(True, MIDI_NOTE_TYPE, PAD_CHANNEL, col + 36 + 8 * row, name='Pad_%d_%d' % (col, row)) for col in xrange(8) ] for row in xrange(2) ])

    def _create_device(self):
        self._device = DeviceComponent(name='Device', is_enabled=False, layer=Layer(parameter_controls=self._device_controls))
        self._device.set_enabled(True)
        self.set_device_component(self._device)
        self._device_selection_follows_track_selection = True

    def _create_session(self):
        self._session = SessionComponent(num_tracks=self._pads.width(), num_scenes=self._pads.height(), name='Session', is_enabled=False, layer=Layer(clip_launch_buttons=self._pads, scene_select_control=self._vertical_scroll_encoder))
        self._session.set_enabled(True)

    def _create_mixer(self):
        self._mixer = MixerComponent(name='Mixer', is_enabled=False, num_returns=2, layer=Layer(track_select_encoder=self._horizontal_scroll_encoder, selected_track_volume_control=self._volume_encoder, selected_track_pan_control=self._pan_encoder, selected_track_send_controls=self._send_encoders, return_volume_controls=self._return_encoders))
        self._mixer.set_enabled(True)

    def _collect_setup_messages(self):
        for cc_id, encoder_id in izip(ENCODER_MSG_IDS, HARDWARE_ENCODER_IDS):
            self._setup_hardware_encoder(encoder_id, cc_id)

        for index, pad_id in enumerate(HARDWARE_BUTTON_IDS):
            identifier = index + PAD_IDENTIFIER_OFFSET
            channel = PAD_CHANNEL
            self._setup_hardware_button(pad_id, identifier, channel)