#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/KeyPad/KeyPad.py
from __future__ import with_statement
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.Layer import Layer
from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.SliderElement import SliderElement
from _Framework.EncoderElement import EncoderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.MixerComponent import MixerComponent
from _Framework.TransportComponent import TransportComponent
from _Framework.SessionComponent import SessionComponent
from CuePointControlComponent import CuePointControlComponent
from CombinedButtonsElement import CombinedButtonsElement
from functools import partial
NUM_CHANNEL_STRIPS = 16
pads = [1,
 2,
 3,
 4,
 9,
 10,
 11,
 12,
 5,
 6,
 7,
 8,
 13,
 14,
 15,
 16]
PAD_TRANSLATIONS = tuple([ (n % 4,
 3 - n / 4,
 pads[n] + 35,
 4) for n in xrange(16) ])

def make_slider(channel, cc, name):
    element = SliderElement(MIDI_CC_TYPE, channel, cc)
    element.name = name
    return element


def make_encoder(channel, cc, name):
    map_mode = Live.MidiMap.MapMode.absolute
    return EncoderElement(MIDI_CC_TYPE, channel, cc, map_mode=map_mode, name=name)


def make_button(channel, cc, name, is_momentary = True):
    return ButtonElement(is_momentary, MIDI_CC_TYPE, channel, cc, name=name)


class KeyPad(ControlSurface):
    """
    Reloop KeyPad controller script.
    """
    _encoder_range = range(73, 81)
    _product_model_id = 101

    def __init__(self, c_instance):
        super(KeyPad, self).__init__(c_instance)
        with self.component_guard():
            self._create_controls()
            self._setup_mixer()
            self._setup_transport()
            self._setup_session()
            self._setup_cue_control()
            self.set_pad_translations(PAD_TRANSLATIONS)

    def _preset_message(self, send_byte):
        """ Sysex message for setting the preset to #2. """
        return (240,
         38,
         self._product_model_id,
         send_byte,
         17,
         2,
         247)

    def refresh_state(self):
        super(KeyPad, self).refresh_state()
        self.schedule_message(2, self._send_midi, self._preset_message(1))

    def handle_sysex(self, midi_bytes):
        if midi_bytes != self._preset_message(2):
            super(KeyPad, self).handle_sysex(midi_bytes)
        else:
            map(lambda x: x.set_enabled(True), (self._mixer,
             self._session,
             self._transport,
             self._cue_control))

    def _create_controls(self):

        def make_controls_range(maker, label, cc_range):
            ccs = [ (index + 1, cc) for index, cc in enumerate(cc_range) ]
            return [ maker(1, cc, label % index) for index, cc in ccs ] + [ maker(2, cc, label % (index + len(ccs))) for index, cc in ccs ]

        def make_controls(maker, label, cc_offset):
            return make_controls_range(maker, label, xrange(cc_offset, cc_offset + 8))

        make_non_momentary_button = partial(make_button, is_momentary=False)
        self._encoders = make_controls(make_encoder, 'Encoder_%d', 57)
        self._rotaries_a = make_controls(make_slider, 'Rotary_A%d', 89)
        self._rotaries_b = make_controls(make_slider, 'Rotary_B%d', 97)
        self._faders = make_controls(make_slider, 'Fader_%d', 0)
        self._mute_buttons = make_controls(make_non_momentary_button, 'Mute_%d_Button', 8)
        self._solo_buttons = make_controls(make_button, 'Solo_%d_Button', 24)
        self._arm_buttons = make_controls(make_button, 'Arm_%d_Button', 40)
        self._play_button = make_button(1, 105, 'Play_Button')
        self._stop_button = make_button(1, 106, 'Stop_Button')
        self._record_button = make_button(1, 107, 'Record_Button')
        self._encoder_pushes = make_controls_range(partial(make_button, is_momentary=False), 'Encoder_%d_Button', self._encoder_range)
        self._shifted_mute_buttons = make_controls(make_non_momentary_button, 'Shifted_Mute_%d_Button', 16)
        self._shifted_solo_buttons = make_controls(make_button, 'Shifted_Solo_%d_Button', 32)
        self._all_shifted_arm_buttons = make_controls(make_button, 'Shifted_Arm_%d_Button', 49)
        self._shifted_arm_buttons = [ CombinedButtonsElement(buttons=(self._all_shifted_arm_buttons[index], self._all_shifted_arm_buttons[index + 8])) for index in xrange(8) ]
        self._shifted_play_button = make_button(1, 108, 'Shifted_Play_Button')
        self._shifted_stop_button = make_button(1, 109, 'Shifted_Stop_Button')
        self._shifted_record_button = make_button(1, 110, 'Shifted_Record_Button')
        self._shifted_octave_down_button = make_button(1, 111, 'Shifted_Octave_Down_Button')
        self._shifted_octave_up_button = make_button(1, 112, 'Shifted_Octave_Up_Button')

    def _setup_mixer(self):
        self._mixer = MixerComponent(NUM_CHANNEL_STRIPS)
        self._mixer.name = 'Mixer'
        self._mixer.set_enabled(False)
        for index in xrange(NUM_CHANNEL_STRIPS):
            strip = self._mixer.channel_strip(index)
            strip.set_invert_mute_feedback(True)
            sends = ButtonMatrixElement(name='%d_Send_Controls' % (index + 1), rows=[(self._rotaries_a[index], self._rotaries_b[index])])
            strip.layer = Layer(volume_control=self._faders[index], pan_control=self._encoders[index], send_controls=sends, mute_button=self._mute_buttons[index], solo_button=self._solo_buttons[index], arm_button=self._arm_buttons[index], select_button=self._encoder_pushes[index])

    def _setup_transport(self):
        self._transport = TransportComponent(name='Transport')
        self._transport.set_enabled(False)
        self._transport.layer = Layer(play_button=self._play_button, stop_button=self._stop_button, record_button=self._record_button, overdub_button=self._shifted_record_button, loop_button=self._shifted_arm_buttons[3], tap_tempo_button=self._shifted_arm_buttons[4], metronome_button=self._shifted_arm_buttons[5], nudge_down_button=self._shifted_arm_buttons[6], nudge_up_button=self._shifted_arm_buttons[7])

    def _setup_session(self):
        self._session = SessionComponent(NUM_CHANNEL_STRIPS, name='Session_Control')
        self._session.set_enabled(False)
        stop_buttons = ButtonMatrixElement(name='Track_Stop_Buttons', rows=[self._shifted_solo_buttons])
        self._session.layer = Layer(stop_all_clips_button=self._shifted_stop_button, stop_track_clip_buttons=stop_buttons, select_prev_button=self._shifted_octave_down_button, select_next_button=self._shifted_octave_up_button)
        self._session.selected_scene().name = 'Selected_Scene_Control'
        self._session.selected_scene().layer = Layer(launch_button=self._shifted_play_button)
        for index in xrange(NUM_CHANNEL_STRIPS):
            slot = self._session.selected_scene().clip_slot(index)
            slot.layer = Layer(launch_button=self._shifted_mute_buttons[index])

    def _setup_cue_control(self):
        self._cue_control = CuePointControlComponent(name='Cue_Point_Control')
        self._cue_control.set_enabled(False)
        self._cue_control.layer = Layer(toggle_cue_button=self._shifted_arm_buttons[0], prev_cue_button=self._shifted_arm_buttons[1], next_cue_button=self._shifted_arm_buttons[2])