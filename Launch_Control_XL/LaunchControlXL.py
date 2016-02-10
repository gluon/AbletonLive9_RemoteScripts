#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launch_Control_XL/LaunchControlXL.py
from __future__ import with_statement
from functools import partial
from itertools import chain
import Live
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.EncoderElement import EncoderElement
from _Framework.IdentifiableControlSurface import IdentifiableControlSurface
from _Framework.InputControlElement import MIDI_CC_TYPE, MIDI_NOTE_TYPE
from _Framework.Layer import Layer
from _Framework.ModesComponent import ModeButtonBehaviour, ModesComponent, AddLayerMode
from _Framework.SessionComponent import SessionComponent
from _Framework.SliderElement import SliderElement
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import nop
from _Framework import Task
from .ButtonElement import ButtonElement
from .DeviceComponent import DeviceComponent, DeviceModeComponent
from .MixerComponent import MixerComponent
from .SkinDefault import make_biled_skin, make_default_skin
NUM_TRACKS = 8
LIVE_CHANNEL = 8
PREFIX_TEMPLATE_SYSEX = (240, 0, 32, 41, 2, 17, 119)
LIVE_TEMPLATE_SYSEX = PREFIX_TEMPLATE_SYSEX + (LIVE_CHANNEL, 247)

class LaunchControlXL(IdentifiableControlSurface):

    def __init__(self, c_instance, *a, **k):
        super(LaunchControlXL, self).__init__(c_instance=c_instance, product_id_bytes=(0, 32, 41, 97), *a, **k)
        self._device_selection_follows_track_selection = True
        self._biled_skin = make_biled_skin()
        self._default_skin = make_default_skin()
        with self.component_guard():
            self._create_controls()
        self._initialize_task = self._tasks.add(Task.sequence(Task.wait(1), Task.run(self._create_components)))
        self._initialize_task.kill()

    def on_identified(self):
        self._send_live_template()

    def _create_components(self):
        self._initialize_task.kill()
        self._disconnect_and_unregister_all_components()
        with self.component_guard():
            mixer = self._create_mixer()
            session = self._create_session()
            device = self._create_device()
            session.set_mixer(mixer)
            self.set_device_component(device)

    def _create_controls(self):

        def make_button(identifier, name, midi_type = MIDI_CC_TYPE, skin = self._default_skin):
            return ButtonElement(True, midi_type, LIVE_CHANNEL, identifier, name=name, skin=skin)

        def make_button_list(identifiers, name):
            return [ make_button(identifier, name % (i + 1), MIDI_NOTE_TYPE, self._biled_skin) for i, identifier in enumerate(identifiers) ]

        def make_encoder(identifier, name):
            return EncoderElement(MIDI_CC_TYPE, LIVE_CHANNEL, identifier, Live.MidiMap.MapMode.absolute, name=name)

        def make_slider(identifier, name):
            return SliderElement(MIDI_CC_TYPE, LIVE_CHANNEL, identifier, name=name)

        self._send_encoders = ButtonMatrixElement(rows=[[ make_encoder(13 + i, 'Top_Send_%d' % (i + 1)) for i in xrange(8) ], [ make_encoder(29 + i, 'Bottom_Send_%d' % (i + 1)) for i in xrange(8) ]])
        self._pan_device_encoders = ButtonMatrixElement(rows=[[ make_encoder(49 + i, 'Pan_Device_%d' % (i + 1)) for i in xrange(8) ]])
        self._volume_faders = ButtonMatrixElement(rows=[[ make_slider(77 + i, 'Volume_%d' % (i + 1)) for i in xrange(8) ]])
        self._pan_device_mode_button = make_button(105, 'Pan_Device_Mode', MIDI_NOTE_TYPE)
        self._mute_mode_button = make_button(106, 'Mute_Mode', MIDI_NOTE_TYPE)
        self._solo_mode_button = make_button(107, 'Solo_Mode', MIDI_NOTE_TYPE)
        self._arm_mode_button = make_button(108, 'Arm_Mode', MIDI_NOTE_TYPE)
        self._up_button = make_button(104, 'Up')
        self._down_button = make_button(105, 'Down')
        self._left_button = make_button(106, 'Track_Left')
        self._right_button = make_button(107, 'Track_Right')
        self._select_buttons = ButtonMatrixElement(rows=[make_button_list(chain(xrange(41, 45), xrange(57, 61)), 'Track_Select_%d')])
        self._state_buttons = ButtonMatrixElement(rows=[make_button_list(chain(xrange(73, 77), xrange(89, 93)), 'Track_State_%d')])
        self._send_encoder_lights = ButtonMatrixElement(rows=[make_button_list([13,
          29,
          45,
          61,
          77,
          93,
          109,
          125], 'Top_Send_Encoder_Light_%d'), make_button_list([14,
          30,
          46,
          62,
          78,
          94,
          110,
          126], 'Bottom_Send_Encoder_Light_%d')])
        self._pan_device_encoder_lights = ButtonMatrixElement(rows=[make_button_list([15,
          31,
          47,
          63,
          79,
          95,
          111,
          127], 'Pan_Device_Encoder_Light_%d')])

    def _create_mixer(self):
        mixer = MixerComponent(NUM_TRACKS, is_enabled=True, auto_name=True)
        mixer.layer = Layer(track_select_buttons=self._select_buttons, send_controls=self._send_encoders, next_sends_button=self._down_button, prev_sends_button=self._up_button, pan_controls=self._pan_device_encoders, volume_controls=self._volume_faders, send_lights=self._send_encoder_lights, pan_lights=self._pan_device_encoder_lights)
        mixer.on_send_index_changed = partial(self._show_controlled_sends_message, mixer)
        for channel_strip in map(mixer.channel_strip, xrange(NUM_TRACKS)):
            channel_strip.empty_color = 'Mixer.NoTrack'

        mixer_modes = ModesComponent()
        mixer_modes.add_mode('mute', [AddLayerMode(mixer, Layer(mute_buttons=self._state_buttons))])
        mixer_modes.add_mode('solo', [AddLayerMode(mixer, Layer(solo_buttons=self._state_buttons))])
        mixer_modes.add_mode('arm', [AddLayerMode(mixer, Layer(arm_buttons=self._state_buttons))])
        mixer_modes.layer = Layer(mute_button=self._mute_mode_button, solo_button=self._solo_mode_button, arm_button=self._arm_mode_button)
        mixer_modes.selected_mode = 'mute'
        return mixer

    def _create_session(self):
        session = SessionComponent(num_tracks=NUM_TRACKS, is_enabled=True, auto_name=True, enable_skinning=True)
        session.layer = Layer(track_bank_left_button=self._left_button, track_bank_right_button=self._right_button)
        self._on_session_offset_changed.subject = session
        return session

    @subject_slot('offset')
    def _on_session_offset_changed(self):
        session = self._on_session_offset_changed.subject
        self._show_controlled_tracks_message(session)

    def _create_device(self):
        device = DeviceComponent(name='Device_Component', is_enabled=False)
        device.layer = Layer(parameter_controls=self._pan_device_encoders, parameter_lights=self._pan_device_encoder_lights, priority=1)
        device_settings_layer = Layer(bank_buttons=self._state_buttons, prev_device_button=self._left_button, next_device_button=self._right_button, priority=1)
        mode = DeviceModeComponent(component=device, device_settings_mode=[AddLayerMode(device, device_settings_layer)], is_enabled=True)
        mode.layer = Layer(device_mode_button=self._pan_device_mode_button)
        return device

    def _show_controlled_sends_message(self, mixer):
        if mixer.send_index is not None:
            send_index = mixer.send_index
            send_name1 = chr(ord('A') + send_index)
            if send_index + 1 < mixer.num_sends:
                send_name2 = chr(ord('A') + send_index + 1)
                self.show_message('Controlling Send %s and %s' % (send_name1, send_name2))
            else:
                self.show_message('Controlling Send %s' % send_name1)

    def _show_controlled_tracks_message(self, session):
        start = session.track_offset() + 1
        end = min(start + 8, len(session.tracks_to_use()))
        if start < end:
            self.show_message('Controlling Track %d to %d' % (start, end))
        else:
            self.show_message('Controlling Track %d' % start)

    def _send_live_template(self):
        self._send_midi(LIVE_TEMPLATE_SYSEX)
        self._initialize_task.restart()

    def handle_sysex(self, midi_bytes):
        if midi_bytes[:7] == PREFIX_TEMPLATE_SYSEX:
            if midi_bytes[7] == LIVE_CHANNEL:
                if self._initialize_task.is_running:
                    self._create_components()
                else:
                    self.update()
        else:
            super(LaunchControlXL, self).handle_sysex(midi_bytes)