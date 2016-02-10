#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/KeyLab/KeyLab.py
from __future__ import with_statement
from itertools import izip
import Live
from _Arturia.ArturiaControlSurface import ArturiaControlSurface, MODE_PROPERTY, SETUP_MSG_PREFIX, SETUP_MSG_SUFFIX
from _Framework.Layer import Layer
from _Framework.DeviceComponent import DeviceComponent
from _Framework.DrumRackComponent import DrumRackComponent
from _Framework.TransportComponent import TransportComponent
from _Framework.SessionRecordingComponent import SessionRecordingComponent
from _Framework.ClipCreator import ClipCreator
from _Framework.ViewControlComponent import ViewControlComponent
from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.SliderElement import SliderElement
from _Framework.DisplayDataSource import DisplayDataSource
from .DeviceNavigationComponent import DeviceNavigationComponent
from .MixerComponent import MixerComponent
from .SessionComponent import SessionComponent
from .DisplayElement import DisplayElement
PAD_NOTE_MODE = 10
ENCODER_HARDWARE_IDS = xrange(33, 43)
SLIDER_HARDWARE_IDS = (43, 44, 45, 46, 107, 108, 109, 110, 111)
PAD_HARDWARE_IDS = xrange(112, 128)
ENCODER_MSG_IDS = (74, 71, 76, 77, 18, 19, 16, 17, 93, 91)
SLIDER_MSG_IDS = (73, 75, 79, 72, 80, 81, 82, 83, 85)
PAD_MSG_IDS = xrange(36, 52)
BUTTON_HARDWARE_AND_MESSAGE_IDS = {'session_record_button': (91, 5),
 'stop_all_clips_button': (92, 4),
 'stop_button': (89, 1),
 'play_button': (88, 2),
 'record_button': (90, 6),
 'loop_button': (93, 55),
 'device_left_button': (18, 22),
 'device_right_button': (19, 23),
 'scene_up_button': (25, 29),
 'scene_down_button': (26, 30),
 'scene_launch_button': (27, 31)}
ENCODER_CHANNEL = 1
PAD_CHANNEL = 9

def get_button_identifier_by_name(identifier):
    id_pair = BUTTON_HARDWARE_AND_MESSAGE_IDS.get(identifier, None)
    if id_pair is not None:
        return id_pair[1]
    return id_pair


