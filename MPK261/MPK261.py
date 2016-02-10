#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MPK261/MPK261.py
from __future__ import with_statement
from _Framework.ControlSurface import ControlSurface
from _Framework.Layer import Layer
from _Framework.DrumRackComponent import DrumRackComponent
from _Framework.TransportComponent import TransportComponent
from _Framework.MixerComponent import MixerComponent
from _Framework.MidiMap import MidiMap as MidiMapBase
from _Framework.MidiMap import make_button, make_encoder, make_slider
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE

class MidiMap(MidiMapBase):

    def __init__(self, *a, **k):
        super(MidiMap, self).__init__(*a, **k)
        self.add_button('Play', 0, 118, MIDI_CC_TYPE)
        self.add_button('Record', 0, 119, MIDI_CC_TYPE)
        self.add_button('Stop', 0, 117, MIDI_CC_TYPE)
        self.add_button('Loop', 0, 114, MIDI_CC_TYPE)
        self.add_button('Forward', 0, 116, MIDI_CC_TYPE)
        self.add_button('Backward', 0, 115, MIDI_CC_TYPE)
        self.add_matrix('Sliders', make_slider, 0, [[12,
          13,
          14,
          15,
          16,
          17,
          18,
          19]], MIDI_CC_TYPE)
        self.add_matrix('Encoders', make_encoder, 0, [[22,
          23,
          24,
          25,
          26,
          27,
          28,
          29]], MIDI_CC_TYPE)
        self.add_matrix('Arm_Buttons', make_button, 0, [[32,
          33,
          34,
          35,
          36,
          37,
          38,
          39]], MIDI_CC_TYPE)
        self.add_matrix('Drum_Pads', make_button, 1, [[81,
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
          65]], MIDI_NOTE_TYPE)


class MPK261(ControlSurface):

    def __init__(self, *a, **k):
        super(MPK261, self).__init__(*a, **k)
        with self.component_guard():
            midimap = MidiMap()
            drum_rack = DrumRackComponent(name='Drum_Rack', is_enabled=False, layer=Layer(pads=midimap['Drum_Pads']))
            drum_rack.set_enabled(True)
            transport = TransportComponent(name='Transport', is_enabled=False, layer=Layer(play_button=midimap['Play'], record_button=midimap['Record'], stop_button=midimap['Stop'], seek_forward_button=midimap['Forward'], seek_backward_button=midimap['Backward'], loop_button=midimap['Loop']))
            transport.set_enabled(True)
            mixer_size = len(midimap['Sliders'])
            mixer = MixerComponent(mixer_size, name='Mixer', is_enabled=False, layer=Layer(volume_controls=midimap['Sliders'], pan_controls=midimap['Encoders'], arm_buttons=midimap['Arm_Buttons']))
            mixer.set_enabled(True)