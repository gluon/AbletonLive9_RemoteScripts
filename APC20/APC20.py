#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/APC20/APC20.py
from __future__ import with_statement
from functools import partial
from itertools import izip
import Live
MapMode = Live.MidiMap.MapMode
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import MIDI_CC_TYPE
from _Framework.TransportComponent import TransportComponent
from _APC.APC import APC
from _APC.ControlElementUtils import make_button, make_pedal_button, make_slider
from _APC.SessionComponent import SessionComponent
from _APC.MixerComponent import MixerComponent
from _APC.SkinDefault import make_biled_skin
from ShiftableSelectorComponent import ShiftableSelectorComponent
from ShiftableZoomingComponent import ShiftableZoomingComponent
from SliderModesComponent import SliderModesComponent
from BackgroundComponent import BackgroundComponent
SESSION_WIDTH = 8
SESSION_HEIGHT = 5
MIXER_SIZE = 8

class APC20(APC):
    """ Script for Akai's APC20 Controller """

    def __init__(self, *a, **k):
        super(APC20, self).__init__(*a, **k)
        self._skin = make_biled_skin()
        with self.component_guard():
            self._create_controls()
            self._create_session()
            self._create_mixer()
            self._create_transport()
            self._create_background()
            self._create_global_control()
            self._session.set_mixer(self._mixer)
            self.set_highlighting_session_component(self._session)
            for component in self.components:
                component.set_enabled(False)

    def _activate_combination_mode(self, track_offset, support_devices):
        super(APC20, self)._activate_combination_mode(track_offset, support_devices)
        if support_devices:
            self._shift_modes.invert_assignment()

    def _create_controls(self):
        make_color_button = partial(make_button, skin=self._skin)
        self._shift_button = make_button(0, 81, name='Shift_Button')
        self._matrix = ButtonMatrixElement(name='Button_Matrix')
        self._scene_launch_buttons = [ make_color_button(0, index + 82, name='Scene_%d_Launch_Button' % index) for index in xrange(SESSION_HEIGHT) ]
        self._track_stop_buttons = [ make_color_button(index, 52, name='Track_%d_Stop_Button' % index) for index in xrange(SESSION_WIDTH) ]
        for scene_index in xrange(SESSION_HEIGHT):
            row = [ make_color_button(track_index, scene_index + 53, name='%d_Clip_%d_Button' % (track_index, scene_index)) for track_index in xrange(SESSION_WIDTH) ]
            self._matrix.add_row(row)

        self._selected_scene_launch_button = make_pedal_button(64, name='Selected_Scene_Launch_Button')
        self._scene_launch_buttons = ButtonMatrixElement(name='Scene_Launch_Buttons', rows=[self._scene_launch_buttons])
        self._solo_buttons = [ make_button(track_index, 49, name='%d_Solo_Button' % track_index) for track_index in xrange(MIXER_SIZE) ]
        self._mute_buttons = [ make_button(track_index, 50, name='%d_Mute_Button' % track_index) for track_index in xrange(MIXER_SIZE) ]
        self._master_volume_control = make_slider(0, 14, name='Master_Volume_Control')
        self._prehear_control = EncoderElement(MIDI_CC_TYPE, 0, 47, MapMode.relative_two_compliment, name='Prehear_Volume_Control')
        self._master_select_button = make_button(0, 80, name='Master_Select_Button')
        self._select_buttons = [ make_button(track_index, 51, name='%d_Select_Button' % track_index) for track_index in xrange(8) ]
        self._arm_buttons = [ make_button(track_index, 48, name='%d_Arm_Button' % track_index) for track_index in xrange(8) ]
        self._sliders = [ make_slider(track_index, 7, name='%d_Volume_Control' % track_index) for track_index in xrange(8) ]
        self._note_matrix = ButtonMatrixElement(name='Note_Button_Matrix')
        self._note_buttons = [ [ make_button(9, note + i, name='Note_%d_Button' % (note + i)) for i in xrange(4) ] for note in xrange(36, 75, 4) ]
        for row in self._note_buttons:
            for button in row:
                button.send_depends_on_forwarding = False

            self._note_matrix.add_row(row)

    def _create_session(self):
        self._session = SessionComponent(SESSION_WIDTH, SESSION_HEIGHT, name='Session_Control', auto_name=True, enable_skinning=True)
        self._session.set_clip_launch_buttons(self._matrix)
        self._session.set_stop_track_clip_buttons(tuple(self._track_stop_buttons))
        self._session.set_scene_launch_buttons(self._scene_launch_buttons)
        for scene_index in xrange(SESSION_HEIGHT):
            scene = self._session.scene(scene_index)
            for track_index in xrange(SESSION_WIDTH):
                clip_slot = scene.clip_slot(track_index)
                clip_slot.name = '%d_Clip_Slot_%d' % (track_index, scene_index)

        self._session.selected_scene().set_launch_button(self._selected_scene_launch_button)
        self._session_zoom = ShiftableZoomingComponent(self._session, tuple(self._track_stop_buttons), name='Session_Overview', enable_skinning=True)
        self._session_zoom.set_button_matrix(self._matrix)
        self._session_zoom.set_zoom_button(self._shift_button)
        self._session_zoom.set_scene_bank_buttons(self._scene_launch_buttons)

    def _create_mixer(self):
        self._mixer = MixerComponent(MIXER_SIZE, name='Mixer')
        self._mixer.master_strip().name = 'Master_Channel_Strip'
        self._mixer.selected_strip().name = 'Selected_Channel_Strip'
        buttons = izip(self._solo_buttons, self._mute_buttons)
        for track_index, (solo_button, mute_button) in enumerate(buttons):
            strip = self._mixer.channel_strip(track_index)
            strip.name = 'Channel_Strip_%d' % track_index
            strip.set_solo_button(solo_button)
            strip.set_mute_button(mute_button)
            strip.set_shift_button(self._shift_button)
            strip.set_invert_mute_feedback(True)

        self._mixer.set_prehear_volume_control(self._prehear_control)
        self._mixer.master_strip().set_volume_control(self._master_volume_control)

    def _create_transport(self):
        self._transport = TransportComponent(name='Transport')

    def _create_background(self):
        self._background = BackgroundComponent(name='Background')

    def _create_global_control(self):
        self._slider_modes = SliderModesComponent(self._mixer, tuple(self._sliders), name='Slider_Modes')
        self._shift_modes = ShiftableSelectorComponent(tuple(self._select_buttons), self._master_select_button, tuple(self._arm_buttons), self._matrix, self._session, self._session_zoom, self._mixer, self._transport, self._slider_modes, self._send_introduction_message, self._note_matrix, self._background, name='Shift_Modes')
        self._shift_modes.set_mode_toggle(self._shift_button)

    def _product_model_id_byte(self):
        return 123