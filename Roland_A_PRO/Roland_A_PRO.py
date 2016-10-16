#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Roland_A_PRO/Roland_A_PRO.py
from __future__ import with_statement
from functools import partial
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.Layer import Layer
from _Framework.EncoderElement import EncoderElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.SliderElement import SliderElement
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.ButtonElement import ButtonElement
from _Framework.DeviceComponent import DeviceComponent
from _Framework.TransportComponent import TransportComponent
from _Framework.ModesComponent import ModesComponent, LayerMode, AddLayerMode
from _Framework.DrumRackComponent import DrumRackComponent
from .DeviceNavigationComponent import DeviceNavigationComponent
from .MixerComponent import MixerComponent
ENCODER_IDS = (74, 71, 65, 2, 5, 76, 77, 78)
SLIDER_IDS = (73, 75, 72, 91, 92, 93, 94, 95)
PAD_ROWS = ([67,
  69,
  71,
  72], [60,
  62,
  64,
  65])

class Roland_A_PRO(ControlSurface):

    def __init__(self, *a, **k):
        super(Roland_A_PRO, self).__init__(*a, **k)
        with self.component_guard():
            self._create_controls()
            self._create_transport()
            self._create_mixer()
            self._create_device()
            self._create_drums()
            self._create_modes()

    def _create_controls(self):
        self._encoders = ButtonMatrixElement(rows=[[ EncoderElement(MIDI_CC_TYPE, 0, identifier, Live.MidiMap.MapMode.absolute, name='Encoder_%d' % index) for index, identifier in enumerate(ENCODER_IDS) ]])
        self._master_encoder = EncoderElement(MIDI_CC_TYPE, 0, 10, Live.MidiMap.MapMode.absolute, name='Master_Encoder')
        self._sliders = ButtonMatrixElement(rows=[[ SliderElement(MIDI_CC_TYPE, 0, identifier, name='Slider_%d' % index) for index, identifier in enumerate(SLIDER_IDS) ]])
        self._master_slider = SliderElement(MIDI_CC_TYPE, 0, 7, name='Master_Slider')
        self._play_button = ButtonElement(True, MIDI_CC_TYPE, 0, 26)
        self._stop_button = ButtonElement(True, MIDI_CC_TYPE, 0, 25)
        self._record_button = ButtonElement(True, MIDI_CC_TYPE, 0, 28)
        self._forward_button = ButtonElement(True, MIDI_CC_TYPE, 0, 24)
        self._backward_button = ButtonElement(True, MIDI_CC_TYPE, 0, 21)
        self._ff_button = ButtonElement(True, MIDI_CC_TYPE, 0, 23)
        self._rw_button = ButtonElement(True, MIDI_CC_TYPE, 0, 22)
        self._device_mode_button = ButtonElement(True, MIDI_CC_TYPE, 0, 80)
        self._pan_mode_button = ButtonElement(True, MIDI_CC_TYPE, 0, 81)
        self._send_a_mode_button = ButtonElement(True, MIDI_CC_TYPE, 0, 82)
        self._send_b_mode_button = ButtonElement(True, MIDI_CC_TYPE, 0, 83)
        self._pads = ButtonMatrixElement(rows=[ [ ButtonElement(True, MIDI_NOTE_TYPE, 0, identifier) for identifier in row ] for row in PAD_ROWS ])

    def _create_transport(self):
        self._transport = TransportComponent(name='Transport', is_enabled=False, layer=Layer(play_button=self._play_button, stop_button=self._stop_button, record_button=self._record_button))
        self._transport.set_enabled(True)

    def _create_mixer(self):
        mixer_size = self._sliders.width()
        self._mixer = MixerComponent(mixer_size, name='Mixer', is_enabled=False, layer=Layer(volume_controls=self._sliders, prehear_volume_control=self._master_encoder))
        self._mixer.master_strip().layer = Layer(volume_control=self._master_slider)
        self._mixer.set_enabled(True)

    def _create_device(self):
        self._device = DeviceComponent()
        self._device_navigation = DeviceNavigationComponent()
        self._device.set_enabled(True)
        self._device_navigation.set_enabled(True)
        self.set_device_component(self._device)
        self._device_selection_follows_track_selection = True

    def _create_drums(self):
        self._drums = DrumRackComponent(name='Drum_Rack', is_enabled=False, layer=Layer(pads=self._pads))
        self._drums.set_enabled(True)

    def _create_modes(self):
        self._encoder_modes = ModesComponent()
        device_layer_mode = LayerMode(self._device, Layer(parameter_controls=self._encoders))
        device_navigation_layer_mode = LayerMode(self._device_navigation, Layer(device_nav_right_button=self._forward_button, device_nav_left_button=self._backward_button))
        self._encoder_modes.add_mode('device_mode', [device_layer_mode, device_navigation_layer_mode])
        self._encoder_modes.add_mode('pan_mode', AddLayerMode(self._mixer, Layer(pan_controls=self._encoders, bank_up_button=self._forward_button, bank_down_button=self._backward_button, track_up_button=self._ff_button, track_down_button=self._rw_button)))
        send_layer_mode = AddLayerMode(self._mixer, Layer(send_controls=self._encoders, bank_up_button=self._forward_button, bank_down_button=self._backward_button, track_up_button=self._ff_button, track_down_button=self._rw_button))
        self._encoder_modes.add_mode('send_a_mode', [send_layer_mode, partial(self._set_send_index, 0)])
        self._encoder_modes.add_mode('send_b_mode', [send_layer_mode, partial(self._set_send_index, 1)])
        self._encoder_modes.layer = Layer(device_mode_button=self._device_mode_button, pan_mode_button=self._pan_mode_button, send_a_mode_button=self._send_a_mode_button, send_b_mode_button=self._send_b_mode_button)
        self._encoder_modes.selected_mode = 'device_mode'
        self._encoder_modes.set_enabled(True)

    def _set_send_index(self, index):
        self._mixer.send_index = index