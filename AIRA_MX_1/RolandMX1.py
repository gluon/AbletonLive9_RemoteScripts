#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/AIRA_MX_1/RolandMX1.py
from __future__ import with_statement
from functools import partial
from _Framework.Util import recursive_map
from _Framework.ControlSurface import OptimizedControlSurface
from _Framework.TransportComponent import TransportComponent
from _Framework.ModesComponent import ModesComponent, AddLayerMode
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.Layer import Layer
from _Framework.Util import const
from _Framework.Dependency import inject
from .ControlElementUtils import make_button, make_encoder, with_modifier
from .NotifyingMixerComponent import NotifyingMixerComponent
from .NotifyingSessionComponent import NotifyingSessionComponent
from .SkinDefault import make_default_skin
NUM_TRACKS = 11
NUM_SCENES = 11

class RolandMX1(OptimizedControlSurface):

    def __init__(self, *a, **k):
        super(RolandMX1, self).__init__(*a, **k)
        with self.component_guard():
            self._skin = make_default_skin()
            with inject(skin=const(self._skin)).everywhere():
                self._create_controls()
            self._transport = self._create_transport()
            self._mixer = self._create_mixer()
            self._session = self._create_session()
            self._step_button_modes = self._create_step_button_modes()

    def _create_controls(self):
        self._aux_button = make_button('Aux_Button', 32, is_modifier=True)
        self._cursor_up_button = make_button('Cursor_Up_Button', 12)
        self._cursor_down_button = make_button('Cursor_Down_Button', 13)
        self._modified_cursor_up_button = with_modifier(self._cursor_up_button, self._aux_button)
        self._modified_cursor_down_button = with_modifier(self._cursor_down_button, self._aux_button)
        self._start_stop_button = make_button('Start_Stop_Button', 16)
        self._modified_start_stop_button = with_modifier(self._start_stop_button, self._aux_button)
        self._recall_button = make_button('Recall_Button', 17)
        self._store_button = make_button('Store_Button', 18)
        self._tone_filter_knobs = ButtonMatrixElement(rows=[[ make_encoder('Tone_Filter_Encoder_%d' % (col,), identifier) for col, identifier in enumerate(xrange(102, 113)) ]], name='Tone_Filter_Knobs')
        step_buttons_raw = [[ make_button('Step_Button_%d' % (col,), identifier) for col, identifier in enumerate(xrange(20, 31)) ]]
        self._step_buttons = ButtonMatrixElement(rows=step_buttons_raw, name='Step_Buttons')
        self._modified_step_buttons = ButtonMatrixElement(rows=recursive_map(partial(with_modifier, modifier=self._aux_button), step_buttons_raw), name='Step_Buttons_With_Modifier')
        self._select_buttons = ButtonMatrixElement(rows=[[ make_button('Select_Button_%d' % (col,), identifier) for col, identifier in enumerate(xrange(60, 71)) ]], name='Select_Buttons')
        self._bfx_buttons = ButtonMatrixElement(rows=[[ make_button('BFX_Button_%d' % (col,), identifier) for col, identifier in enumerate(xrange(80, 91)) ]], name='BFX_Buttons')
        self._mfx_buttons = ButtonMatrixElement(rows=[[ make_button('MFX_Button_%d' % (col,), identifier) for col, identifier in enumerate(xrange(100, 111)) ]], name='MFX_Buttons')

    def _create_transport(self):
        transport = TransportComponent(play_toggle_model_transform=lambda v: v)
        transport.layer = Layer(record_button=self._modified_start_stop_button, play_button=self._start_stop_button)
        return transport

    def _create_mixer(self):
        mixer = NotifyingMixerComponent(NUM_TRACKS, auto_name=True)
        mixer.layer = Layer(send_controls=self._tone_filter_knobs, track_select_buttons=self._select_buttons, arm_buttons=self._bfx_buttons, solo_buttons=self._mfx_buttons, send_index_up_button=self._modified_cursor_up_button, send_index_down_button=self._modified_cursor_down_button, modifier_button=self._aux_button)
        return mixer

    def _create_session(self):
        session = NotifyingSessionComponent(NUM_TRACKS, NUM_SCENES, enable_skinning=True, auto_name=True)
        session.layer = Layer(scene_bank_down_button=self._cursor_up_button, scene_bank_up_button=self._cursor_down_button)
        return session

    def _create_step_button_modes(self):
        matrix_modes = ModesComponent(name='Step_Button_Modes')
        clip_mode = AddLayerMode(self._session, Layer(clip_launch_buttons=self._step_buttons, stop_track_clip_buttons=self._modified_step_buttons))
        scene_mode = AddLayerMode(self._session, Layer(scene_launch_buttons=self._step_buttons))
        matrix_modes.add_mode('clip', clip_mode)
        matrix_modes.add_mode('scene', scene_mode)
        matrix_modes.layer = Layer(clip_button=self._recall_button, scene_button=self._store_button)
        matrix_modes.selected_mode = 'clip'
        return matrix_modes