class KeyLab(ArturiaControlSurface):

    def __init__(self, *a, **k):
        super(KeyLab, self).__init__(*a, **k)
        with self.component_guard():
            self._create_controls()
            self._create_display()
            self._create_device()
            self._create_drums()
            self._create_transport()
            self._create_session()
            self._create_session_recording()
            self._create_mixer()

    def _create_controls(self):
        self._device_encoders = ButtonMatrixElement(rows=[ [ EncoderElement(MIDI_CC_TYPE, ENCODER_CHANNEL, identifier, Live.MidiMap.MapMode.relative_smooth_binary_offset, name='Device_Encoder_%d_%d' % (col_index, row_index)) for col_index, identifier in enumerate(row) ] for row_index, row in enumerate((ENCODER_MSG_IDS[:4], ENCODER_MSG_IDS[4:8])) ])
        self._horizontal_scroll_encoder = EncoderElement(MIDI_CC_TYPE, ENCODER_CHANNEL, ENCODER_MSG_IDS[-2], Live.MidiMap.MapMode.relative_smooth_binary_offset, name='Horizontal_Scroll_Encoder')
        self._vertical_scroll_encoder = EncoderElement(MIDI_CC_TYPE, ENCODER_CHANNEL, ENCODER_MSG_IDS[-1], Live.MidiMap.MapMode.relative_smooth_binary_offset, name='Vertical_Scroll_Encoder')
        self._volume_sliders = ButtonMatrixElement(rows=[[ SliderElement(MIDI_CC_TYPE, ENCODER_CHANNEL, identifier) for identifier in SLIDER_MSG_IDS[:-1] ]])
        self._master_slider = SliderElement(MIDI_CC_TYPE, ENCODER_CHANNEL, SLIDER_MSG_IDS[-1])

        def make_keylab_button(name):
            button = ButtonElement(True, MIDI_CC_TYPE, 0, get_button_identifier_by_name(name), name=name.title())
            return button

        for button_name in BUTTON_HARDWARE_AND_MESSAGE_IDS.keys():
            setattr(self, '_' + button_name, make_keylab_button(button_name))

        self._pads = ButtonMatrixElement(rows=[ [ ButtonElement(True, MIDI_CC_TYPE, PAD_CHANNEL, col_index + row_offset, name='Pad_%d_%d' % (col_index, row_index)) for col_index in xrange(4) ] for row_index, row_offset in enumerate(xrange(48, 35, -4)) ])

    def _create_display(self):
        self._display_line1, self._display_line2 = DisplayElement(16, 1), DisplayElement(16, 1)
        for index, display_line in enumerate((self._display_line1, self._display_line2)):
            display_line.set_message_parts(SETUP_MSG_PREFIX + (4, 0, 96), SETUP_MSG_SUFFIX)
            display_line.segment(0).set_position_identifier((index + 1,))

        def adjust_null_terminated_string(string, width):
            return string.ljust(width, ' ') + '\x00'

        self._display_line1_data_source, self._display_line2_data_source = DisplayDataSource(adjust_string_fn=adjust_null_terminated_string), DisplayDataSource(adjust_string_fn=adjust_null_terminated_string)
        self._display_line1.segment(0).set_data_source(self._display_line1_data_source)
        self._display_line2.segment(0).set_data_source(self._display_line2_data_source)
        self._display_line1_data_source.set_display_string('KeyLab')
        self._display_line2_data_source.set_display_string('Ableton Live')

    def _create_device(self):
        self._device = DeviceComponent(name='Device', is_enabled=False, layer=Layer(parameter_controls=self._device_encoders))
        self._device.set_enabled(True)
        self.set_device_component(self._device)
        self._device_selection_follows_track_selection = True
        self._device_navigation = DeviceNavigationComponent(name='Device_Navigation', is_enabled=False, layer=Layer(device_nav_left_button=self._device_left_button, device_nav_right_button=self._device_right_button))
        self._device_navigation.set_enabled(True)

    def _create_drums(self):
        self._drums = DrumRackComponent(name='Drums', is_enabled=False, layer=Layer(pads=self._pads))
        self._drums.set_enabled(True)

    def _create_transport(self):
        self._transport = TransportComponent(name='Transport', is_enabled=False, layer=Layer(play_button=self._play_button, stop_button=self._stop_button, record_button=self._record_button, loop_button=self._loop_button))
        self._transport.set_enabled(True)

    def _create_session(self):
        self._session = SessionComponent(num_tracks=8, num_scenes=1, name='Session', is_enabled=False, layer=Layer(select_next_button=self._scene_down_button, select_prev_button=self._scene_up_button, selected_scene_launch_button=self._scene_launch_button, stop_all_clips_button=self._stop_all_clips_button, scene_select_encoder=self._vertical_scroll_encoder))
        self._session.set_enabled(True)

    def _create_session_recording(self):
        self._session_recording = SessionRecordingComponent(ClipCreator(), ViewControlComponent(), name='Session_Recording', is_enabled=False, layer=Layer(record_button=self._session_record_button))
        self._session_recording.set_enabled(True)

    def _create_mixer(self):
        self._mixer = MixerComponent(num_tracks=self._volume_sliders.width(), name='Mixer', is_enabled=False, layer=Layer(volume_controls=self._volume_sliders, track_select_encoder=self._horizontal_scroll_encoder))
        self._mixer.master_strip().layer = Layer(volume_control=self._master_slider)
        self._mixer.set_enabled(True)

    def _collect_setup_messages(self):
        for hardware_id, identifier in izip(ENCODER_HARDWARE_IDS, ENCODER_MSG_IDS):
            self._setup_hardware_encoder(hardware_id, identifier, ENCODER_CHANNEL)

        for hardware_id, identifier in izip(SLIDER_HARDWARE_IDS, SLIDER_MSG_IDS):
            self._setup_hardware_slider(hardware_id, identifier, ENCODER_CHANNEL)

        for hardware_id, identifier in BUTTON_HARDWARE_AND_MESSAGE_IDS.itervalues():
            self._setup_hardware_button(hardware_id, identifier)

        for hardware_id, identifier in izip(PAD_HARDWARE_IDS, PAD_MSG_IDS):
            self._setup_hardware_pad(hardware_id, identifier)

    def _setup_hardware_encoder(self, hardware_id, identifier, channel = 0):
        self._set_encoder_cc_msg_type(hardware_id, is_relative=True)
        self._set_identifier(hardware_id, identifier)
        self._set_channel(hardware_id, channel)

    def _setup_hardware_button(self, hardware_id, identifier, channel = 0, **k):
        self._set_encoder_cc_msg_type(hardware_id)
        self._set_identifier(hardware_id, identifier)
        self._set_channel(hardware_id, channel)
        self._set_value_minimum(hardware_id)
        self._set_value_maximum(hardware_id)

    def _setup_hardware_pad(self, hardware_id, identifier, channel = PAD_CHANNEL):
        self._set_pad_note_msg_type(hardware_id)
        self._set_identifier(hardware_id, identifier)
        self._set_channel(hardware_id, channel)

    def _set_pad_note_msg_type(self, hardware_id):
        self._collect_setup_message(MODE_PROPERTY, hardware_id, PAD_NOTE_MODE)