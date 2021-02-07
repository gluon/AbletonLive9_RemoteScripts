# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/custom_bank_definitions.py
# Compiled at: 2016-09-29 19:13:24
from __future__ import absolute_import, print_function
from ableton.v2.base.collection import IndexedDict
from pushbase.parameter_slot_description import use
from pushbase.banking_util import PARAMETERS_KEY, MAIN_KEY
OPTIONS_KEY = 'Options'
SHOW_WAVEFORM_KEY = 'show_waveform'
RACK_BANKS = IndexedDict((
 (
  'Macros',
  {PARAMETERS_KEY: ('Macro 1', 'Macro 2', 'Macro 3', 'Macro 4', 'Macro 5', 'Macro 6', 'Macro 7', 'Macro 8')
     }),))
BANK_DEFINITIONS = {'AudioEffectGroupDevice': RACK_BANKS,
   'MidiEffectGroupDevice': RACK_BANKS,
   'InstrumentGroupDevice': RACK_BANKS,
   'DrumGroupDevice': RACK_BANKS,
   'UltraAnalog': IndexedDict((
                 (
                  MAIN_KEY,
                  {PARAMETERS_KEY: (
                                    use('OSC1 Shape').if_parameter('OSC1 On/Off').has_value('on').else_use('OSC2 Shape').if_parameter('OSC2 On/Off').has_value('on'),
                                    use('OSC1 Octave').if_parameter('OSC1 On/Off').has_value('on').else_use('OSC2 Octave').if_parameter('OSC2 On/Off').has_value('on'),
                                    use('OSC2 Shape').if_parameter('OSC1 On/Off').has_value('on').and_parameter('OSC2 On/Off').has_value('on').else_use('OSC1 Semi').if_parameter('OSC1 On/Off').has_value('on').else_use('OSC2 Semi').if_parameter('OSC2 On/Off').has_value('on'),
                                    use('OSC2 Octave').if_parameter('OSC1 On/Off').has_value('on').and_parameter('OSC2 On/Off').has_value('on').else_use('OSC1 Detune').if_parameter('OSC1 On/Off').has_value('on').else_use('OSC2 Detune').if_parameter('OSC2 On/Off').has_value('on'),
                                    use('F1 Type').if_parameter('F1 On/Off').has_value('on').else_use('F2 Type').if_parameter('F2 On/Off').has_value('on'),
                                    use('F1 Freq').if_parameter('F1 On/Off').has_value('on').else_use('F2 Freq').if_parameter('F2 On/Off').has_value('on'),
                                    use('F1 Resonance').if_parameter('F1 On/Off').has_value('on').else_use('F2 Resonance').if_parameter('F2 On/Off').has_value('on'),
                                    'Volume')
                     }),
                 (
                  'Osc. 1 Shape',
                  {PARAMETERS_KEY: (
                                    'OSC1 On/Off',
                                    use('OSC1 Shape').if_parameter('OSC1 On/Off').has_value('on'),
                                    use('').if_parameter('OSC1 On/Off').has_value('off').else_use('OSC1 PW').if_parameter('OSC1 Shape').has_value('Rect'),
                                    use('').if_parameter('OSC1 On/Off').has_value('off').else_use('O1 PW < LFO').if_parameter('OSC1 Shape').has_value('Rect').else_use('').if_parameter('LFO1 On/Off').has_value('off'),
                                    use('').if_parameter('OSC1 On/Off').has_value('off').else_use('').if_parameter('OSC1 Shape').has_value('Noise').else_use('').if_parameter('OSC1 Shape').has_value('Sine').else_use('OSC1 Mode'),
                                    use('').if_parameter('OSC1 On/Off').has_value('off').else_use('').if_parameter('OSC1 Shape').has_value('Noise').else_use('O1 Sub/Sync'),
                                    use('OSC1 Balance').if_parameter('OSC1 On/Off').has_value('on'),
                                    use('OSC1 Level').if_parameter('OSC1 On/Off').has_value('on'))
                     }),
                 (
                  'Osc. 1 Pitch',
                  {PARAMETERS_KEY: (
                                    'OSC1 On/Off',
                                    use('OSC1 Octave').if_parameter('OSC1 On/Off').has_value('on'),
                                    use('OSC1 Semi').if_parameter('OSC1 On/Off').has_value('on'),
                                    use('OSC1 Detune').if_parameter('OSC1 On/Off').has_value('on'),
                                    use('PEG1 Amount').if_parameter('OSC1 On/Off').has_value('on'),
                                    use('PEG1 Time').if_parameter('OSC1 On/Off').has_value('on'),
                                    use('O1 Keytrack').if_parameter('OSC1 On/Off').has_value('on'),
                                    use('').if_parameter('OSC1 On/Off').has_value('off').else_use('').if_parameter('LFO1 On/Off').has_value('off').else_use('OSC1 < LFO'))
                     }),
                 (
                  'Osc. 2 Shape',
                  {PARAMETERS_KEY: (
                                    'OSC2 On/Off',
                                    use('OSC2 Shape').if_parameter('OSC2 On/Off').has_value('on'),
                                    use('').if_parameter('OSC2 On/Off').has_value('off').else_use('OSC2 PW').if_parameter('OSC2 Shape').has_value('Rect'),
                                    use('').if_parameter('OSC2 On/Off').has_value('off').else_use('O2 PW < LFO').if_parameter('OSC2 Shape').has_value('Rect').else_use('').if_parameter('LFO2 On/Off').has_value('off'),
                                    use('').if_parameter('OSC2 On/Off').has_value('off').else_use('').if_parameter('OSC2 Shape').has_value('Noise').else_use('').if_parameter('OSC2 Shape').has_value('Sine').else_use('OSC2 Mode'),
                                    use('').if_parameter('OSC2 On/Off').has_value('off').else_use('').if_parameter('OSC2 Shape').has_value('Noise').else_use('O2 Sub/Sync'),
                                    use('OSC2 Balance').if_parameter('OSC2 On/Off').has_value('on'),
                                    use('OSC2 Level').if_parameter('OSC2 On/Off').has_value('on'))
                     }),
                 (
                  'Osc. 2 Pitch',
                  {PARAMETERS_KEY: (
                                    'OSC2 On/Off',
                                    use('OSC2 Octave').if_parameter('OSC2 On/Off').has_value('on'),
                                    use('OSC2 Semi').if_parameter('OSC2 On/Off').has_value('on'),
                                    use('OSC2 Detune').if_parameter('OSC2 On/Off').has_value('on'),
                                    use('PEG2 Amount').if_parameter('OSC2 On/Off').has_value('on'),
                                    use('PEG2 Time').if_parameter('OSC2 On/Off').has_value('on'),
                                    use('O2 Keytrack').if_parameter('OSC2 On/Off').has_value('on'),
                                    use('').if_parameter('OSC2 On/Off').has_value('off').else_use('').if_parameter('LFO2 On/Off').has_value('off').else_use('OSC2 < LFO'))
                     }),
                 (
                  'Filters',
                  {PARAMETERS_KEY: (
                                    'F1 On/Off',
                                    use('F1 Type').if_parameter('F1 On/Off').has_value('on'),
                                    use('F1 Freq').if_parameter('F1 On/Off').has_value('on'),
                                    use('F1 Resonance').if_parameter('F1 On/Off').has_value('on'),
                                    'F2 On/Off',
                                    use('F2 Type').if_parameter('F2 On/Off').has_value('on'),
                                    use('F2 Freq').if_parameter('F2 On/Off').has_value('on'),
                                    use('F2 Resonance').if_parameter('F2 On/Off').has_value('on'))
                     }),
                 (
                  'Filt. 1 Env.',
                  {PARAMETERS_KEY: (
                                    'F1 On/Off',
                                    use('FEG1 < Vel').if_parameter('F1 On/Off').has_value('on'),
                                    use('FEG1 A < Vel').if_parameter('F1 On/Off').has_value('on'),
                                    use('FEG1 Attack').if_parameter('F1 On/Off').has_value('on'),
                                    use('FEG1 Decay').if_parameter('F1 On/Off').has_value('on'),
                                    use('FEG1 Sustain').if_parameter('F1 On/Off').has_value('on'),
                                    use('FEG1 S Time').if_parameter('F1 On/Off').has_value('on'),
                                    use('FEG1 Rel').if_parameter('F1 On/Off').has_value('on'))
                     }),
                 (
                  'Filt. 2 Env.',
                  {PARAMETERS_KEY: (
                                    'F2 On/Off',
                                    use('FEG2 < Vel').if_parameter('F1 On/Off').has_value('on'),
                                    use('FEG2 A < Vel').if_parameter('F1 On/Off').has_value('on'),
                                    use('FEG2 Attack').if_parameter('F1 On/Off').has_value('on'),
                                    use('FEG2 Decay').if_parameter('F1 On/Off').has_value('on'),
                                    use('FEG2 Sustain').if_parameter('F1 On/Off').has_value('on'),
                                    use('FEG2 S Time').if_parameter('F1 On/Off').has_value('on'),
                                    use('FEG2 Rel').if_parameter('F1 On/Off').has_value('on'))
                     }),
                 (
                  'Filt. Modulation',
                  {PARAMETERS_KEY: (
                                    'F1 On/Off',
                                    use('F1 Freq < LFO').if_parameter('F1 On/Off').has_value('on'),
                                    use('F1 Freq < Env').if_parameter('F1 On/Off').has_value('on'),
                                    use('F1 Res < LFO').if_parameter('F1 On/Off').has_value('on'),
                                    'F2 On/Off',
                                    use('F2 Freq < LFO').if_parameter('F2 On/Off').has_value('on'),
                                    use('F2 Freq < Env').if_parameter('F2 On/Off').has_value('on'),
                                    use('F2 Res < LFO').if_parameter('F2 On/Off').has_value('on'))
                     }),
                 (
                  'Amp',
                  {PARAMETERS_KEY: (
                                    use('AMP1 Level').if_parameter('AMP1 On/Off').has_value('on'),
                                    use('AMP1 Pan').if_parameter('AMP1 On/Off').has_value('on'),
                                    use('AMP1 < LFO').if_parameter('AMP1 On/Off').has_value('on'),
                                    use('').if_parameter('LFO1 On/Off').has_value('off').else_use('LFO1 Speed').if_parameter('LFO1 Sync').has_value('Hertz').else_use('LFO1 SncRate'),
                                    use('AMP2 Level').if_parameter('AMP2 On/Off').has_value('on'),
                                    use('AMP2 Pan').if_parameter('AMP2 On/Off').has_value('on'),
                                    use('AMP2 < LFO').if_parameter('AMP2 On/Off').has_value('on'),
                                    use('').if_parameter('LFO2 On/Off').has_value('off').else_use('LFO2 Speed').if_parameter('LFO2 Sync').has_value('Hertz').else_use('LFO2 SncRate'))
                     }),
                 (
                  'Amp 1 Envelope',
                  {PARAMETERS_KEY: (
                                    'AMP1 On/Off',
                                    use('AEG1 < Vel').if_parameter('AMP1 On/Off').has_value('on'),
                                    use('AEG1 A < Vel').if_parameter('AMP1 On/Off').has_value('on'),
                                    use('AEG1 Attack').if_parameter('AMP1 On/Off').has_value('on'),
                                    use('AEG1 Decay').if_parameter('AMP1 On/Off').has_value('on'),
                                    use('AEG1 Sustain').if_parameter('AMP1 On/Off').has_value('on'),
                                    use('AEG1 S Time').if_parameter('AMP1 On/Off').has_value('on'),
                                    use('AEG1 Rel').if_parameter('AMP1 On/Off').has_value('on'))
                     }),
                 (
                  'Amp 2 Envelope',
                  {PARAMETERS_KEY: (
                                    'AMP2 On/Off',
                                    use('AEG2 < Vel').if_parameter('AMP2 On/Off').has_value('on'),
                                    use('AEG2 A < Vel').if_parameter('AMP2 On/Off').has_value('on'),
                                    use('AEG2 Attack').if_parameter('AMP2 On/Off').has_value('on'),
                                    use('AEG2 Decay').if_parameter('AMP2 On/Off').has_value('on'),
                                    use('AEG2 Sustain').if_parameter('AMP2 On/Off').has_value('on'),
                                    use('AEG2 S Time').if_parameter('AMP2 On/Off').has_value('on'),
                                    use('AEG2 Rel').if_parameter('AMP2 On/Off').has_value('on'))
                     }),
                 (
                  'Noise & Unison',
                  {PARAMETERS_KEY: (
                                    'Noise On/Off',
                                    use('Noise Level').if_parameter('Noise On/Off').has_value('on'),
                                    use('Noise Color').if_parameter('Noise On/Off').has_value('on'),
                                    use('Noise Balance').if_parameter('Noise On/Off').has_value('on'),
                                    'Unison On/Off',
                                    use('Unison Detune').if_parameter('Unison On/Off').has_value('on'),
                                    use('Unison Delay').if_parameter('Unison On/Off').has_value('on'),
                                    '')
                     }),
                 (
                  'Performance',
                  {PARAMETERS_KEY: (
                                    'Glide On/Off',
                                    use('Glide Time').if_parameter('Glide On/Off').has_value('on'),
                                    use('Glide Mode').if_parameter('Glide On/Off').has_value('on'),
                                    use('Glide Legato').if_parameter('Glide On/Off').has_value('on'),
                                    'PB Range', 'Key Stretch', 'Key Error', 'Voices')
                     }),
                 (
                  'LFO 1',
                  {PARAMETERS_KEY: (
                                    'LFO1 On/Off',
                                    use('LFO1 Sync').if_parameter('LFO1 On/Off').has_value('on'),
                                    use('').if_parameter('LFO1 On/Off').has_value('off').else_use('LFO1 Speed').if_parameter('LFO1 Sync').has_value('Hertz').else_use('LFO1 SncRate'),
                                    use('LFO1 Shape').if_parameter('LFO1 On/Off').has_value('on'),
                                    use('').if_parameter('LFO1 On/Off').has_value('off').else_use('LFO1 PW').if_parameter('LFO1 Shape').has_value('Rect').else_use('LFO1 PW').if_parameter('LFO1 Shape').has_value('Tri'),
                                    use('LFO1 Phase').if_parameter('LFO1 On/Off').has_value('on'),
                                    use('LFO1 Delay').if_parameter('LFO1 On/Off').has_value('on'),
                                    use('LFO1 Fade In').if_parameter('LFO1 On/Off').has_value('on'))
                     }),
                 (
                  'LFO 2',
                  {PARAMETERS_KEY: (
                                    'LFO2 On/Off',
                                    use('LFO2 Sync').if_parameter('LFO2 On/Off').has_value('on'),
                                    use('').if_parameter('LFO2 On/Off').has_value('off').else_use('LFO2 Speed').if_parameter('LFO2 Sync').has_value('Hertz').else_use('LFO2 SncRate'),
                                    use('LFO2 Shape').if_parameter('LFO2 On/Off').has_value('on'),
                                    use('').if_parameter('LFO2 On/Off').has_value('off').else_use('LFO2 PW').if_parameter('LFO2 Shape').has_value('Rect').else_use('LFO2 PW').if_parameter('LFO2 Shape').has_value('Tri'),
                                    use('LFO2 Phase').if_parameter('LFO2 On/Off').has_value('on'),
                                    use('LFO2 Delay').if_parameter('LFO2 On/Off').has_value('on'),
                                    use('LFO2 Fade In').if_parameter('LFO2 On/Off').has_value('on'))
                     }),
                 (
                  'Vibrato',
                  {PARAMETERS_KEY: (
                                    'Vib On/Off',
                                    use('Vib Amount').if_parameter('Vib On/Off').has_value('on'),
                                    use('Vib Speed').if_parameter('Vib On/Off').has_value('on'),
                                    use('Vib Delay').if_parameter('Vib On/Off').has_value('on'),
                                    use('Vib Fade-In').if_parameter('Vib On/Off').has_value('on'),
                                    use('Vib Error').if_parameter('Vib On/Off').has_value('on'),
                                    use('Vib < ModWh').if_parameter('Vib On/Off').has_value('on'),
                                    '')
                     }))),
   'Collision': IndexedDict((
               (
                MAIN_KEY,
                {PARAMETERS_KEY: (
                                  use('Res 1 Type').if_parameter('Res 1 On/Off').has_value('on'),
                                  use('').if_parameter('Res 1 On/Off').has_value('off').else_use('').if_parameter('Res 1 Type').has_value('Tube').else_use('').if_parameter('Res 1 Type').has_value('Pipe').else_use('Res 1 Brightness'),
                                  use('').if_parameter('Res 1 On/Off').has_value('off').else_use('').if_parameter('Res 1 Type').has_value('Tube').else_use('Res 1 Opening').if_parameter('Res 1 Type').has_value('Pipe').else_use('Res 1 Inharmonics'),
                                  use('Res 1 Decay').if_parameter('Res 1 On/Off').has_value('on'),
                                  use('').if_parameter('Res 1 On/Off').has_value('off').else_use('Res 1 Radius').if_parameter('Res 1 Type').has_value('Tube').else_use('Res 1 Radius').if_parameter('Res 1 Type').has_value('Pipe').else_use('Res 1 Material'),
                                  use('Mallet Stiffness').if_parameter('Mallet On/Off').has_value('on'),
                                  use('Mallet Noise Amount').if_parameter('Mallet On/Off').has_value('on'),
                                  'Volume')
                   }),
               (
                'Mix',
                {PARAMETERS_KEY: (
                                  use('Res 1 Volume').if_parameter('Res 1 On/Off').has_value('on'),
                                  use('Panorama').if_parameter('Res 1 On/Off').has_value('on'),
                                  use('Res 1 Bleed').if_parameter('Res 1 On/Off').has_value('on'),
                                  use('Res 2 Volume').if_parameter('Res 2 On/Off').has_value('on'),
                                  use('Res 2 Panorama').if_parameter('Res 2 On/Off').has_value('on'),
                                  use('Res 2 Bleed').if_parameter('Res 2 On/Off').has_value('on'),
                                  'Structure', 'Volume')
                   }),
               (
                'Mallet',
                {PARAMETERS_KEY: (
                                  'Mallet On/Off',
                                  use('Mallet Volume').if_parameter('Mallet On/Off').has_value('on'),
                                  use('Mallet Noise Amount').if_parameter('Mallet On/Off').has_value('on'),
                                  use('Mallet Stiffness').if_parameter('Mallet On/Off').has_value('on'),
                                  use('Mallet Noise Color').if_parameter('Mallet On/Off').has_value('on'),
                                  use('Mallet Modulation').if_parameter('Mallet On/Off').has_value('on'),
                                  use('Mallet Volume < Vel').if_parameter('Mallet On/Off').has_value('on'),
                                  use('Mallet Noise Amount < Vel').if_parameter('Mallet On/Off').has_value('on'))
                   }),
               (
                'Noise Envelope',
                {PARAMETERS_KEY: (
                                  'Noise On/Off',
                                  use('Noise Volume').if_parameter('Noise On/Off').has_value('on'),
                                  use('Noise Volume < Key').if_parameter('Noise On/Off').has_value('on'),
                                  use('Noise Volume < Vel').if_parameter('Noise On/Off').has_value('on'),
                                  use('Noise Attack').if_parameter('Noise On/Off').has_value('on'),
                                  use('Noise Sustain').if_parameter('Noise On/Off').has_value('on'),
                                  use('Noise Decay').if_parameter('Noise On/Off').has_value('on'),
                                  use('Noise Release').if_parameter('Noise On/Off').has_value('on'))
                   }),
               (
                'Noise Filter',
                {PARAMETERS_KEY: (
                                  'Noise On/Off',
                                  use('Noise Volume').if_parameter('Noise On/Off').has_value('on'),
                                  use('Noise Filter Type').if_parameter('Noise On/Off').has_value('on'),
                                  use('Noise Filter Freq').if_parameter('Noise On/Off').has_value('on'),
                                  use('Noise Filter Q').if_parameter('Noise On/Off').has_value('on'),
                                  use('Noise Freq < Key').if_parameter('Noise On/Off').has_value('on'),
                                  use('Noise Freq < Vel').if_parameter('Noise On/Off').has_value('on'),
                                  use('Noise Freq < Env').if_parameter('Noise On/Off').has_value('on'))
                   }),
               (
                'Res. 1 Body',
                {PARAMETERS_KEY: (
                                  'Res 1 On/Off',
                                  use('Res 1 Type').if_parameter('Res 1 On/Off').has_value('on'),
                                  use('').if_parameter('Res 1 On/Off').has_value('off').else_use('Res 1 Ratio').if_parameter('Res 1 Type').has_value('Plate').else_use('Res 1 Ratio').if_parameter('Res 1 Type').has_value('Membrane'),
                                  use('Res 1 Decay').if_parameter('Res 1 On/Off').has_value('on'),
                                  use('').if_parameter('Res 1 On/Off').has_value('off').else_use('Res 1 Radius').if_parameter('Res 1 Type').has_value('Tube').else_use('Res 1 Radius').if_parameter('Res 1 Type').has_value('Pipe').else_use('Res 1 Material'),
                                  use('').if_parameter('Res 1 On/Off').has_value('off').else_use('').if_parameter('Res 1 Type').has_value('Tube').else_use('').if_parameter('Res 1 Type').has_value('Pipe').else_use('Res 1 Listening L'),
                                  use('').if_parameter('Res 1 On/Off').has_value('off').else_use('').if_parameter('Res 1 Type').has_value('Tube').else_use('').if_parameter('Res 1 Type').has_value('Pipe').else_use('Res 1 Listening R'),
                                  use('').if_parameter('Res 1 On/Off').has_value('off').else_use('').if_parameter('Res 1 Type').has_value('Tube').else_use('').if_parameter('Res 1 Type').has_value('Pipe').else_use('Res 1 Hit'))
                   }),
               (
                'Res. 1 Tune',
                {PARAMETERS_KEY: (
                                  'Res 1 On/Off',
                                  use('').if_parameter('Res 1 On/Off').has_value('off').else_use('').if_parameter('Res 1 Type').has_value('Tube').else_use('').if_parameter('Res 1 Type').has_value('Pipe').else_use('Res 1 Brightness'),
                                  use('Res 1 Quality').if_parameter('Res 1 On/Off').has_value('on'),
                                  use('').if_parameter('Res 1 On/Off').has_value('off').else_use('').if_parameter('Res 1 Type').has_value('Tube').else_use('Res 1 Opening').if_parameter('Res 1 Type').has_value('Pipe').else_use('Res 1 Inharmonics'),
                                  use('Res 1 Tune').if_parameter('Res 1 On/Off').has_value('on'),
                                  use('Res 1 Fine Tune').if_parameter('Res 1 On/Off').has_value('on'),
                                  use('Res 1 Pitch Env.').if_parameter('Res 1 On/Off').has_value('on'),
                                  use('Res 1 Pitch Env. Time').if_parameter('Res 1 On/Off').has_value('on'))
                   }),
               (
                'Res. 2 Body',
                {PARAMETERS_KEY: (
                                  'Res 2 On/Off',
                                  use('Res 2 Type').if_parameter('Res 2 On/Off').has_value('on'),
                                  use('').if_parameter('Res 2 On/Off').has_value('off').else_use('Res 2 Ratio').if_parameter('Res 2 Type').has_value('Plate').else_use('Res 2 Ratio').if_parameter('Res 2 Type').has_value('Membrane'),
                                  use('Res 2 Decay').if_parameter('Res 2 On/Off').has_value('on'),
                                  use('').if_parameter('Res 2 On/Off').has_value('off').else_use('Res 2 Radius').if_parameter('Res 2 Type').has_value('Tube').else_use('Res 2 Radius').if_parameter('Res 2 Type').has_value('Pipe').else_use('Res 2 Material'),
                                  use('').if_parameter('Res 2 On/Off').has_value('off').else_use('').if_parameter('Res 2 Type').has_value('Tube').else_use('').if_parameter('Res 2 Type').has_value('Pipe').else_use('Res 2 Listening L'),
                                  use('').if_parameter('Res 2 On/Off').has_value('off').else_use('').if_parameter('Res 2 Type').has_value('Tube').else_use('').if_parameter('Res 2 Type').has_value('Pipe').else_use('Res 2 Listening R'),
                                  use('').if_parameter('Res 2 On/Off').has_value('off').else_use('').if_parameter('Res 2 Type').has_value('Tube').else_use('').if_parameter('Res 2 Type').has_value('Pipe').else_use('Res 2 Hit'))
                   }),
               (
                'Res. 2 Tune',
                {PARAMETERS_KEY: (
                                  'Res 2 On/Off',
                                  use('').if_parameter('Res 2 On/Off').has_value('off').else_use('').if_parameter('Res 2 Type').has_value('Tube').else_use('').if_parameter('Res 2 Type').has_value('Pipe').else_use('Res 2 Brightness'),
                                  use('Res 2 Quality').if_parameter('Res 2 On/Off').has_value('on'),
                                  use('').if_parameter('Res 2 On/Off').has_value('off').else_use('').if_parameter('Res 2 Type').has_value('Tube').else_use('Res 2 Opening').if_parameter('Res 2 Type').has_value('Pipe').else_use('Res 2 Inharmonics'),
                                  use('Res 2 Tune').if_parameter('Res 2 On/Off').has_value('on'),
                                  use('Res 2 Fine Tune').if_parameter('Res 2 On/Off').has_value('on'),
                                  use('Res 2 Pitch Env.').if_parameter('Res 2 On/Off').has_value('on'),
                                  use('Res 2 Pitch Env. Time').if_parameter('Res 2 On/Off').has_value('on'))
                   }),
               (
                'LFO 1',
                {PARAMETERS_KEY: (
                                  'LFO 1 On/Off',
                                  use('LFO 1 Depth').if_parameter('LFO 1 On/Off').has_value('on'),
                                  use('LFO 1 Shape').if_parameter('LFO 1 On/Off').has_value('on'),
                                  use('LFO 1 Sync').if_parameter('LFO 1 On/Off').has_value('on'),
                                  use('').if_parameter('LFO 1 On/Off').has_value('off').else_use('LFO 1 Sync Rate').if_parameter('LFO 1 Sync').has_value('Sync').else_use('LFO 1 Rate'),
                                  use('LFO 1 Offset').if_parameter('LFO 1 On/Off').has_value('on'),
                                  use('LFO 1 Destination A').if_parameter('LFO 1 On/Off').has_value('on'),
                                  use('LFO 1 Destination A Amount').if_parameter('LFO 1 On/Off').has_value('on'))
                   }),
               (
                'LFO 2',
                {PARAMETERS_KEY: (
                                  'LFO 2 On/Off',
                                  use('LFO 2 Depth').if_parameter('LFO 2 On/Off').has_value('on'),
                                  use('LFO 2 Shape').if_parameter('LFO 2 On/Off').has_value('on'),
                                  use('LFO 2 Sync').if_parameter('LFO 2 On/Off').has_value('on'),
                                  use('').if_parameter('LFO 2 On/Off').has_value('off').else_use('LFO 2 Sync Rate').if_parameter('LFO 2 Sync').has_value('Sync').else_use('LFO 2 Rate'),
                                  use('LFO 2 Offset').if_parameter('LFO 2 On/Off').has_value('on'),
                                  use('LFO 2 Destination A').if_parameter('LFO 2 On/Off').has_value('on'),
                                  use('LFO 2 Destination A Amount').if_parameter('LFO 2 On/Off').has_value('on'))
                   }),
               (
                'Mallet Mod.',
                {PARAMETERS_KEY: (
                                  'Mallet On/Off',
                                  use('Mallet Volume < Key').if_parameter('Mallet On/Off').has_value('on'),
                                  use('Mallet Volume < Vel').if_parameter('Mallet On/Off').has_value('on'),
                                  use('Mallet Noise Amount < Key').if_parameter('Mallet On/Off').has_value('on'),
                                  use('Mallet Noise Amount < Vel').if_parameter('Mallet On/Off').has_value('on'),
                                  use('Mallet Stiffness < Key').if_parameter('Mallet On/Off').has_value('on'),
                                  use('Mallet Stiffness < Vel').if_parameter('Mallet On/Off').has_value('on'),
                                  '')
                   }))),
   'LoungeLizard': IndexedDict((
                  (
                   MAIN_KEY,
                   {PARAMETERS_KEY: ('M Stiffness', 'M Force', 'Noise Amount', 'F Tine Vol', 'F Tone Vol', 'F Release',
 'P Symmetry', 'Volume')
                      }),
                  (
                   'Mallet',
                   {PARAMETERS_KEY: ('M Stiffness', 'M Force', 'Noise Pitch', 'Noise Decay', 'Noise Amount', 'M Stiff < Vel',
 'M Force < Vel', 'Volume')
                      }),
                  (
                   'Fork',
                   {PARAMETERS_KEY: ('F Tine Color', 'F Tine Decay', 'F Tine Vol', 'F Tone Vol', 'F Tone Decay', 'F Release',
 'F Tine < Key', 'Volume')
                      }),
                  (
                   'Damper',
                   {PARAMETERS_KEY: ('Damp Tone', 'Damp Balance', 'Damp Amount', '', '', '', '', 'Volume')
                      }),
                  (
                   'Pickup',
                   {PARAMETERS_KEY: ('P Symmetry', 'P Distance', 'P Amp In', 'P Amp Out', 'Pickup Model', 'P Amp < Key',
 '', 'Volume')
                      }),
                  (
                   'Modulation',
                   {PARAMETERS_KEY: ('M Stiff < Vel', 'M Stiff < Key', 'M Force < Vel', 'M Force < Key', 'Noise < Key',
 'F Tine < Key', 'P Amp < Key', 'Volume')
                      }),
                  (
                   'Global',
                   {PARAMETERS_KEY: ('KB Stretch', 'PB Range', '', '', 'Voices', 'Semitone', 'Detune', 'Volume')
                      }))),
   'InstrumentImpulse': IndexedDict((
                       (
                        MAIN_KEY,
                        {PARAMETERS_KEY: ('1 Transpose', '1 Volume', '3 Transpose', '3 Volume', '7 Transpose', '7 Volume', '8 Transpose',
 '8 Volume')
                           }),
                       (
                        'Pad 1',
                        {PARAMETERS_KEY: ('1 Start', '1 Envelope Decay', '1 Stretch Factor', '1 Saturator Drive', '1 Envelope Type',
 '1 Transpose', '1 Volume <- Vel', '1 Volume')
                           }),
                       (
                        '1 Filt/Mod/Pan',
                        {PARAMETERS_KEY: ('1 Filter Type', '1 Filter Freq', '1 Filter Res', '1 Filter <- Vel', '1 Filter <- Random',
 '1 Pan', '1 Pan <- Vel', '1 Pan <- Random')
                           }),
                       (
                        'Pad 2',
                        {PARAMETERS_KEY: ('2 Start', '2 Envelope Decay', '2 Stretch Factor', '2 Saturator Drive', '2 Envelope Type',
 '2 Transpose', '2 Volume <- Vel', '2 Volume')
                           }),
                       (
                        '2 Filt/Mod/Pan',
                        {PARAMETERS_KEY: ('2 Filter Type', '2 Filter Freq', '2 Filter Res', '2 Filter <- Vel', '2 Filter <- Random',
 '2 Pan', '2 Pan <- Vel', '2 Pan <- Random')
                           }),
                       (
                        'Pad 3',
                        {PARAMETERS_KEY: ('3 Start', '3 Envelope Decay', '3 Stretch Factor', '3 Saturator Drive', '3 Envelope Type',
 '3 Transpose', '3 Volume <- Vel', '3 Volume')
                           }),
                       (
                        '3 Filt/Mod/Pan',
                        {PARAMETERS_KEY: ('3 Filter Type', '3 Filter Freq', '3 Filter Res', '3 Filter <- Vel', '3 Filter <- Random',
 '3 Pan', '3 Pan <- Vel', '3 Pan <- Random')
                           }),
                       (
                        'Pad 4',
                        {PARAMETERS_KEY: ('4 Start', '4 Envelope Decay', '4 Stretch Factor', '4 Saturator Drive', '4 Envelope Type',
 '4 Transpose', '4 Volume <- Vel', '4 Volume')
                           }),
                       (
                        '4 Filt/Mod/Pan',
                        {PARAMETERS_KEY: ('4 Filter Type', '4 Filter Freq', '4 Filter Res', '4 Filter <- Vel', '4 Filter <- Random',
 '4 Pan', '4 Pan <- Vel', '4 Pan <- Random')
                           }),
                       (
                        'Pad 5',
                        {PARAMETERS_KEY: ('5 Start', '5 Envelope Decay', '5 Stretch Factor', '5 Saturator Drive', '5 Envelope Type',
 '5 Transpose', '5 Volume <- Vel', '5 Volume')
                           }),
                       (
                        '5 Filt/Mod/Pan',
                        {PARAMETERS_KEY: ('5 Filter Type', '5 Filter Freq', '5 Filter Res', '5 Filter <- Vel', '5 Filter <- Random',
 '5 Pan', '5 Pan <- Vel', '5 Pan <- Random')
                           }),
                       (
                        'Pad 6',
                        {PARAMETERS_KEY: ('6 Start', '6 Envelope Decay', '6 Stretch Factor', '6 Saturator Drive', '6 Envelope Type',
 '6 Transpose', '6 Volume <- Vel', '6 Volume')
                           }),
                       (
                        '6 Filt/Mod/Pan',
                        {PARAMETERS_KEY: ('6 Filter Type', '6 Filter Freq', '6 Filter Res', '6 Filter <- Vel', '6 Filter <- Random',
 '6 Pan', '6 Pan <- Vel', '6 Pan <- Random')
                           }),
                       (
                        'Pad 7',
                        {PARAMETERS_KEY: ('7 Start', '7 Envelope Decay', '7 Stretch Factor', '7 Saturator Drive', '7 Envelope Type',
 '7 Transpose', '7 Volume <- Vel', '7 Volume')
                           }),
                       (
                        '7 Filt/Mod/Pan',
                        {PARAMETERS_KEY: ('7 Filter Type', '7 Filter Freq', '7 Filter Res', '7 Filter <- Vel', '7 Filter <- Random',
 '7 Pan', '7 Pan <- Vel', '7 Pan <- Random')
                           }),
                       (
                        'Pad 8',
                        {PARAMETERS_KEY: ('8 Start', '8 Envelope Decay', '8 Stretch Factor', '8 Saturator Drive', '8 Envelope Type',
 '8 Transpose', '8 Volume <- Vel', '8 Volume')
                           }),
                       (
                        '8 Filt/Mod/Pan',
                        {PARAMETERS_KEY: ('8 Filter Type', '8 Filter Freq', '8 Filter Res', '8 Filter <- Vel', '8 Filter <- Random',
 '8 Pan', '8 Pan <- Vel', '8 Pan <- Random')
                           }),
                       (
                        'Stretch Modes',
                        {PARAMETERS_KEY: ('1 Stretch Mode', '2 Stretch Mode', '3 Stretch Mode', '4 Stretch Mode', '5 Stretch Mode',
 '6 Stretch Mode', '7 Stretch Mode', '8 Stretch Mode')
                           }),
                       (
                        'Global',
                        {PARAMETERS_KEY: ('Global Time', 'Global Transpose', 'Global Volume', '', '', '', '', '')
                           }))),
   'Operator': IndexedDict((
              (
               'Oscillators',
               {PARAMETERS_KEY: (
                                 'Oscillator',
                                 use('Osc-A On').if_parameter('Oscillator').has_value('A').else_use('Osc-B On').if_parameter('Oscillator').has_value('B').else_use('Osc-C On').if_parameter('Oscillator').has_value('C').else_use('Osc-D On').if_parameter('Oscillator').has_value('D'),
                                 use('Osc-A Wave').if_parameter('Oscillator').has_value('A').else_use('Osc-B Wave').if_parameter('Oscillator').has_value('B').else_use('Osc-C Wave').if_parameter('Oscillator').has_value('C').else_use('Osc-D Wave').if_parameter('Oscillator').has_value('D'),
                                 use('A Fix On ').if_parameter('Oscillator').has_value('A').else_use('B Fix On ').if_parameter('Oscillator').has_value('B').else_use('C Fix On ').if_parameter('Oscillator').has_value('C').else_use('D Fix On ').if_parameter('Oscillator').has_value('D'),
                                 use('A Fix Freq').if_parameter('Oscillator').has_value('A').and_parameter('A Fix On ').has_value('on').else_use('A Coarse').if_parameter('Oscillator').has_value('A').else_use('B Fix Freq').if_parameter('Oscillator').has_value('B').and_parameter('B Fix On ').has_value('on').else_use('B Coarse').if_parameter('Oscillator').has_value('B').else_use('C Fix Freq').if_parameter('Oscillator').has_value('C').and_parameter('C Fix On ').has_value('on').else_use('C Coarse').if_parameter('Oscillator').has_value('C').else_use('D Fix Freq').if_parameter('Oscillator').has_value('D').and_parameter('D Fix On ').has_value('on').else_use('D Coarse').if_parameter('Oscillator').has_value('D'),
                                 use('A Fix Freq Mul').if_parameter('Oscillator').has_value('A').and_parameter('A Fix On ').has_value('on').else_use('A Fine').if_parameter('Oscillator').has_value('A').else_use('B Fix Freq Mul').if_parameter('Oscillator').has_value('B').and_parameter('B Fix On ').has_value('on').else_use('B Fine').if_parameter('Oscillator').has_value('B').else_use('C Fix Freq Mul').if_parameter('Oscillator').has_value('C').and_parameter('C Fix On ').has_value('on').else_use('C Fine').if_parameter('Oscillator').has_value('C').else_use('D Fix Freq Mul').if_parameter('Oscillator').has_value('D').and_parameter('D Fix On ').has_value('on').else_use('D Fine').if_parameter('Oscillator').has_value('D'),
                                 use('Osc-A Level').if_parameter('Oscillator').has_value('A').else_use('Osc-B Level').if_parameter('Oscillator').has_value('B').else_use('Osc-C Level').if_parameter('Oscillator').has_value('C').else_use('Osc-D Level').if_parameter('Oscillator').has_value('D'),
                                 'Algorithm')
                  }),
              (
               'Osc. Envelopes',
               {PARAMETERS_KEY: (
                                 'Oscillator',
                                 use('Osc-A On').if_parameter('Oscillator').has_value('A').else_use('Osc-B On').if_parameter('Oscillator').has_value('B').else_use('Osc-C On').if_parameter('Oscillator').has_value('C').else_use('Osc-D On').if_parameter('Oscillator').has_value('D'),
                                 use('Ae Init').if_parameter('Oscillator').has_value('A').else_use('Be Init').if_parameter('Oscillator').has_value('B').else_use('Ce Init').if_parameter('Oscillator').has_value('C').else_use('De Init').if_parameter('Oscillator').has_value('D'),
                                 use('Ae Attack').if_parameter('Oscillator').has_value('A').else_use('Be Attack').if_parameter('Oscillator').has_value('B').else_use('Ce Attack').if_parameter('Oscillator').has_value('C').else_use('De Attack').if_parameter('Oscillator').has_value('D'),
                                 use('Ae Peak').if_parameter('Oscillator').has_value('A').else_use('Be Peak').if_parameter('Oscillator').has_value('B').else_use('Ce Peak').if_parameter('Oscillator').has_value('C').else_use('De Peak').if_parameter('Oscillator').has_value('D'),
                                 use('Ae Decay').if_parameter('Oscillator').has_value('A').else_use('Be Decay').if_parameter('Oscillator').has_value('B').else_use('Ce Decay').if_parameter('Oscillator').has_value('C').else_use('De Decay').if_parameter('Oscillator').has_value('D'),
                                 use('Ae Sustain').if_parameter('Oscillator').has_value('A').else_use('Be Sustain').if_parameter('Oscillator').has_value('B').else_use('Ce Sustain').if_parameter('Oscillator').has_value('C').else_use('De Sustain').if_parameter('Oscillator').has_value('D'),
                                 use('Ae Release').if_parameter('Oscillator').has_value('A').else_use('Be Release').if_parameter('Oscillator').has_value('B').else_use('Ce Release').if_parameter('Oscillator').has_value('C').else_use('De Release').if_parameter('Oscillator').has_value('D'))
                  }),
              (
               'Filter',
               {PARAMETERS_KEY: (
                                 'Filter On',
                                 use('Filter Type').if_parameter('Filter Type').is_available(True).else_use('Filter Type (Legacy)'),
                                 use('Filter Freq'),
                                 use('Filter Res').if_parameter('Filter Res').is_available(True).else_use('Filter Res (Legacy)'),
                                 use('Filter Circuit - LP/HP').if_parameter('Filter Type').has_value('Lowpass').else_use('Filter Circuit - LP/HP').if_parameter('Filter Type').has_value('Highpass').else_use('Filter Circuit - BP/NO/Morph'),
                                 use('Filter Morph').if_parameter('Filter Type').has_value('Morph').else_use('').if_parameter('Filter Type').has_value('Lowpass').and_parameter('Filter Circuit - LP/HP').has_value('Clean').else_use('').if_parameter('Filter Type').has_value('Highpass').and_parameter('Filter Circuit - LP/HP').has_value('Clean').else_use('').if_parameter('Filter Type').has_value('Bandpass').and_parameter('Filter Circuit - BP/NO/Morph').has_value('Clean').else_use('').if_parameter('Filter Type').has_value('Notch').and_parameter('Filter Circuit - BP/NO/Morph').has_value('Clean').else_use('Filter Drive'),
                                 'Shaper Type', 'Shaper Mix'),
                  OPTIONS_KEY: (
                              use('Filter Slope').if_parameter('Filter On').has_value('on').and_parameter('Filter Slope').is_available(True),
                              '', '', '', '', '', '')
                  }),
              (
               'Filt. Env.',
               {PARAMETERS_KEY: ('Filter On', 'Fe Init', 'Fe Attack', 'Fe Decay', 'Fe Sustain', 'Fe Release', 'Fe End',
 'Fe Amount')
                  }),
              (
               'Filt. Mod.',
               {PARAMETERS_KEY: ('Filter On', 'Filt < Vel', 'Filt < LFO', 'Filt < Key', '', '', '', '')
                  }),
              (
               'LFO',
               {PARAMETERS_KEY: (
                                 'LFO On', 'LFO Type', 'LFO Range',
                                 use('LFO Sync').if_parameter('LFO Range').has_value('Sync').else_use('LFO Rate'),
                                 'LFO Amt', 'Filt < LFO',
                                 use('Oscillator').if_parameter('LFO On').has_value('on'),
                                 use('Osc-A < LFO').if_parameter('Oscillator').has_value('A').else_use('Osc-B < LFO').if_parameter('Oscillator').has_value('B').else_use('Osc-C < LFO').if_parameter('Oscillator').has_value('C').else_use('Osc-D < LFO').if_parameter('Oscillator').has_value('D'))
                  }),
              (
               'LFO Env.',
               {PARAMETERS_KEY: ('LFO On', 'Le Init', 'Le Attack', 'Le Decay', 'Le Sustain', 'Le Release', 'Le End',
 'LFO Amt')
                  }),
              (
               'Pitch',
               {PARAMETERS_KEY: (
                                 'Transpose', 'Spread', 'Glide On', 'Glide Time',
                                 'Pe R < Vel', 'LFO < Pe',
                                 use('Oscillator').if_parameter('Pe On').has_value('on'),
                                 use('Osc-A < Pe').if_parameter('Oscillator').has_value('A').else_use('Osc-B < Pe').if_parameter('Oscillator').has_value('B').else_use('Osc-C < Pe').if_parameter('Oscillator').has_value('C').else_use('Osc-D < Pe').if_parameter('Oscillator').has_value('D'))
                  }),
              (
               'Pitch Env.',
               {PARAMETERS_KEY: ('Pe On', 'Pe Init', 'Pe Attack', 'Pe Decay', 'Pe Sustain', 'Pe Release', 'Pe End',
 'Pe Amount')
                  }),
              (
               'Global',
               {PARAMETERS_KEY: ('Panorama', 'Pan < Rnd', 'Pan < Key', 'Filt < Key', 'Time', 'Time < Key', 'Tone',
 'Volume')
                  }),
              (
               'Modulation',
               {PARAMETERS_KEY: (
                                 'Oscillator',
                                 use('Osc-A Lev < Vel').if_parameter('Oscillator').has_value('A').else_use('Osc-B Lev < Vel').if_parameter('Oscillator').has_value('B').else_use('Osc-C Lev < Vel').if_parameter('Oscillator').has_value('C').else_use('Osc-D Lev < Vel').if_parameter('Oscillator').has_value('D'),
                                 use('A Freq<Vel').if_parameter('Oscillator').has_value('A').else_use('B Freq<Vel').if_parameter('Oscillator').has_value('B').else_use('C Freq<Vel').if_parameter('Oscillator').has_value('C').else_use('D Freq<Vel').if_parameter('Oscillator').has_value('D'),
                                 use('A Quantize').if_parameter('Oscillator').has_value('A').else_use('B Quantize').if_parameter('Oscillator').has_value('B').else_use('C Quantize').if_parameter('Oscillator').has_value('C').else_use('D Quantize').if_parameter('Oscillator').has_value('D'),
                                 use('Osc-A Retrig').if_parameter('Oscillator').has_value('A').else_use('Osc-B Retrig').if_parameter('Oscillator').has_value('B').else_use('Osc-C Retrig').if_parameter('Oscillator').has_value('C').else_use('Osc-D Retrig').if_parameter('Oscillator').has_value('D'),
                                 use('Osc-A Phase').if_parameter('Oscillator').has_value('A').else_use('Osc-B Phase').if_parameter('Oscillator').has_value('B').else_use('Osc-C Phase').if_parameter('Oscillator').has_value('C').else_use('Osc-D Phase').if_parameter('Oscillator').has_value('D'),
                                 'LFO Dst B', 'LFO Amt B')
                  }))),
   'MultiSampler': IndexedDict((
                  (
                   MAIN_KEY,
                   {PARAMETERS_KEY: (
                                     'Ve Attack', 'Ve Decay', 'Ve Sustain', 'Ve Release',
                                     use('Pan').if_parameter('F On').has_value('off').else_use('Filter Type').if_parameter('Filter Type').is_available(True).else_use('Filter Type (Legacy)'),
                                     use('Transpose').if_parameter('F On').has_value('off').else_use('Filter Freq'),
                                     use('Detune').if_parameter('F On').has_value('off').else_use('Filter Res').if_parameter('Filter Res').is_available(True).else_use('Filter Res (Legacy)'),
                                     'Volume')
                      }),
                  (
                   'Volume Env.',
                   {PARAMETERS_KEY: ('Ve Init', 'Ve Attack', 'Ve Peak', 'Ve Decay', 'Ve Sustain', 'Ve Release', 'Vol < Vel',
 'Volume')
                      }),
                  (
                   'Env. Loop & Pan',
                   {PARAMETERS_KEY: (
                                     'Ve Mode',
                                     use('Ve Loop').if_parameter('Ve Mode').has_value('Loop').else_use('Ve Retrig').if_parameter('Ve Mode').has_value('Beat').else_use('Ve Retrig').if_parameter('Ve Mode').has_value('Sync').else_use(''),
                                     'Ve R < Vel', '', 'Pan', 'Pan < Rnd', 'Time', 'Time < Key')
                      }),
                  (
                   'Filter',
                   {PARAMETERS_KEY: (
                                     'F On',
                                     use('Filter Type').if_parameter('Filter Type').is_available(True).else_use('Filter Type (Legacy)'),
                                     use('Filter Freq'),
                                     use('Filter Res').if_parameter('Filter Res').is_available(True).else_use('Filter Res (Legacy)'),
                                     use('Filter Circuit - LP/HP').if_parameter('Filter Type').has_value('Lowpass').else_use('Filter Circuit - LP/HP').if_parameter('Filter Type').has_value('Highpass').else_use('Filter Circuit - BP/NO/Morph'),
                                     use('Filter Morph').if_parameter('Filter Type').has_value('Morph').else_use('').if_parameter('Filter Type').has_value('Lowpass').and_parameter('Filter Circuit - LP/HP').has_value('Clean').else_use('').if_parameter('Filter Type').has_value('Highpass').and_parameter('Filter Circuit - LP/HP').has_value('Clean').else_use('').if_parameter('Filter Type').has_value('Bandpass').and_parameter('Filter Circuit - BP/NO/Morph').has_value('Clean').else_use('').if_parameter('Filter Type').has_value('Notch').and_parameter('Filter Circuit - BP/NO/Morph').has_value('Clean').else_use('Filter Drive'),
                                     'Filt < Vel', 'Filt < Key'),
                      OPTIONS_KEY: (
                                  use('Filter Slope').if_parameter('F On').has_value('on').and_parameter('Filter Slope').is_available(True),
                                  '', '', '', '', '', '', '')
                      }),
                  (
                   'Filt. Env',
                   {PARAMETERS_KEY: ('Fe On', 'Fe < Env', 'Fe Init', 'Fe Attack', 'Fe Decay', 'Fe Peak', 'Fe Sustain',
 'Fe Release')
                      }),
                  (
                   'Shaper',
                   {PARAMETERS_KEY: (
                                     'Fe On', 'Fe End', 'Fe Mode',
                                     use('Fe Loop').if_parameter('Fe Mode').has_value('Loop').else_use('Fe Retrig').if_parameter('Fe Mode').has_value('Beat').else_use('Fe Retrig').if_parameter('Fe Mode').has_value('Sync').else_use(''),
                                     'Fe R < Vel', 'Shaper On', 'Shaper Type', 'Shaper Amt')
                      }),
                  (
                   'Osc. pg. 1',
                   {PARAMETERS_KEY: ('Osc On', 'O Mode', 'Oe Init', 'Oe Attack', 'Oe Peak', 'Oe Decay', 'Oe Sustain', 'Oe Release')
                      }),
                  (
                   'Osc. pg. 2',
                   {PARAMETERS_KEY: (
                                     'Oe End', 'Oe Mode',
                                     use('Oe Loop').if_parameter('Oe Mode').has_value('Loop').else_use('Oe Retrig').if_parameter('Oe Mode').has_value('Beat').else_use('Oe Retrig').if_parameter('Oe Mode').has_value('Sync').else_use(''),
                                     'O Type', 'O Volume', 'O Fix On',
                                     use('O Coarse').if_parameter('O Fix On').has_value('off').else_use('O Fix Freq'),
                                     use('O Fine').if_parameter('O Fix On').has_value('off').else_use('O Fix Freq Mul'))
                      }),
                  (
                   'Pitch Env.',
                   {PARAMETERS_KEY: ('Pe On', 'Pe < Env', 'Pe Init', 'Pe Attack', 'Pe Peak', 'Pe Decay', 'Pe Sustain',
 'Pe Release')
                      }),
                  (
                   'Pitch Env. 2',
                   {PARAMETERS_KEY: (
                                     'Pe On', 'Pe End', 'Pe R < Vel', 'Pe Mode',
                                     use('Pe Loop').if_parameter('Pe Mode').has_value('Loop').else_use('Pe Retrig').if_parameter('Pe Mode').has_value('Beat').else_use('Pe Retrig').if_parameter('Pe Mode').has_value('Sync').else_use(''),
                                     '', '', '')
                      }),
                  (
                   'Pitch/Glide',
                   {PARAMETERS_KEY: (
                                     'Pe On', 'Spread', 'Transpose', 'Detune', 'Key Zone Shift', 'Glide Mode',
                                     use('Glide Time').if_parameter('Glide Mode').has_value('On'),
                                     '')
                      }),
                  (
                   'LFO1 pg. 1',
                   {PARAMETERS_KEY: (
                                     'L 1 On', 'L 1 Wave', 'L 1 Sync',
                                     use('L 1 Sync Rate').if_parameter('L 1 Sync').has_value('Sync').else_use('L 1 Rate'),
                                     'Vol < LFO', 'Filt < LFO', 'Pan < LFO', 'Pitch < LFO')
                      }),
                  (
                   'LFO1 pg. 2',
                   {PARAMETERS_KEY: ('L 1 On', 'L 1 Retrig', 'L 1 Offset', 'L 1 Attack', '', '', '', '')
                      }),
                  (
                   'LFO2 pg. 1',
                   {PARAMETERS_KEY: (
                                     'L 2 On', 'L 2 Wave', 'L 2 Sync',
                                     use('L 2 Sync Rate').if_parameter('L 2 Sync').has_value('Sync').else_use('L 2 Rate'),
                                     'L 2 Retrig', 'L 2 Offset', 'L 2 Attack', '')
                      }),
                  (
                   'LFO2 pg. 2',
                   {PARAMETERS_KEY: (
                                     'L 2 On', 'L 2 St Mode',
                                     use('L 2 Spin').if_parameter('L 2 St Mode').has_value('Spin').else_use('L 2 Phase'),
                                     '', '', '', '', '')
                      }),
                  (
                   'LFO3 pg. 1',
                   {PARAMETERS_KEY: (
                                     'L 3 On', 'L 3 Wave', 'L 3 Sync',
                                     use('L 3 Sync Rate').if_parameter('L 3 Sync').has_value('Sync').else_use('L 3 Rate'),
                                     'L 3 Retrig', 'L 3 Offset', 'L 3 Attack',
                                     '')
                      }),
                  (
                   'LFO3 pg. 2',
                   {PARAMETERS_KEY: (
                                     'L 3 On', 'L 3 St Mode',
                                     use('L 3 Spin').if_parameter('L 3 St Mode').has_value('Spin').else_use('L 3 Phase'),
                                     '', '', '', '', '')
                      }),
                  (
                   'Aux Env. 1',
                   {PARAMETERS_KEY: (
                                     'Ae On', 'Ae Init', 'Ae Peak', 'Ae Sustain',
                                     'Ae End', 'Ae Mode',
                                     use('Ae Loop').if_parameter('Ae Mode').has_value('Loop').else_use('Ae Retrig').if_parameter('Ae Mode').has_value('Beat').else_use('Ae Retrig').if_parameter('Ae Mode').has_value('Sync'),
                                     '')
                      }),
                  (
                   'Aux Env. 2',
                   {PARAMETERS_KEY: ('Ae On', 'Ae Attack', 'Ae Decay', 'Ae Release', 'Ae A Slope', 'Ae D Slope', 'Ae R Slope',
 '')
                      }))),
   'OriginalSimpler': IndexedDict((
                     (
                      MAIN_KEY,
                      {PARAMETERS_KEY: (
                                        use('Ve Attack').if_parameter('Multi Sample').has_value('on').else_use('Zoom'),
                                        use('Ve Decay').if_parameter('Multi Sample').has_value('on').else_use('Start'),
                                        use('Ve Sustain').if_parameter('Multi Sample').has_value('on').else_use('End'),
                                        use('Ve Release').if_parameter('Multi Sample').has_value('on').else_use('Fade In').if_parameter('Mode').has_value('One-Shot').else_use('Nudge').if_parameter('Mode').has_value('Slicing').else_use('S Start').if_parameter('Mode').has_value('Classic'),
                                        use('Pan').if_parameter('Multi Sample').has_value('on').else_use('Fade Out').if_parameter('Mode').has_value('One-Shot').else_use('Playback').if_parameter('Mode').has_value('Slicing').else_use('S Length').if_parameter('Mode').has_value('Classic'),
                                        use('Transpose').if_parameter('Multi Sample').has_value('on').else_use('Transpose').if_parameter('Mode').has_value('One-Shot').else_use('Slice by').if_parameter('Mode').has_value('Slicing').else_use('S Loop Length').if_parameter('Mode').has_value('Classic'),
                                        use('Detune').if_parameter('Multi Sample').has_value('on').else_use('Gain').if_parameter('Mode').has_value('One-Shot').else_use('Sensitivity').if_parameter('Slice by').has_value('Transient').and_parameter('Mode').has_value('Slicing').else_use('Division').if_parameter('Slice by').has_value('Beat').and_parameter('Mode').has_value('Slicing').else_use('Regions').if_parameter('Slice by').has_value('Region').and_parameter('Mode').has_value('Slicing').else_use('Pad Slicing').if_parameter('Slice by').has_value('Manual').and_parameter('Mode').has_value('Slicing').else_use('Sensitivity').if_parameter('Mode').has_value('Slicing').else_use('S Loop Fade').if_parameter('Mode').has_value('Classic').and_parameter('Warp').has_value('off').else_use('Detune'),
                                        use('Volume').if_parameter('Multi Sample').has_value('on').else_use('Mode')),
                         OPTIONS_KEY: (
                                     use('').if_parameter('Multi Sample').has_value('on').else_use('Loop').if_parameter('Mode').has_value('Classic').else_use('Trigger Mode'),
                                     use('').if_parameter('Multi Sample').has_value('on').else_use('Warp as X Bars'),
                                     use('').if_parameter('Multi Sample').has_value('on').else_use(':2'),
                                     use('').if_parameter('Multi Sample').has_value('on').else_use('x2'),
                                     use('').if_parameter('Multi Sample').has_value('on').else_use('Clear Slices').if_parameter('Slice by').has_value('Manual').and_parameter('Mode').has_value('Slicing').else_use('Reset Slices').if_parameter('Mode').has_value('Slicing'),
                                     use('').if_parameter('Multi Sample').has_value('on').else_use('Split Slice').if_parameter('Mode').has_value('Slicing').else_use('Crop'),
                                     use('').if_parameter('Multi Sample').has_value('on').else_use('Reverse')),
                         SHOW_WAVEFORM_KEY: True
                         }),
                     (
                      'Global',
                      {PARAMETERS_KEY: (
                                        'Glide Mode', 'Glide Time',
                                        use('').if_parameter('Mode').has_value('One-Shot').else_use('Voices').if_parameter('Mode').has_value('Classic').else_use('Voices').if_parameter('Mode').has_value('Slicing').and_parameter('Playback').has_value('Poly'),
                                        'Transpose', 'Detune', 'Vol < Vel', 'Gain', 'Volume'),
                         OPTIONS_KEY: (
                                     '',
                                     use('').if_parameter('Mode').has_value('One-Shot').else_use('Retrigger').if_parameter('Mode').has_value('Classic').else_use('Retrigger').if_parameter('Mode').has_value('Slicing').and_parameter('Playback').has_value('Poly'),
                                     '', '', '', '', ''),
                         SHOW_WAVEFORM_KEY: True
                         }),
                     (
                      'Envelopes',
                      {PARAMETERS_KEY: (
                                        'Env. Type',
                                        use('Fe On').if_parameter('Env. Type').has_value('Filter').else_use('Pe On').if_parameter('Env. Type').has_value('Pitch').else_use('Ve Attack').if_parameter('Mode').has_value('Classic').else_use('Fade In'),
                                        use('Fe Attack').if_parameter('Env. Type').has_value('Filter').else_use('Pe Attack').if_parameter('Env. Type').has_value('Pitch').else_use('Ve Decay').if_parameter('Mode').has_value('Classic').else_use('Fade Out'),
                                        use('Fe Decay').if_parameter('Env. Type').has_value('Filter').else_use('Pe Decay').if_parameter('Env. Type').has_value('Pitch').else_use('Ve Sustain').if_parameter('Mode').has_value('Classic').else_use('Volume'),
                                        use('Fe Sustain').if_parameter('Env. Type').has_value('Filter').else_use('Pe Sustain').if_parameter('Env. Type').has_value('Pitch').else_use('Ve Release').if_parameter('Mode').has_value('Classic'),
                                        use('Fe Release').if_parameter('Env. Type').has_value('Filter').else_use('Pe Release').if_parameter('Env. Type').has_value('Pitch'),
                                        use('Fe < Env').if_parameter('Env. Type').has_value('Filter').else_use('Pe < Env').if_parameter('Env. Type').has_value('Pitch'),
                                        use('Filter Freq').if_parameter('Env. Type').has_value('Filter').else_use('Transpose').if_parameter('Env. Type').has_value('Pitch')),
                         OPTIONS_KEY: ('', '', '', '', '', '', ''),
                         SHOW_WAVEFORM_KEY: False
                         }),
                     (
                      'Warp',
                      {PARAMETERS_KEY: (
                                        use('').if_parameter('Multi Sample').has_value('on').else_use('Zoom'),
                                        use('').if_parameter('Multi Sample').has_value('on').else_use('Start'),
                                        use('').if_parameter('Multi Sample').has_value('on').else_use('End'),
                                        use('').if_parameter('Multi Sample').has_value('on').else_use('Warp'),
                                        use('').if_parameter('Multi Sample').has_value('on').else_use('').if_parameter('Warp').has_value('off').else_use('Warp Mode'),
                                        use('').if_parameter('Multi Sample').has_value('on').else_use('').if_parameter('Warp').has_value('off').else_use('Preserve').if_parameter('Warp Mode').has_value('Beats').else_use('Grain Size Tones').if_parameter('Warp Mode').has_value('Tones').else_use('Grain Size Texture').if_parameter('Warp Mode').has_value('Texture').else_use('Formants').if_parameter('Warp Mode').has_value('Pro'),
                                        use('').if_parameter('Multi Sample').has_value('on').else_use('').if_parameter('Warp').has_value('off').else_use('Loop Mode').if_parameter('Warp Mode').has_value('Beats').else_use('Flux').if_parameter('Warp Mode').has_value('Texture').else_use('Envelope Complex Pro').if_parameter('Warp Mode').has_value('Pro'),
                                        use('').if_parameter('Multi Sample').has_value('on').else_use('').if_parameter('Warp').has_value('off').else_use('Envelope').if_parameter('Warp Mode').has_value('Beats')),
                         OPTIONS_KEY: (
                                     use('').if_parameter('Multi Sample').has_value('on').else_use('Warp as X Bars'),
                                     use('').if_parameter('Multi Sample').has_value('on').else_use(':2'),
                                     use('').if_parameter('Multi Sample').has_value('on').else_use('x2'),
                                     '', '', '', '', ''),
                         SHOW_WAVEFORM_KEY: True
                         }),
                     (
                      'Filter',
                      {PARAMETERS_KEY: (
                                        'F On',
                                        use('Filter Type').if_parameter('Filter Type').is_available(True).else_use('Filter Type (Legacy)'),
                                        'Filter Freq',
                                        use('Filter Res').if_parameter('Filter Res').is_available(True).else_use('Filter Res (Legacy)'),
                                        use('Filter Circuit - LP/HP').if_parameter('Filter Type').has_value('Lowpass').else_use('Filter Circuit - LP/HP').if_parameter('Filter Type').has_value('Highpass').else_use('Filter Circuit - BP/NO/Morph'),
                                        use('Filter Morph').if_parameter('Filter Type').has_value('Morph').else_use('').if_parameter('Filter Type').has_value('Lowpass').and_parameter('Filter Circuit - LP/HP').has_value('Clean').else_use('').if_parameter('Filter Type').has_value('Highpass').and_parameter('Filter Circuit - LP/HP').has_value('Clean').else_use('').if_parameter('Filter Type').has_value('Bandpass').and_parameter('Filter Circuit - BP/NO/Morph').has_value('Clean').else_use('').if_parameter('Filter Type').has_value('Notch').and_parameter('Filter Circuit - BP/NO/Morph').has_value('Clean').else_use('Filter Drive'),
                                        'Filt < Vel', 'Filt < LFO'),
                         OPTIONS_KEY: (
                                     use('Filter Slope').if_parameter('F On').has_value('on').and_parameter('Filter Slope').is_available(True),
                                     '', '', '', '', '', '')
                         }),
                     (
                      'LFO',
                      {PARAMETERS_KEY: (
                                        'L On', 'L Wave',
                                        use('L Rate').if_parameter('L Sync').has_value('Free').else_use('L Sync Rate'),
                                        'L Attack', 'L R < Key', 'Vol < LFO', 'L Retrig', 'L Offset'),
                         OPTIONS_KEY: (
                                     '',
                                     use('LFO Sync Type').if_parameter('L On').has_value('on'),
                                     '', '', '', '', '')
                         }),
                     (
                      'Pan',
                      {PARAMETERS_KEY: ('Pan', 'Spread', 'Pan < Rnd', 'Pan < LFO', '', '', '', ''),
                         OPTIONS_KEY: ('', '', '', '', '', '', '')
                         }))),
   'StringStudio': IndexedDict((
                  (
                   MAIN_KEY,
                   {PARAMETERS_KEY: (
                                     use('Excitator Type').if_parameter('Exc On/Off').has_value('on'),
                                     use('Exc ForceMassProt').if_parameter('Exc On/Off').has_value('on'),
                                     use('Exc FricStiff').if_parameter('Exc On/Off').has_value('on'),
                                     use('Exc Velocity').if_parameter('Exc On/Off').has_value('on'),
                                     use('E Pos').if_parameter('Exc On/Off').has_value('on'),
                                     'String Decay', 'Str Damping', 'Volume')
                      }),
                  (
                   'Excitator',
                   {PARAMETERS_KEY: (
                                     'Exc On/Off',
                                     use('Excitator Type').if_parameter('Exc On/Off').has_value('on'),
                                     use('Exc ForceMassProt').if_parameter('Exc On/Off').has_value('on'),
                                     use('Exc FricStiff').if_parameter('Exc On/Off').has_value('on'),
                                     use('Exc Velocity').if_parameter('Exc On/Off').has_value('on'),
                                     use('E Pos').if_parameter('Exc On/Off').has_value('on'),
                                     use('E Pos Abs').if_parameter('Exc On/Off').has_value('on'),
                                     'Volume')
                      }),
                  (
                   'String & Pickup',
                   {PARAMETERS_KEY: (
                                     'String Decay', 'S Decay < Key', 'S Decay Ratio', 'Str Inharmon',
                                     'Str Damping', 'S Damp < Key', 'Pickup On/Off',
                                     use('Pickup Pos').if_parameter('Pickup On/Off').has_value('on'))
                      }),
                  (
                   'Damper',
                   {PARAMETERS_KEY: (
                                     'Damper On',
                                     use('Damper Mass').if_parameter('Damper On').has_value('on'),
                                     use('D Stiffness').if_parameter('Damper On').has_value('on'),
                                     use('Damp Pos').if_parameter('Damper On').has_value('on'),
                                     use('D Damping').if_parameter('Damper On').has_value('on'),
                                     use('Damper Gated').if_parameter('Damper On').has_value('on'),
                                     use('').if_parameter('Damper On').has_value('off').else_use('D Velocity').if_parameter('Damper Gated').has_value('on').else_use(''),
                                     use('D Pos Abs').if_parameter('Damper On').has_value('on'))
                      }),
                  (
                   'Termination',
                   {PARAMETERS_KEY: (
                                     'Term On/Off',
                                     use('Term Mass').if_parameter('Term On/Off').has_value('on'),
                                     use('Term Fng Stiff').if_parameter('Term On/Off').has_value('on'),
                                     use('Term Fret Stiff').if_parameter('Term On/Off').has_value('on'),
                                     use('T Mass < Vel').if_parameter('Term On/Off').has_value('on'),
                                     use('T Mass < Key').if_parameter('Term On/Off').has_value('on'),
                                     '', 'Volume')
                      }),
                  (
                   'Body',
                   {PARAMETERS_KEY: (
                                     'Body On/Off',
                                     use('Body Type').if_parameter('Body On/Off').has_value('on'),
                                     use('Body Size').if_parameter('Body On/Off').has_value('on'),
                                     use('Body Decay').if_parameter('Body On/Off').has_value('on'),
                                     use('Body Low-Cut').if_parameter('Body On/Off').has_value('on'),
                                     use('Body High-Cut').if_parameter('Body On/Off').has_value('on'),
                                     use('Body Mix').if_parameter('Body On/Off').has_value('on'),
                                     'Volume')
                      }),
                  (
                   'Filter',
                   {PARAMETERS_KEY: (
                                     'Filter On/Off',
                                     use('Filter Type').if_parameter('Filter On/Off').has_value('on'),
                                     use('Filter Freq').if_parameter('Filter On/Off').has_value('on'),
                                     use('Filter Reso').if_parameter('Filter On/Off').has_value('on'),
                                     use('Freq < Env').if_parameter('Filter On/Off').has_value('on'),
                                     use('Freq < LFO').if_parameter('Filter On/Off').has_value('on'),
                                     use('Reso < Env').if_parameter('Filter On/Off').has_value('on'),
                                     use('Reso < LFO').if_parameter('Filter On/Off').has_value('on'))
                      }),
                  (
                   'LFO',
                   {PARAMETERS_KEY: (
                                     'LFO On/Off',
                                     use('LFO Shape').if_parameter('LFO On/Off').has_value('on'),
                                     use('LFO Sync On').if_parameter('LFO On/Off').has_value('on'),
                                     use('').if_parameter('LFO On/Off').has_value('off').else_use('LFO SyncRate').if_parameter('LFO Sync On').has_value('Beat').else_use('LFO Speed'),
                                     use('LFO Delay').if_parameter('LFO On/Off').has_value('on'),
                                     use('LFO Fade In').if_parameter('LFO On/Off').has_value('on'),
                                     '', '')
                      }),
                  (
                   'Vibrato',
                   {PARAMETERS_KEY: (
                                     'Vibrato On/Off',
                                     use('Vib Delay').if_parameter('Vibrato On/Off').has_value('on'),
                                     use('Vib Fade-In').if_parameter('Vibrato On/Off').has_value('on'),
                                     use('Vib Speed').if_parameter('Vibrato On/Off').has_value('on'),
                                     use('Vib Amount').if_parameter('Vibrato On/Off').has_value('on'),
                                     use('Vib < ModWh').if_parameter('Vibrato On/Off').has_value('on'),
                                     use('Vib Error').if_parameter('Vibrato On/Off').has_value('on'),
                                     '')
                      }),
                  (
                   'Unison & Portamento',
                   {PARAMETERS_KEY: (
                                     'Unison On/Off',
                                     use('Unison Voices').if_parameter('Unison On/Off').has_value('on'),
                                     use('Uni Delay').if_parameter('Unison On/Off').has_value('on'),
                                     use('Uni Detune').if_parameter('Unison On/Off').has_value('on'),
                                     'Porta On/Off',
                                     use('Porta Time').if_parameter('Porta On/Off').has_value('on'),
                                     use('Porta Legato').if_parameter('Porta On/Off').has_value('on'),
                                     use('Porta Prop').if_parameter('Porta On/Off').has_value('on'))
                      }),
                  (
                   'Global',
                   {PARAMETERS_KEY: ('Octave', 'Semitone', 'Fine Tune', 'Voices', 'PB Depth', 'Stretch', 'Error', 'Key Priority')
                      }),
                  (
                   'Filt. Env.',
                   {PARAMETERS_KEY: (
                                     'FEG On/Off',
                                     use('FEG Attack').if_parameter('FEG On/Off').has_value('on'),
                                     use('FEG Decay').if_parameter('FEG On/Off').has_value('on'),
                                     use('FEG Sustain').if_parameter('FEG On/Off').has_value('on'),
                                     use('FEG Release').if_parameter('FEG On/Off').has_value('on'),
                                     use('FEG Att < Vel').if_parameter('FEG On/Off').has_value('on'),
                                     use('FEG < Vel').if_parameter('FEG On/Off').has_value('on'),
                                     '')
                      }),
                  (
                   'Excitator Mod.',
                   {PARAMETERS_KEY: (
                                     use('Exc Prot < Vel').if_parameter('Exc On/Off').has_value('on'),
                                     use('Exc Prot < Key').if_parameter('Exc On/Off').has_value('on'),
                                     use('Exc Stiff < Vel').if_parameter('Exc On/Off').has_value('on'),
                                     use('Exc Stiff < Key').if_parameter('Exc On/Off').has_value('on'),
                                     use('Exc Vel < Vel').if_parameter('Exc On/Off').has_value('on'),
                                     use('Exc Vel < Key').if_parameter('Exc On/Off').has_value('on'),
                                     use('E Pos < Vel').if_parameter('Exc On/Off').has_value('on'),
                                     use('E Pos < Key').if_parameter('Exc On/Off').has_value('on'))
                      }),
                  (
                   'Mass Mod.',
                   {PARAMETERS_KEY: (
                                     use('D Mass < Key').if_parameter('Damper On').has_value('on'),
                                     use('D Stiff < Key').if_parameter('Damper On').has_value('on'),
                                     use('D Pos < Key').if_parameter('Damper On').has_value('on'),
                                     use('D Pos < Vel').if_parameter('Damper On').has_value('on'),
                                     use('Damper Gated').if_parameter('Damper On').has_value('on'),
                                     use('').if_parameter('Damper On').has_value('off').else_use('D Velo < Key').if_parameter('Damper Gated').has_value('on').else_use(''),
                                     '', '')
                      }))),
   'MidiArpeggiator': IndexedDict((
                     (
                      MAIN_KEY,
                      {PARAMETERS_KEY: (
                                        'Style',
                                        use('Synced Rate').if_parameter('Sync On').has_value('on').else_use('Free Rate'),
                                        'Gate', 'Offset',
                                        'Hold On', 'Tranpose Key', 'Transp. Steps', 'Transp. Dist.')
                         }),
                     (
                      'Rhythm',
                      {PARAMETERS_KEY: (
                                        'Sync On',
                                        use('Synced Rate').if_parameter('Sync On').has_value('on').else_use('Free Rate'),
                                        'Groove', 'Offset', 'Repeats', 'Gate', 'Retrigger Mode',
                                        use('Ret. Interval').if_parameter('Retrigger Mode').has_value('Beat'))
                         }),
                     (
                      'Pitch/Vel.',
                      {PARAMETERS_KEY: ('Tranpose Mode', 'Tranpose Key', 'Transp. Steps', 'Transp. Dist.', 'Velocity On',
 'Vel. Retrigger', 'Velocity Decay', 'Velocity Target')
                         }))),
   'MidiChord': IndexedDict((
               (
                'Shift',
                {PARAMETERS_KEY: ('Shift1', 'Shift2', 'Shift3', 'Shift4', 'Shift5', 'Shift6', '', '')
                   }),
               (
                'Velocity',
                {PARAMETERS_KEY: ('Velocity1', 'Velocity2', 'Velocity3', 'Velocity4', 'Velocity5', 'Velocity6', '',
 '')
                   }))),
   'MidiNoteLength': IndexedDict((
                    (
                     MAIN_KEY,
                     {PARAMETERS_KEY: (
                                       'Trigger Mode', 'Sync On',
                                       use('Synced Length').if_parameter('Sync On').has_value('on').else_use('Time Length'),
                                       'Gate', 'On/Off-Balance', 'Decay Time', 'Decay Key Scale', '')
                        }),)),
   'MidiPitcher': IndexedDict((
                 (
                  MAIN_KEY,
                  {PARAMETERS_KEY: ('Pitch', 'Range', 'Lowest', '', '', '', '', '')
                     }),)),
   'MidiRandom': IndexedDict((
                (
                 MAIN_KEY,
                 {PARAMETERS_KEY: ('Chance', 'Choices', 'Mode', 'Scale', 'Sign', '', '', '')
                    }),)),
   'MidiScale': IndexedDict((
               (
                MAIN_KEY,
                {PARAMETERS_KEY: ('Base', 'Transpose', 'Range', 'Lowest', 'Fold', '', '', '')
                   }),)),
   'MidiVelocity': IndexedDict((
                  (
                   MAIN_KEY,
                   {PARAMETERS_KEY: ('Mode', 'Drive', 'Compand', 'Out Hi', 'Out Low', 'Range', 'Lowest', 'Random')
                      }),)),
   'Amp': IndexedDict((
         (
          'Global',
          {PARAMETERS_KEY: ('Amp Type', 'Bass', 'Middle', 'Treble', 'Presence', 'Gain', 'Volume', 'Dry/Wet')
             }),
         (
          'Dual/Mono',
          {PARAMETERS_KEY: ('Dual Mono', '', '', '', '', '', '', '')
             }))),
   'AutoFilter': IndexedDict((
                (
                 MAIN_KEY,
                 {PARAMETERS_KEY: (
                                   use('Filter Type').if_parameter('Filter Type').is_available(True).else_use('Filter Type (Legacy)'),
                                   use('Frequency'),
                                   use('Resonance').if_parameter('Resonance').is_available(True).else_use('Resonance (Legacy)'),
                                   use('Filter Circuit - LP/HP').if_parameter('Filter Type').has_value('Lowpass').else_use('Filter Circuit - LP/HP').if_parameter('Filter Type').has_value('Highpass').else_use('Filter Circuit - BP/NO/Morph'),
                                   use('Morph').if_parameter('Filter Type').has_value('Morph').else_use('').if_parameter('Filter Type').has_value('Lowpass').and_parameter('Filter Circuit - LP/HP').has_value('Clean').else_use('').if_parameter('Filter Type').has_value('Highpass').and_parameter('Filter Circuit - LP/HP').has_value('Clean').else_use('').if_parameter('Filter Type').has_value('Bandpass').and_parameter('Filter Circuit - BP/NO/Morph').has_value('Clean').else_use('').if_parameter('Filter Type').has_value('Notch').and_parameter('Filter Circuit - BP/NO/Morph').has_value('Clean').else_use('Drive'),
                                   'LFO Amount', 'LFO Sync',
                                   use('LFO Frequency').if_parameter('LFO Sync').has_value('Free').else_use('LFO Sync Rate')),
                    OPTIONS_KEY: (
                                use('Slope').if_parameter('Slope').is_available(True),
                                '', '', '', '', '', '', '')
                    }),
                (
                 'Envelope',
                 {PARAMETERS_KEY: (
                                   use('Filter Type').if_parameter('Filter Type').is_available(True).else_use('Filter Type (Legacy)'),
                                   use('Frequency'),
                                   use('Resonance').if_parameter('Resonance').is_available(True).else_use('Resonance (Legacy)'),
                                   use('Morph').if_parameter('Filter Type').has_value('Morph SVF').else_use('Drive'),
                                   'Env. Attack', 'Env. Release', 'Env. Modulation', '')
                    }),
                (
                 'LFO',
                 {PARAMETERS_KEY: (
                                   'LFO Amount', 'LFO Waveform', 'LFO Sync',
                                   use('LFO Frequency').if_parameter('LFO Sync').has_value('Free').else_use('LFO Sync Rate'),
                                   use('').if_parameter('LFO Waveform').has_value('S&H Mono').else_use('LFO Offset').if_parameter('LFO Sync').has_value('Sync').else_use('LFO Stereo Mode'),
                                   use('').if_parameter('LFO Waveform').has_value('S&H Mono').else_use('LFO Phase').if_parameter('LFO Sync').has_value('Sync').else_use('LFO Phase').if_parameter('LFO Stereo Mode').has_value('Phase').else_use('LFO Spin'),
                                   'LFO Quantize On', 'LFO Quantize Rate')
                    }),
                (
                 'Sidechain',
                 {PARAMETERS_KEY: ('Ext. In On', 'Ext. In Mix', 'Ext. In Gain', '', '', '', '', '')
                    }))),
   'AutoPan': IndexedDict((
             (
              MAIN_KEY,
              {PARAMETERS_KEY: (
                                'Amount', 'Shape', 'Invert', 'Waveform', 'LFO Type',
                                use('Sync Rate').if_parameter('LFO Type').has_value('Beats').else_use('Frequency'),
                                use('Width (Random)').if_parameter('Waveform').has_value('S&H Width').else_use('Stereo Mode').if_parameter('LFO Type').has_value('Frequency').else_use('Offset'),
                                use('').if_parameter('Waveform').has_value('S&H Width').else_use('Phase').if_parameter('LFO Type').has_value('Beats').else_use('Spin').if_parameter('Stereo Mode').has_value('Spin').else_use('Phase'))
                 }),)),
   'BeatRepeat': IndexedDict((
                (
                 MAIN_KEY,
                 {PARAMETERS_KEY: ('Grid', 'Interval', 'Offset', 'Gate', 'Pitch', 'Pitch Decay', 'Variation', 'Chance')
                    }),
                (
                 'Filt/Mix',
                 {PARAMETERS_KEY: ('Filter On', 'Filter Freq', 'Filter Width', '', 'Mix Type', 'Volume', 'Decay', 'Chance')
                    }),
                (
                 'Repeat Rate',
                 {PARAMETERS_KEY: ('Repeat', 'Interval', 'Offset', 'Gate', 'Grid', 'Block Triplets', 'Variation', 'Variation Type')
                    }))),
   'Cabinet': IndexedDict((
             (
              MAIN_KEY,
              {PARAMETERS_KEY: ('Cabinet Type', 'Microphone Type', 'Microphone Position', 'Dual Mono', '', '', '',
 'Dry/Wet')
                 }),)),
   'Chorus': IndexedDict((
            (
             'Chorus',
             {PARAMETERS_KEY: (
                               'LFO Amount', 'LFO Rate', 'Delay 1 Time', 'Delay 1 HiPass',
                               'Delay 2 Mode',
                               use('').if_parameter('Delay 2 Mode').has_value('off').else_use('Delay 2 Time'),
                               'Feedback', 'Dry/Wet')
                }),
            (
             'Other',
             {PARAMETERS_KEY: ('LFO Extend On', 'Polarity', 'Link On', '', '', '', '', '')
                }))),
   'Compressor2': IndexedDict((
                 (
                  MAIN_KEY,
                  {PARAMETERS_KEY: (
                                    'Threshold',
                                    use('Expansion Ratio').if_parameter('Model').has_value('Expand').else_use('Ratio'),
                                    'Model', 'Knee', 'Attack',
                                    use('Release').if_parameter('Auto Release On/Off').has_value('off').else_use('Makeup').if_parameter('Ext. In On').has_value('off'),
                                    'Dry/Wet', 'Output Gain')
                     }),
                 (
                  'Sidechain',
                  {PARAMETERS_KEY: (
                                    'Ext. In On', 'Ext. In Gain', 'Ext. In Mix', 'Side Listen',
                                    'EQ On', 'EQ Mode', 'EQ Freq',
                                    use('').if_parameter('EQ On').has_value('off').else_use('EQ Gain').if_parameter('EQ Mode').has_value('Low Shelf').else_use('EQ Gain').if_parameter('EQ Mode').has_value('High Shelf').else_use('EQ Gain').if_parameter('EQ Mode').has_value('Bell').else_use('EQ Q'))
                     }),
                 (
                  'Global',
                  {PARAMETERS_KEY: ('Auto Release On/Off', 'Env Mode', 'Makeup', 'LookAhead', '', '', 'Dry/Wet', 'Output Gain')
                     }))),
   'Corpus': IndexedDict((
            (
             MAIN_KEY,
             {PARAMETERS_KEY: (
                               'Resonance Type',
                               use('').if_parameter('Resonance Type').has_value('Tube').else_use('').if_parameter('Resonance Type').has_value('Pipe').else_use('Brightness'),
                               'Decay',
                               use('Radius').if_parameter('Resonance Type').has_value('Tube').else_use('Radius').if_parameter('Resonance Type').has_value('Pipe').else_use('Material'),
                               use('').if_parameter('Resonance Type').has_value('Tube').else_use('Opening').if_parameter('Resonance Type').has_value('Pipe').else_use('Inharmonics'),
                               use('Ratio').if_parameter('Resonance Type').has_value('Plate').else_use('Ratio').if_parameter('Resonance Type').has_value('Membrane').else_use(''),
                               use('Transpose').if_parameter('MIDI Frequency').has_value('on').else_use('Tune'),
                               'Dry Wet')
                }),
            (
             'Body',
             {PARAMETERS_KEY: (
                               'Resonance Type',
                               use('Ratio').if_parameter('Resonance Type').has_value('Plate').else_use('Ratio').if_parameter('Resonance Type').has_value('Membrane'),
                               'Decay',
                               use('Radius').if_parameter('Resonance Type').has_value('Tube').else_use('Radius').if_parameter('Resonance Type').has_value('Pipe').else_use('Material'),
                               use('').if_parameter('Resonance Type').has_value('Tube').else_use('Opening').if_parameter('Resonance Type').has_value('Pipe').else_use('Inharmonics'),
                               use('').if_parameter('Resonance Type').has_value('Tube').else_use('').if_parameter('Resonance Type').has_value('Pipe').else_use('Listening L'),
                               use('').if_parameter('Resonance Type').has_value('Tube').else_use('').if_parameter('Resonance Type').has_value('Pipe').else_use('Listening R'),
                               use('').if_parameter('Resonance Type').has_value('Tube').else_use('').if_parameter('Resonance Type').has_value('Pipe').else_use('Hit'))
                }),
            (
             'LFO',
             {PARAMETERS_KEY: (
                               'LFO On/Off',
                               use('LFO Shape').if_parameter('LFO On/Off').has_value('on'),
                               use('LFO Amount').if_parameter('LFO On/Off').has_value('on'),
                               use('LFO Sync').if_parameter('LFO On/Off').has_value('on'),
                               use('').if_parameter('LFO On/Off').has_value('off').else_use('LFO Rate').if_parameter('LFO Sync').has_value('Free').else_use('LFO Sync Rate'),
                               use('').if_parameter('LFO On/Off').has_value('off').else_use('LFO Stereo Mode').if_parameter('LFO Sync').has_value('Free').else_use('Offset'),
                               use('').if_parameter('LFO On/Off').has_value('off').else_use('Phase').if_parameter('LFO Sync').has_value('Sync').else_use('Spin').if_parameter('LFO Stereo Mode').has_value('Spin'),
                               '')
                }),
            (
             'Tune & Sidechain',
             {PARAMETERS_KEY: (
                               'MIDI Frequency', 'MIDI Mode',
                               use('Transpose').if_parameter('MIDI Frequency').has_value('on').else_use('Tune'),
                               use('Fine').if_parameter('MIDI Frequency').has_value('on'),
                               'Spread',
                               use('').if_parameter('Resonance Type').has_value('Tube').else_use('').if_parameter('Resonance Type').has_value('Pipe').else_use('Brightness'),
                               'Note Off',
                               use('Off Decay').if_parameter('Note Off').has_value('on'))
                }),
            (
             'Filter & Mix',
             {PARAMETERS_KEY: (
                               'Filter On/Off',
                               use('Mid Freq').if_parameter('Filter On/Off').has_value('on'),
                               use('Width').if_parameter('Filter On/Off').has_value('on'),
                               use('').if_parameter('Resonance Type').has_value('Tube').else_use('').if_parameter('Resonance Type').has_value('Pipe').else_use('Resonator Quality'),
                               'Bleed', 'Gain', 'Dry Wet', '')
                }))),
   'Tube': IndexedDict((
          (
           'Character',
           {PARAMETERS_KEY: ('Drive', 'Tube Type', 'Bias', 'Tone', 'Attack', 'Release', 'Envelope', 'Dry/Wet')
              }),
          (
           'Output',
           {PARAMETERS_KEY: ('', '', '', '', '', '', 'Output', 'Dry/Wet')
              }))),
   'Eq8': IndexedDict((
         (
          MAIN_KEY,
          {PARAMETERS_KEY: (
                            'Band',
                            use('1 Filter On A').if_parameter('Band').has_value('1').else_use('2 Filter On A').if_parameter('Band').has_value('2').else_use('3 Filter On A').if_parameter('Band').has_value('3').else_use('4 Filter On A').if_parameter('Band').has_value('4').else_use('5 Filter On A').if_parameter('Band').has_value('5').else_use('6 Filter On A').if_parameter('Band').has_value('6').else_use('7 Filter On A').if_parameter('Band').has_value('7').else_use('8 Filter On A').if_parameter('Band').has_value('8'),
                            use('1 Filter Type A').if_parameter('Band').has_value('1').else_use('2 Filter Type A').if_parameter('Band').has_value('2').else_use('3 Filter Type A').if_parameter('Band').has_value('3').else_use('4 Filter Type A').if_parameter('Band').has_value('4').else_use('5 Filter Type A').if_parameter('Band').has_value('5').else_use('6 Filter Type A').if_parameter('Band').has_value('6').else_use('7 Filter Type A').if_parameter('Band').has_value('7').else_use('8 Filter Type A').if_parameter('Band').has_value('8'),
                            use('1 Frequency A').if_parameter('Band').has_value('1').else_use('2 Frequency A').if_parameter('Band').has_value('2').else_use('3 Frequency A').if_parameter('Band').has_value('3').else_use('4 Frequency A').if_parameter('Band').has_value('4').else_use('5 Frequency A').if_parameter('Band').has_value('5').else_use('6 Frequency A').if_parameter('Band').has_value('6').else_use('7 Frequency A').if_parameter('Band').has_value('7').else_use('8 Frequency A').if_parameter('Band').has_value('8'),
                            use('1 Resonance A').if_parameter('Band').has_value('1').else_use('2 Resonance A').if_parameter('Band').has_value('2').else_use('3 Resonance A').if_parameter('Band').has_value('3').else_use('4 Resonance A').if_parameter('Band').has_value('4').else_use('5 Resonance A').if_parameter('Band').has_value('5').else_use('6 Resonance A').if_parameter('Band').has_value('6').else_use('7 Resonance A').if_parameter('Band').has_value('7').else_use('8 Resonance A').if_parameter('Band').has_value('8'),
                            use('1 Gain A').if_parameter('Band').has_value('1').else_use('2 Gain A').if_parameter('Band').has_value('2').else_use('3 Gain A').if_parameter('Band').has_value('3').else_use('4 Gain A').if_parameter('Band').has_value('4').else_use('5 Gain A').if_parameter('Band').has_value('5').else_use('6 Gain A').if_parameter('Band').has_value('6').else_use('7 Gain A').if_parameter('Band').has_value('7').else_use('8 Gain A').if_parameter('Band').has_value('8'),
                            'Scale', 'Output Gain')
             }),
         (
          '4 Band',
          {PARAMETERS_KEY: (
                            '1 Frequency A',
                            use('1 Gain A').if_parameter('1 Filter Type A').has_value('Low Shelf').else_use('1 Gain A').if_parameter('1 Filter Type A').has_value('Bell').else_use('1 Gain A').if_parameter('1 Filter Type A').has_value('High Shelf').else_use('1 Resonance A'),
                            '2 Frequency A',
                            use('2 Gain A').if_parameter('2 Filter Type A').has_value('Low Shelf').else_use('2 Gain A').if_parameter('2 Filter Type A').has_value('Bell').else_use('2 Gain A').if_parameter('2 Filter Type A').has_value('High Shelf').else_use('2 Resonance A'),
                            '3 Frequency A',
                            use('3 Gain A').if_parameter('3 Filter Type A').has_value('Low Shelf').else_use('3 Gain A').if_parameter('3 Filter Type A').has_value('Bell').else_use('3 Gain A').if_parameter('3 Filter Type A').has_value('High Shelf').else_use('3 Resonance A'),
                            '4 Frequency A',
                            use('4 Gain A').if_parameter('4 Filter Type A').has_value('Low Shelf').else_use('4 Gain A').if_parameter('4 Filter Type A').has_value('Bell').else_use('4 Gain A').if_parameter('4 Filter Type A').has_value('High Shelf').else_use('4 Resonance A'))
             }),
         (
          '8 x Frequency',
          {PARAMETERS_KEY: ('1 Frequency A', '2 Frequency A', '3 Frequency A', '4 Frequency A', '5 Frequency A',
 '6 Frequency A', '7 Frequency A', '8 Frequency A')
             }),
         (
          '8 x Gain',
          {PARAMETERS_KEY: ('1 Gain A', '2 Gain A', '3 Gain A', '4 Gain A', '5 Gain A', '6 Gain A', '7 Gain A',
 '8 Gain A')
             }),
         (
          '8 x Resonance',
          {PARAMETERS_KEY: ('1 Resonance A', '2 Resonance A', '3 Resonance A', '4 Resonance A', '5 Resonance A',
 '6 Resonance A', '7 Resonance A', '8 Resonance A')
             }))),
   'FilterEQ3': IndexedDict((
               (
                'EQ',
                {PARAMETERS_KEY: ('LowOn', 'MidOn', 'HighOn', 'GainLo', 'GainMid', 'GainHi', 'FreqLo', 'FreqHi')
                   }),
               (
                'Slope',
                {PARAMETERS_KEY: ('Slope', '', '', '', '', '', '', '')
                   }))),
   'Erosion': IndexedDict((
             (
              MAIN_KEY,
              {PARAMETERS_KEY: (
                                'Mode', 'Frequency',
                                use('').if_parameter('Mode').has_value('Sine').else_use('Width'),
                                'Amount', '', '', '', '')
                 }),)),
   'ProxyAudioEffectDevice': IndexedDict((
                            (
                             MAIN_KEY,
                             {PARAMETERS_KEY: ('Input Gain', 'Output Gain', 'Dry/Wet', '', '', '', '', '')
                                }),)),
   'FilterDelay': IndexedDict((
                 (
                  MAIN_KEY,
                  {PARAMETERS_KEY: (
                                    '2 Filter Freq', '2 Filter Width', '2 Delay Mode',
                                    use('2 Time Delay').if_parameter('2 Delay Mode').has_value('off').else_use('2 Beat Delay'),
                                    '2 Feedback',
                                    use('1 Volume').if_parameter('1 Input On').has_value('on').else_use('2 Pan'),
                                    '2 Volume',
                                    use('3 Volume').if_parameter('3 Input On').has_value('on').else_use('Dry'))
                     }),
                 (
                  'L Filter',
                  {PARAMETERS_KEY: (
                                    '1 Input On', '1 Filter Freq', '1 Filter Width', '1 Feedback',
                                    '1 Delay Mode',
                                    use('1 Time Delay').if_parameter('1 Delay Mode').has_value('off').else_use('1 Beat Delay'),
                                    use('1 Beat Swing').if_parameter('1 Delay Mode').has_value('on').else_use(''),
                                    '1 Volume')
                     }),
                 (
                  'L+R Filter',
                  {PARAMETERS_KEY: (
                                    '2 Input On', '2 Filter Freq', '2 Filter Width', '2 Feedback',
                                    '2 Delay Mode',
                                    use('2 Time Delay').if_parameter('2 Delay Mode').has_value('off').else_use('2 Beat Delay'),
                                    use('2 Beat Swing').if_parameter('2 Delay Mode').has_value('on').else_use(''),
                                    '2 Volume')
                     }),
                 (
                  'R Filter',
                  {PARAMETERS_KEY: (
                                    '3 Input On', '3 Filter Freq', '3 Filter Width', '3 Feedback',
                                    '3 Delay Mode',
                                    use('3 Time Delay').if_parameter('3 Delay Mode').has_value('off').else_use('3 Beat Delay'),
                                    use('3 Beat Swing').if_parameter('3 Delay Mode').has_value('on').else_use(''),
                                    '3 Volume')
                     }),
                 (
                  'Mix',
                  {PARAMETERS_KEY: ('1 Pan', '2 Pan', '3 Pan', '', '1 Volume', '2 Volume', '3 Volume', 'Dry')
                     }))),
   'Flanger': IndexedDict((
             (
              MAIN_KEY,
              {PARAMETERS_KEY: (
                                'LFO Amount', 'Sync',
                                use('Frequency').if_parameter('Sync').has_value('Free').else_use('Sync Rate'),
                                'Delay Time', 'Hi Pass', 'Env. Modulation', 'Feedback', 'Dry/Wet')
                 }),
             (
              'Envelope',
              {PARAMETERS_KEY: ('Env. Attack', 'Env. Release', 'Env. Modulation', 'Hi Pass', 'Delay Time', 'Feedback',
 'Polarity', 'Dry/Wet')
                 }),
             (
              'LFO / S&H',
              {PARAMETERS_KEY: (
                                'LFO Amount', 'LFO Waveform', 'Sync',
                                use('Frequency').if_parameter('Sync').has_value('Free').else_use('Sync Rate'),
                                use('').if_parameter('LFO Waveform').has_value('S&H Width').else_use('LFO Stereo Mode').if_parameter('Sync').has_value('Free').else_use('LFO Offset'),
                                use('LFO Width (Random)').if_parameter('LFO Waveform').has_value('S&H Width').else_use('LFO Phase').if_parameter('Sync').has_value('Sync').else_use('LFO Phase').if_parameter('LFO Stereo Mode').has_value('Phase').else_use('LFO Spin'),
                                '', '')
                 }))),
   'FrequencyShifter': IndexedDict((
                      (
                       'FreqDrive',
                       {PARAMETERS_KEY: (
                                         'Mode',
                                         use('Ring Mod Frequency').if_parameter('Mode').has_value('Ring Modulation').else_use('Coarse'),
                                         'Wide', 'Fine',
                                         use('Drive On/Off').if_parameter('Mode').has_value('Ring Modulation'),
                                         use('Drive').if_parameter('Drive On/Off').has_value('on').and_parameter('Mode').has_value('Ring Modulation'),
                                         'LFO Amount', 'Dry/Wet')
                          }),
                      (
                       'LFO / S&H',
                       {PARAMETERS_KEY: (
                                         'LFO Amount', 'LFO Waveform', 'Sync',
                                         use('LFO Frequency').if_parameter('Sync').has_value('Free').else_use('Sync Rate'),
                                         use('').if_parameter('LFO Waveform').has_value('S&H Width').else_use('LFO Stereo Mode').if_parameter('Sync').has_value('Free').else_use('LFO Offset'),
                                         use('LFO Width (Random)').if_parameter('LFO Waveform').has_value('S&H Width').else_use('LFO Phase').if_parameter('Sync').has_value('Sync').else_use('LFO Phase').if_parameter('LFO Stereo Mode').has_value('Phase').else_use('LFO Spin'),
                                         '', '')
                          }))),
   'Gate': IndexedDict((
          (
           'Gate',
           {PARAMETERS_KEY: ('Threshold', 'Return', 'FlipMode', 'LookAhead', 'Attack', 'Hold', 'Release', 'Floor')
              }),
          (
           'Sidechain',
           {PARAMETERS_KEY: (
                             'Ext. In On', 'Ext. In Gain', 'Ext. In Mix', 'Side Listen',
                             'EQ On', 'EQ Mode', 'EQ Freq',
                             use('EQ Gain').if_parameter('EQ Mode').has_value('Low Shelf').else_use('EQ Gain').if_parameter('EQ Mode').has_value('High Shelf').else_use('EQ Gain').if_parameter('EQ Mode').has_value('Bell').else_use('EQ Q'))
              }))),
   'GlueCompressor': IndexedDict((
                    (
                     'Compression',
                     {PARAMETERS_KEY: ('Threshold', 'Ratio', 'Attack', 'Release', 'Peak Clip In', 'Range', 'Makeup', 'Dry/Wet')
                        }),
                    (
                     'Sidechain',
                     {PARAMETERS_KEY: (
                                       'Ext. In On', 'Ext. In Gain', 'Ext. In Mix', '',
                                       'EQ On', 'EQ Mode', 'EQ Freq',
                                       use('EQ Gain').if_parameter('EQ Mode').has_value('Low Shelf').else_use('EQ Gain').if_parameter('EQ Mode').has_value('High Shelf').else_use('EQ Gain').if_parameter('EQ Mode').has_value('Bell').else_use('EQ Q'))
                        }))),
   'GrainDelay': IndexedDict((
                (
                 'Pitch',
                 {PARAMETERS_KEY: (
                                   'Frequency', 'Pitch', 'Delay Mode',
                                   use('Time Delay').if_parameter('Delay Mode').has_value('off').else_use('Beat Delay'),
                                   'Random', 'Spray', 'Feedback', 'DryWet')
                    }),
                (
                 'Time',
                 {PARAMETERS_KEY: (
                                   'Delay Mode',
                                   use('Time Delay').if_parameter('Delay Mode').has_value('off').else_use('Beat Delay'),
                                   'Beat Swing', 'Feedback', '', '', '', 'DryWet')
                    }))),
   'Limiter': IndexedDict((
             (
              MAIN_KEY,
              {PARAMETERS_KEY: ('Gain', 'Ceiling', 'Link Channels', 'Lookahead', 'Auto', 'Release time', '', '')
                 }),)),
   'Looper': IndexedDict((
            (
             MAIN_KEY,
             {PARAMETERS_KEY: ('State', 'Speed', 'Reverse', 'Quantization', 'Monitor', 'Song Control', 'Tempo Control',
 'Feedback')
                }),)),
   'MultibandDynamics': IndexedDict((
                       (
                        MAIN_KEY,
                        {PARAMETERS_KEY: ('Above Threshold (Low)', 'Above Ratio (Low)', 'Above Threshold (Mid)', 'Above Ratio (Mid)',
 'Above Threshold (High)', 'Above Ratio (High)', 'Master Output', 'Amount')
                           }),
                       (
                        'Low Band',
                        {PARAMETERS_KEY: ('Band Activator (Low)', 'Input Gain (Low)', 'Below Threshold (Low)', 'Below Ratio (Low)',
 'Above Threshold (Low)', 'Above Ratio (Low)', 'Attack Time (Low)', 'Release Time (Low)')
                           }),
                       (
                        'Mid Band',
                        {PARAMETERS_KEY: ('Band Activator (Mid)', 'Input Gain (Mid)', 'Below Threshold (Mid)', 'Below Ratio (Mid)',
 'Above Threshold (Mid)', 'Above Ratio (Mid)', 'Attack Time (Mid)', 'Release Time (Mid)')
                           }),
                       (
                        'High Band',
                        {PARAMETERS_KEY: ('Band Activator (High)', 'Input Gain (High)', 'Below Threshold (High)', 'Below Ratio (High)',
 'Above Threshold (High)', 'Above Ratio (High)', 'Attack Time (High)', 'Release Time (High)')
                           }),
                       (
                        'Mix & Split',
                        {PARAMETERS_KEY: ('Output Gain (Low)', 'Low-Mid Crossover', 'Output Gain (Mid)', 'Mid-High Crossover',
 'Output Gain (High)', 'Peak/RMS Mode', 'Amount', 'Master Output')
                           }),
                       (
                        'Sidechain',
                        {PARAMETERS_KEY: ('Ext. In On', 'Ext. In Mix', 'Ext. In Gain', '', 'Time Scaling', 'Soft Knee On/Off',
 '', '')
                           }))),
   'Overdrive': IndexedDict((
               (
                MAIN_KEY,
                {PARAMETERS_KEY: ('Filter Freq', 'Filter Width', 'Drive', 'Tone', 'Preserve Dynamics', '', '', 'Dry/Wet')
                   }),)),
   'Phaser': IndexedDict((
            (
             MAIN_KEY,
             {PARAMETERS_KEY: (
                               'Poles', 'Frequency', 'Feedback', 'Env. Modulation',
                               'LFO Amount', 'LFO Sync',
                               use('LFO Frequency').if_parameter('LFO Sync').has_value('Free').else_use('LFO Sync Rate'),
                               'Dry/Wet')
                }),
            (
             'Envelope',
             {PARAMETERS_KEY: ('Poles', 'Type', 'Color', 'Frequency', 'Feedback', 'Env. Modulation', 'Env. Attack',
 'Env. Release')
                }),
            (
             'LFO',
             {PARAMETERS_KEY: (
                               'LFO Amount', 'LFO Waveform', 'LFO Sync',
                               use('LFO Frequency').if_parameter('LFO Sync').has_value('Free').else_use('LFO Sync Rate'),
                               use('LFO Width (Random)').if_parameter('LFO Waveform').has_value('S&H Width').else_use('LFO Stereo Mode').if_parameter('LFO Sync').has_value('Free').else_use('LFO Offset'),
                               use('').if_parameter('LFO Waveform').has_value('S&H Width').else_use('LFO Phase').if_parameter('LFO Sync').has_value('Sync').else_use('LFO Phase').if_parameter('LFO Stereo Mode').has_value('Phase').else_use('LFO Spin'),
                               '', '')
                }))),
   'PingPongDelay': IndexedDict((
                   (
                    MAIN_KEY,
                    {PARAMETERS_KEY: (
                                      'Delay Mode',
                                      use('Beat Delay').if_parameter('Delay Mode').has_value('Sync').else_use('Time Delay'),
                                      use('Beat Swing').if_parameter('Delay Mode').has_value('Sync').else_use(''),
                                      'Freeze', 'Filter Freq', 'Filter Width', 'Feedback', 'Dry/Wet')
                       }),)),
   'Redux': IndexedDict((
           (
            MAIN_KEY,
            {PARAMETERS_KEY: (
                              'Bit On', 'Bit Depth', 'Sample Mode',
                              use('Sample Hard').if_parameter('Sample Mode').has_value('Hard').else_use('Sample Soft'),
                              '', '', '', '')
               }),)),
   'Resonator': IndexedDict((
               (
                MAIN_KEY,
                {PARAMETERS_KEY: ('Frequency', 'Decay', 'Color', 'I Gain', 'II Gain', 'III Gain', 'Width', 'Dry/Wet')
                   }),
               (
                'Global',
                {PARAMETERS_KEY: ('Mode', 'Decay', 'Const', 'Color', '', 'Width', 'Global Gain', 'Dry/Wet')
                   }),
               (
                'Filter',
                {PARAMETERS_KEY: ('Filter On', 'Frequency', 'Filter Type', '', '', '', '', '')
                   }),
               (
                'Mode I & II',
                {PARAMETERS_KEY: ('I On', 'I Note', 'I Tune', 'I Gain', 'II On', 'II Pitch', 'II Tune', 'II Gain')
                   }),
               (
                'Mode III & IV',
                {PARAMETERS_KEY: ('III On', 'III Pitch', 'III Tune', 'III Gain', 'IV On', 'IV Pitch', 'IV Tune', 'IV Gain')
                   }),
               (
                'Mode V',
                {PARAMETERS_KEY: ('V On', 'V Pitch', 'V Tune', 'V Gain', '', '', '', '')
                   }),
               (
                'Mix',
                {PARAMETERS_KEY: ('I Gain', 'II Gain', 'III Gain', 'IV Gain', 'V Gain', '', '', '')
                   }),
               (
                'Pitch',
                {PARAMETERS_KEY: ('I Note', 'II Pitch', 'III Pitch', 'IV Pitch', 'V Pitch', '', '', '')
                   }))),
   'Reverb': IndexedDict((
            (
             MAIN_KEY,
             {PARAMETERS_KEY: (
                               'PreDelay',
                               use('In Filter Freq').if_parameter('In LowCut On').has_value('on').else_use('ER Shape').if_parameter('In HighCut On').has_value('off').else_use('In Filter Freq'),
                               use('Chorus Amount').if_parameter('Chorus On').has_value('on').else_use('ER Level'),
                               'Stereo Image', 'Room Size', 'DecayTime',
                               use('HiShelf Gain').if_parameter('HiShelf On').has_value('on').else_use('Diffuse Level'),
                               'Dry/Wet')
                }),
            (
             'Global',
             {PARAMETERS_KEY: ('Chorus On', 'Chorus Rate', 'Chorus Amount', 'Quality', 'Freeze On', 'Flat On', 'ER Level',
 'Diffuse Level')
                }),
            (
             'Diffusion Network',
             {PARAMETERS_KEY: ('HiShelf On', 'HiShelf Freq', 'HiShelf Gain', 'LowShelf On', 'LowShelf Freq', 'LowShelf Gain',
 'Density', 'Scale')
                }),
            (
             'Input/Reflections',
             {PARAMETERS_KEY: ('In LowCut On', 'In HighCut On', 'In Filter Freq', 'In Filter Width', 'ER Spin On',
 'ER Spin Rate', 'ER Spin Amount', 'ER Shape')
                }))),
   'Saturator': IndexedDict((
               (
                MAIN_KEY,
                {PARAMETERS_KEY: ('Drive', 'Type', 'Color', 'Base', 'Frequency', 'Width', 'Depth', 'Output')
                   }),
               (
                'Waveshaper',
                {PARAMETERS_KEY: (
                                  'Type',
                                  use('WS Drive').if_parameter('Type').has_value('Waveshaper'),
                                  use('WS Curve').if_parameter('Type').has_value('Waveshaper'),
                                  use('WS Depth').if_parameter('Type').has_value('Waveshaper'),
                                  use('WS Lin').if_parameter('Type').has_value('Waveshaper'),
                                  use('WS Damp').if_parameter('Type').has_value('Waveshaper'),
                                  use('WS Period').if_parameter('Type').has_value('Waveshaper'),
                                  'Dry/Wet')
                   }),
               (
                'Output',
                {PARAMETERS_KEY: ('', '', '', '', '', 'Soft Clip', 'Output', 'Dry/Wet')
                   }))),
   'CrossDelay': IndexedDict((
                (
                 MAIN_KEY,
                 {PARAMETERS_KEY: (
                                   'L Delay Mode',
                                   use('L Beat Delay').if_parameter('L Delay Mode').has_value('on').else_use('L Time Delay'),
                                   use('L Beat Swing').if_parameter('L Delay Mode').has_value('on'),
                                   'R Delay Mode',
                                   use('R Beat Delay').if_parameter('R Delay Mode').has_value('on').else_use('R Time Delay'),
                                   use('R Beat Swing').if_parameter('R Delay Mode').has_value('on').else_use(''),
                                   'Feedback', 'Dry/Wet')
                    }),
                (
                 'Global',
                 {PARAMETERS_KEY: ('', '', '', '', '', 'Link On', 'Feedback', 'Dry/Wet')
                    }))),
   'StereoGain': IndexedDict((
                (
                 MAIN_KEY,
                 {PARAMETERS_KEY: ('Mute', 'BlockDc', 'PhaseInvertL', 'PhaseInvertR', 'Signal Source', 'Panorama', 'StereoSeparation',
 'Gain')
                    }),)),
   'Vinyl': IndexedDict((
           (
            'Global',
            {PARAMETERS_KEY: ('Tracing On', 'Tracing Drive', 'Tracing Freq.', 'Tracing Width', 'Pinch On', 'Global Drive',
 'Crackle Density', 'Crackle Volume')
               }),
           (
            'Pinch',
            {PARAMETERS_KEY: ('Pinch On', 'Pinch Soft On', 'Pinch Mono On', 'Pinch Width', 'Pinch Drive', 'Pinch Freq.',
 'Crackle Density', 'Crackle Volume')
               }))),
   'Vocoder': IndexedDict((
             (
              MAIN_KEY,
              {PARAMETERS_KEY: ('Formant Shift', 'Attack Time', 'Release Time', 'Unvoiced Level', 'Gate Threshold',
 'Filter Bandwidth', 'Envelope Depth', 'Dry/Wet')
                 }),
             (
              'Carrier',
              {PARAMETERS_KEY: ('Noise Rate', 'Noise Crackle', 'Lower Pitch Detection', 'Upper Pitch Detection', 'Oscillator Pitch',
 'Oscillator Waveform', 'Enhance', '')
                 }),
             (
              'Global',
              {PARAMETERS_KEY: ('Formant Shift', 'Attack Time', 'Release Time', 'Mono/Stereo', 'Output Level', 'Gate Threshold',
 'Envelope Depth', 'Dry/Wet')
                 }),
             (
              'Filters/Voicing',
              {PARAMETERS_KEY: ('Filter Bandwidth', 'Upper Filter Band', 'Lower Filter Band', 'Precise/Retro', 'Unvoiced Level',
 'Unvoiced Sensitivity', 'Unvoiced Speed', 'Enhance')
                 })))
   }
PARAMETERS_BLACKLIST_FOR_CPP_SANITY_CHECK = {'OriginalSimpler': ('Start', 'End', 'Sensitivity', 'Mode', 'Playback', 'Pad Slicing', 'Multi Sample',
 'Zoom', 'Env. Type', 'Warp', 'Warp Mode', 'Voices', 'Preserve', 'Loop Mode', 'Envelope',
 'Grain Size Tones', 'Grain Size Texture', 'Flux', 'Formants', 'Envelope Complex Pro',
 'Gain'),
   'Operator': ('Oscillator', ),
   'Eq8': ('Band', )
   }