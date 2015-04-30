#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\Maschine.py
from __future__ import with_statement
import Live
import MidiRemoteScript
import time
from functools import partial
from _Framework.Task import Task
from _Framework.SubjectSlot import subject_slot
from PadScale import *
from MIDI_Map import *
from MaschineSessionComponent import MaschineSessionComponent
from MaschineDeviceComponent import MaschineDeviceComponent
from MaschineTransport import MaschineTransport
from ModeSelector import ModeSelector
from StateButton import StateButton, ToggleButton
from NoteRepeatComponent import NoteRepeatComponent
from MaschineMixerComponent import MaschineMixerComponent
from EditSection import EditSection
from AudioClipEditComponent import AudioClipEditComponent
from MidiEditSection import MidiEditSection
from _Framework.ControlSurface import ControlSurface, _scheduled_method
from _Framework.InputControlElement import *
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement, ON_VALUE, OFF_VALUE
from _Framework.EncoderElement import EncoderElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.ChannelTranslationSelector import ChannelTranslationSelector
from _Framework.TransportComponent import TransportComponent
from _Framework.DeviceComponent import DeviceComponent
from _Framework.ToggleComponent import ToggleComponent
LOOP_KNOB_DIVISION = (4.0, 1.0, 0.5)

class DisplayTask(object):

    def __init__(self):
        self._wait = 0
        self._grid = 0
        self._func = None
        self._hold = False

    def set_func(self, func, grid):
        self._func = func
        self._grid = grid

    def hold(self):
        self._hold = True

    def release(self):
        self._hold = False

    def start(self):
        self._wait = 80

    def tick(self):
        if not self._hold and self._wait > 0:
            self._wait -= 1
            if self._wait == 0 and self._func != None:
                self._func(self._grid)


class Maschine(ControlSurface):
    __module__ = __name__
    __doc__ = 'Basic Control Script for All Maschine Modell Mikro, Mikro Mk2, Mk1, Mk2, Studio'

    def __init__(self, c_instance):
        super(Maschine, self).__init__(c_instance)
        with self.component_guard():
            register_sender(self)
            self._diplay_cache = ['',
             '',
             '',
             '']
            self._suppress_send_midi = True
            is_momentary = True
            self._c_ref = c_instance
            self.display_task = DisplayTask()
            self._challenge = Live.Application.get_random_int(0, 400000000) & 2139062143
            self._active = False
            self._midi_pause_count = 0
            self.blink_state = 0
            self.send_slider_index = 0
            self.nav_index = 0
            self.arm_selected_track = False
            self.undo_state = 0
            self.redo_state = 0
            self._set_suppress_rebuild_requests(True)
            self._modeselect = ModeSelector(self.is_monochrome())
            self._device = self._set_up_device_control()
            self._set_up_session(self._modeselect)
            self._set_up_mixer()
            self._setup_transport()
            self._set_global_buttons()
            self._editsection = EditSection()
            self._editsection.connect_session(self._session)
            self._editsection.set_mode_selector(self._modeselect)
            self._session.set_mode(self._modeselect._clip_mode)
            self._audio_clip_editor = AudioClipEditComponent()
            self._note_repeater = NoteRepeatComponent(c_instance.note_repeat)
            self._midi_edit = MidiEditSection()
            self._init_settings()
            self._init_maschine()
            self.set_highlighting_session_component(self._session)
            self.set_pad_translations(PAD_TRANSLATIONS)
            self._on_selected_track_changed()
            self.set_up_function_buttons()
            self.show_message(str(''))
            self.request_rebuild_midi_map()
            self._set_suppress_rebuild_requests(False)
            self._active = True
            self._display_device_param = False
            self.set_feedback_channels(FEEDBACK_CHANNELS)
            self._final_init()
            self._suppress_send_midi = False
            self.apply_preferences()
            self.init_text_display()
            self._on_appointed_device_changed.subject = self.song()

    def _init_maschine(self):
        pass

    def _final_init(self):
        pass

    def create_pad_button(self, scene_index, track_index, color_source):
        pass

    def create_gated_button(self, identifier, hue):
        pass

    def apply_preferences(self):
        pref_dict = self._pref_dict
        if 'step_advance' in pref_dict:
            self._session.set_step_advance(pref_dict['step_advance'])
        if 'solo_exclusive' in pref_dict:
            self._modeselect.set_solo_exclusive(pref_dict['solo_exclusive'])
        else:
            self._modeselect.set_solo_exclusive(True)
        if 'arm_exclusive' in pref_dict:
            self._modeselect.set_arm_exclusive(pref_dict['arm_exclusive'])
        else:
            self._modeselect.set_arm_exclusive(True)
        if 'quantize_val' in pref_dict:
            self._editsection.quantize = pref_dict['quantize_val']
        else:
            self._editsection.quantize = 5
        if 'initial_cliplen' in pref_dict:
            self._editsection.initial_clip_len = pref_dict['initial_cliplen']
        else:
            self._editsection.initial_clip_len = 4.0
        if 'auto_arm_sel_track' in pref_dict:
            self.arm_selected_track = pref_dict['auto_arm_sel_track']
        else:
            self.arm_selected_track = False
        if 'note_color_mode' in pref_dict:
            self._modeselect._pad_mode._note_display_mode = pref_dict['note_color_mode']
        else:
            self._modeselect._pad_mode._note_display_mode = ND_KEYBOARD1
        self._pref_dict['note_color_mode'] = self._modeselect._pad_mode._note_display_mode
        self.set_sel_arm_button.send_value(self.arm_selected_track and 127 or 0, True)
        self._note_repeater.recall_values(self._pref_dict)

    def store_preferences(self):
        self._pref_dict['step_advance'] = self._session.get_step_advance()
        self._pref_dict['solo_exclusive'] = self._modeselect.is_solo_exclusive()
        self._pref_dict['arm_exclusive'] = self._modeselect.is_arm_exclusive()
        self._pref_dict['quantize_val'] = self._editsection.quantize
        self._pref_dict['initial_cliplen'] = self._editsection.initial_clip_len
        self._pref_dict['auto_arm_sel_track'] = self.arm_selected_track
        self._pref_dict['note_color_mode'] = self._modeselect._pad_mode._note_display_mode
        self._note_repeater.store_values(self._pref_dict)

    def _init_settings(self):
        from pickle import loads, dumps
        from encodings import ascii
        nop(ascii)
        preferences = self._c_instance.preferences(self.preferences_name())
        self._pref_dict = {}
        try:
            self._pref_dict = loads(str(preferences))
        except Exception:
            pass

        pref_dict = self._pref_dict
        preferences.set_serializer(lambda : dumps(pref_dict))

    def preferences_name(self):
        return 'Maschine'

    def _pre_serialize(self):
        from pickle import dumps
        from encodings import ascii
        nop(ascii)
        preferences = self._c_instance.preferences('Maschine')
        self.store_preferences()
        dump = dumps(self._pref_dict)
        preferences.set_serializer(lambda : dump)

    def toggle_nav_mode(self):
        self._session.switch_step_advance()
        self.show_message(' View Navigation in steps of ' + str(self._session.get_step_advance()))

    def _set_up_session(self, mode_selector):
        is_momentary = True
        self._session = MaschineSessionComponent()
        self._session.set_color_manager(mode_selector.get_color_manager())
        self.nav_buttons = (self.create_gated_button(92, COLOR_HUE_NAV),
         self.create_gated_button(81, COLOR_HUE_NAV),
         self.create_gated_button(93, COLOR_HUE_NAV),
         self.create_gated_button(91, COLOR_HUE_NAV))
        self._session.set_scene_bank_buttons(self.nav_buttons[0], self.nav_buttons[1])
        self._session.set_track_bank_buttons(self.nav_buttons[2], self.nav_buttons[3])
        track_stop_buttons = [ StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, index + STOP_CC_OFF) for index in range(4) ]
        self._session.set_stop_track_clip_buttons(tuple(track_stop_buttons))
        self._matrix = []
        self._bmatrix = ButtonMatrixElement()
        for scene_index in range(4):
            button_row = []
            for track_index in range(4):
                button = self.create_pad_button(scene_index, track_index, mode_selector)
                button_row.append(button)

            self._matrix.append(tuple(button_row))
            self._bmatrix.add_row(tuple(button_row))

        self._session.set_matrix(self._matrix)
        for button, (track_index, scene_index) in self._bmatrix.iterbuttons():
            if button:
                scene = self._session.scene(scene_index)
                clip_slot = scene.clip_slot(track_index)
                clip_slot.set_launch_button(button)
                clip_slot.set_triggered_to_play_value(1)
                clip_slot.set_triggered_to_record_value(1)
                clip_slot.set_started_value(1)
                clip_slot.set_recording_value(1)
                clip_slot.set_stopped_value(1)

        self._session._link()

    def _set_up_mixer(self):
        is_momentary = True
        self._mixer = MaschineMixerComponent(8)
        self.send_sliders = []
        for track in range(8):
            self.send_sliders.append(SliderElement(MIDI_CC_TYPE, BASIC_CHANNEL, SEND_CC_OFF + track))

        for track in range(8):
            strip = self._mixer.channel_strip(track)
            strip.set_arm_button(StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, ARM_CC_OFF + track))
            strip.set_solo_button(StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, SOLO_CC_OFF + track))
            strip.set_mute_button(StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, MUTE_CC_OFF + track))
            strip.set_volume_control(SliderElement(MIDI_CC_TYPE, BASIC_CHANNEL, LEVEL_CC_OFF + track))
            strip.set_pan_control(SliderElement(MIDI_CC_TYPE, BASIC_CHANNEL, PAN_CC_OFF + track))
            strip.set_select_button(StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, SELECT_CC_OFF + track))
            st = tuple([self.send_sliders[track]])
            strip.set_send_controls(st)

        self.send_slider_toggle_button = StateButton(False, MIDI_CC_TYPE, 0, 90)
        self._do_toggle_send.subject = self.send_slider_toggle_button
        self._session.set_mixer(self._mixer)

    def _set_global_buttons(self):
        is_momentary = True
        self._undo_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 85)
        self._do_undo.subject = self._undo_button
        self._redo_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 87)
        self._do_redo.subject = self._redo_button
        self._stop_all_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 111)
        self._do_stop_all.subject = self._stop_all_button
        self._toggle_detail_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 1, 121)
        self._action_toogle_detail_view.subject = self._toggle_detail_button
        self._fire_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 9)
        self._do_fire_button.subject = self._fire_button
        self._g_clear_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 1, 106)
        self._hold_clear_action.subject = self._g_clear_button
        self._g_duplicate_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 1, 107)
        self._hold_duplicate_action.subject = self._g_duplicate_button
        self.track_left_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 120)
        self.track_right_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 121)
        self.set_sel_arm_button = StateButton(is_momentary, MIDI_CC_TYPE, 2, 56)
        self._reenable_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 1, 120)
        self._do_auto_reenable.subject = self._reenable_button
        self._on_change_reenabled.subject = self.song()
        self._on_change_reenabled()
        self._a_trk_left.subject = self.track_left_button
        self._a_trk_right.subject = self.track_right_button
        self._a_sel_arm.subject = self.set_sel_arm_button

    def _set_up_device_control(self):
        is_momentary = True
        device = MaschineDeviceComponent()
        param_controls = []
        for index in range(8):
            param_controls.append(SliderElement(MIDI_CC_TYPE, BASIC_CHANNEL, DEVICE_CC_OFF + index))

        device.set_parameter_controls(tuple(param_controls))
        self.device_control = param_controls
        device.set_on_off_button(StateButton(is_momentary, MIDI_CC_TYPE, BASIC_CHANNEL, DEVICE_BUTTON_CC_OFF))
        device.set_bank_nav_buttons(StateButton(is_momentary, MIDI_CC_TYPE, 3, 104), ButtonElement(is_momentary, MIDI_CC_TYPE, 3, 105))
        self._device_nav_button_left = StateButton(is_momentary, MIDI_CC_TYPE, 3, 106)
        self._device_nav_button_right = StateButton(is_momentary, MIDI_CC_TYPE, 3, 107)
        self._navigate_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 127)
        self._nav_value_left.subject = self._device_nav_button_left
        self._nav_value_right.subject = self._device_nav_button_right
        self._do_focus_navigate.subject = self._navigate_button
        self.set_device_component(device)
        return device

    def _setup_transport(self):
        is_momentary = True
        transport = TransportComponent()
        studiotransport = MaschineTransport()
        playButton = StateButton(is_momentary, MIDI_CC_TYPE, 0, 108)
        stopButton = StateButton(not is_momentary, MIDI_CC_TYPE, 0, 110)
        recordButton = StateButton(is_momentary, MIDI_CC_TYPE, 0, 109)
        overdubButton = StateButton(is_momentary, MIDI_CC_TYPE, 0, 107)
        metrononmeButton = StateButton(is_momentary, MIDI_CC_TYPE, 0, 104)
        eventRecButton = StateButton(is_momentary, MIDI_CC_TYPE, 0, 98)
        playButton.name = 'Play'
        stopButton.name = 'Stop'
        recordButton.name = 'Record'
        overdubButton.name = 'Overdub'
        metrononmeButton.name = 'Metronome'
        transport.set_play_button(playButton)
        transport.set_stop_button(stopButton)
        transport.set_record_button(recordButton)
        transport.set_overdub_button(overdubButton)
        transport.set_metronome_button(metrononmeButton)
        studiotransport.set_session_auto_button(eventRecButton)
        studiotransport.set_arrangement_overdub_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 106))
        studiotransport.set_back_arrange_button(StateButton(is_momentary, MIDI_CC_TYPE, 0, 105))
        transport.set_nudge_buttons(StateButton(is_momentary, MIDI_CC_TYPE, 1, 51), StateButton(is_momentary, MIDI_CC_TYPE, 1, 50))
        punchinbutton = ToggleButton(MIDI_CC_TYPE, 1, 52)
        punchoutbutton = ToggleButton(MIDI_CC_TYPE, 1, 53)
        punchinbutton.name = 'Punch In'
        punchoutbutton.name = 'Punch Out'
        transport.set_punch_buttons(punchinbutton, punchoutbutton)
        transport.set_loop_button(StateButton(is_momentary, MIDI_CC_TYPE, 1, 54))
        self.song_follow_button = ButtonElement(True, MIDI_CC_TYPE, 2, 98)
        self._do_song_follow.subject = self.song_follow_button
        self._song_follow_changed.subject = self.song().view
        self._song_follow_changed()
        self.prehear_knob = SliderElement(MIDI_CC_TYPE, 0, 41)
        self.prehear_knob.connect_to(self.song().master_track.mixer_device.cue_volume)
        self.transp_ff_button = ButtonElement(True, MIDI_CC_TYPE, 1, 59)
        self.transp_rw_button = ButtonElement(True, MIDI_CC_TYPE, 1, 58)
        transport.set_seek_buttons(self.transp_ff_button, self.transp_rw_button)
        self.xfadeKnob = SliderElement(MIDI_CC_TYPE, 1, 105)
        self.xfadeKnob.connect_to(self.song().master_track.mixer_device.crossfader)
        self.master_knob = SliderElement(MIDI_CC_TYPE, 0, 99)
        self.master_knob.connect_to(self.song().master_track.mixer_device.volume)
        self.tap_button = StateButton(is_momentary, MIDI_CC_TYPE, 0, 88)
        self._do_tap_tempo.subject = self.tap_button
        self.cue_add_delete_button = StateButton(is_momentary, MIDI_CC_TYPE, 1, 55)
        self.cue_prev_button = StateButton(is_momentary, MIDI_CC_TYPE, 1, 56)
        self.cue_next_button = StateButton(is_momentary, MIDI_CC_TYPE, 1, 57)
        self._do_toggle_cue.subject = self.cue_add_delete_button
        self._do_toggle_prev_cue.subject = self.cue_prev_button
        self._do_toggle_next_cue.subject = self.cue_next_button

    def set_up_function_buttons(self):
        is_momentary = True
        self.keycolor_mod_button = StateButton(is_momentary, MIDI_CC_TYPE, 1, 73)
        self._do_key_color.subject = self.keycolor_mod_button
        self._update_button = ButtonElement(is_momentary, MIDI_CC_TYPE, 0, 86)
        self._do_update_display.subject = self._update_button

    @subject_slot('appointed_device')
    def _on_appointed_device_changed(self):
        self._modeselect._device_changed()

    def _update_hardware(self):
        self._session.update()
        self._modeselect.refresh()
        self.update_undo_redo(True)

    def refresh_state(self):
        ControlSurface.refresh_state(self)
        self._update_hardware()

    def _send_midi(self, midi_bytes, **keys):
        self._c_ref.send_midi(midi_bytes)
        return True

    def init_text_display(self):
        if USE_DISPLAY:
            self._modeselect._pad_mode.update_text_display()

    def _on_selected_track_changed(self):
        super(Maschine, self)._on_selected_track_changed()
        self.set_controlled_track(self.song().view.selected_track)
        self._on_devices_changed.subject = self.song().view.selected_track

    @subject_slot('devices')
    def _on_devices_changed(self):
        pass

    def update(self):
        self.set_feedback_channels(FEEDBACK_CHANNELS)
        super(Maschine, self).update()

    def is_monochrome(self):
        return False

    def _deassign_matrix(self):
        for scene_index in range(4):
            scene = self._session.scene(scene_index)
            for track_index in range(4):
                clip_slot = scene.clip_slot(track_index)
                clip_slot.set_launch_button(None)

    def update_display(self):
        with self.component_guard():
            with self._is_sending_scheduled_messages():
                self._task_group.update(0.1)
            self._modeselect.notify(self.blink_state)
            self.blink_state = (self.blink_state + 1) % 4
            self.display_task.tick()
            self.update_undo_redo(False)

    def update_undo_redo(self, force = False):
        if force:
            self.undo_state = self.song().can_undo
            self.redo_state = self.song().can_redo
        if self.song().can_undo != self.undo_state:
            self.undo_state = self.song().can_undo
            self._undo_button.send_value(self.undo_state == 1 and 127 or 0)
        if self.song().can_redo != self.redo_state:
            self.redo_state = self.song().can_redo
            self._redo_button.send_value(self.redo_state == 1 and 127 or 0)

    def adjust_loop_start(self, delta):
        loopval = self.song().loop_start
        self.song().loop_start = min(self.song().song_length, max(0, loopval + delta))

    def adjust_loop_length(self, delta):
        loopval = self.song().loop_length
        self.song().loop_length = min(self.song().song_length, max(abs(delta), loopval + delta))

    def _do_armsolo_mode(self, value):
        pass

    @subject_slot('value')
    def _do_fire_button(self, value):
        raise self._fire_button != None or AssertionError
        raise value in range(128) or AssertionError
        if value != 0:
            if self.isShiftDown():
                self.song().tap_tempo()
            else:
                clip_slot = self.song().view.highlighted_clip_slot
                if clip_slot:
                    clip_slot.fire()

    @subject_slot('value')
    def _do_undo(self, value):
        if value != 0:
            if self.use_layered_buttons() and self.isShiftDown():
                if self.song().can_redo == 1:
                    self.song().redo()
                    self.show_message(str('REDO'))
            elif self.song().can_undo == 1:
                self.song().undo()
                self.show_message(str('UNDO'))

    @subject_slot('value')
    def _do_redo(self, value):
        if value != 0:
            if self.song().can_redo == 1:
                self.song().redo()
                self.show_message(str('REDO'))

    @subject_slot('value')
    def _do_stop_all(self, value):
        if value != 0:
            if self.use_layered_buttons() and self.isShiftDown():
                self.song().stop_all_clips(0)
            else:
                self.song().stop_all_clips(1)

    def isShiftDown(self):
        return self._editsection.isShiftdown()

    def modifiers(self):
        return self._editsection.modifiers()

    def use_layered_buttons(self):
        return False

    def _handle_base_note(self, diff):
        self._modeselect._pad_mode.inc_base_note(diff)

    def _handle_octave(self, diff):
        self._modeselect._pad_mode.inc_octave(diff)
        octave_val = self._modeselect._pad_mode

    def _handle_scale(self, diff):
        self._modeselect._pad_mode.inc_scale(diff)

    @subject_slot('value')
    def _do_update_display(self, value):
        if value != 0:
            self.refresh_state()

    @subject_slot('value')
    def _do_key_color(self, value):
        if not value in range(128):
            raise AssertionError
            value != 0 and self._modeselect._pad_mode.step_key_color_mode()

    @subject_slot('value')
    def _do_tap_tempo(self, value):
        if not value in range(128):
            raise AssertionError
            value != 0 and self.song().tap_tempo()

    @subject_slot('value')
    def _do_toggle_cue(self, value):
        if not value in range(128):
            raise AssertionError
            value != 0 and self.song().set_or_delete_cue()

    @subject_slot('value')
    def _do_toggle_prev_cue(self, value):
        if not value in range(128):
            raise AssertionError
            value != 0 and self.song().jump_to_prev_cue()

    @subject_slot('value')
    def _do_toggle_next_cue(self, value):
        if not value in range(128):
            raise AssertionError
            value != 0 and self.song().jump_to_next_cue()

    @subject_slot('value')
    def _do_toggle_send(self, value):
        if not value in range(128):
            raise AssertionError
            if self.isShiftDown():
                value != 0 and self.refresh_state()
                self.show_message('Refresh Display')
        else:
            nr_of_tracks = len(self.song().return_tracks)
            if value == 0 or nr_of_tracks < 1:
                return
            prev = self.send_slider_index
            self.send_slider_index += 1
            if self.send_slider_index >= nr_of_tracks:
                self.send_slider_index = 0
            self.show_message(' Set Send ' + str(SENDS[self.send_slider_index]))
            self.timed_message(2, ' Set Send ' + str(SENDS[self.send_slider_index]))
            if prev != self.send_slider_index:
                for track in range(8):
                    strip = self._mixer.channel_strip(track)
                    slider_list = []
                    for index in range(self.send_slider_index + 1):
                        if index < self.send_slider_index - 1:
                            slider_list.append(None)
                        else:
                            slider_list.append(self.send_sliders[track])
                        strip.set_send_controls(tuple(slider_list))

    @subject_slot('value')
    def _a_trk_left(self, value):
        if not value in range(128):
            raise AssertionError
            if value != 0:
                if self.application().view.is_view_visible('Session'):
                    direction = Live.Application.Application.View.NavDirection.left
                    self.application().view.scroll_view(direction, 'Session', True)
                    track = self.song().view.selected_track
                    self.timed_message(2, 'T:' + track.name, False)
                    self.arm_selected_track and track.can_be_armed and arm_exclusive(self.song(), track)

    @subject_slot('value')
    def _a_trk_right(self, value):
        if not value in range(128):
            raise AssertionError
            if value != 0:
                if self.application().view.is_view_visible('Session'):
                    direction = Live.Application.Application.View.NavDirection.right
                    self.application().view.scroll_view(direction, 'Session', True)
                    track = self.song().view.selected_track
                    self.timed_message(2, 'T:' + track.name, False)
                    self.arm_selected_track and track.can_be_armed and arm_exclusive(self.song(), track)

    @subject_slot('value')
    def _a_sel_arm(self, value):
        if value != 0:
            if self.arm_selected_track:
                self.arm_selected_track = False
                self.set_sel_arm_button.send_value(0, True)
            else:
                self.arm_selected_track = True
                self.set_sel_arm_button.send_value(127, True)

    @subject_slot('value')
    def _nav_value_left(self, value):
        if not self._device_nav_button_left != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                modifier_pressed = True
                value != 0 and (not self.application().view.is_view_visible('Detail') or not self.application().view.is_view_visible('Detail/DeviceChain')) and self.application().view.show_view('Detail')
                self.application().view.show_view('Detail/DeviceChain')
            else:
                direction = Live.Application.Application.View.NavDirection.left
                self.application().view.scroll_view(direction, 'Detail/DeviceChain', not modifier_pressed)

    @subject_slot('value')
    def _nav_value_right(self, value):
        if not self._device_nav_button_right != None:
            raise AssertionError
            if not value in range(128):
                raise AssertionError
                modifier_pressed = value != 0 and True
                (not self.application().view.is_view_visible('Detail') or not self.application().view.is_view_visible('Detail/DeviceChain')) and self.application().view.show_view('Detail')
                self.application().view.show_view('Detail/DeviceChain')
            else:
                direction = Live.Application.Application.View.NavDirection.right
                self.application().view.scroll_view(direction, 'Detail/DeviceChain', not modifier_pressed)

    @subject_slot('value')
    def _do_focus_navigate(self, value):
        if not self._navigate_button != None:
            raise AssertionError
            raise value in range(128) or AssertionError
            self.nav_index = value != 0 and (self.nav_index + 1) % len(VIEWS_ALL)
            self.application().view.focus_view(VIEWS_ALL[self.nav_index])
            self.show_message('Focus on : ' + str(VIEWS_ALL[self.nav_index]))

    def focus_clip_detail(self):
        self.application().view.focus_view('Detail/Clip')

    @subject_slot('follow_song')
    def _song_follow_changed(self):
        view = self.song().view
        if view.follow_song:
            self.song_follow_button.send_value(1, True)
        else:
            self.song_follow_button.send_value(0, True)

    @subject_slot('value')
    def _do_song_follow(self, value):
        if value != 0:
            view = self.song().view
            if view.follow_song:
                view.follow_song = False
                self.song_follow_button.send_value(0, True)
            else:
                view.follow_song = True
                self.song_follow_button.send_value(1, True)

    @subject_slot('value')
    def _hold_duplicate_action(self, value):
        if value != 0:
            pass

    @subject_slot('value')
    def _hold_clear_action(self, value):
        if value != 0:
            self._mixer.enter_clear_mode()
            self._device_component.enter_clear_mode()
        else:
            self._mixer.exit_clear_mode()
            self._device_component.exit_clear_mode()

    @subject_slot('value')
    def _action_toogle_main_view(self, value):
        if value != 0:
            appv = self.application().view
            if appv.is_view_visible('Arranger'):
                appv.show_view('Session')
            else:
                appv.show_view('Arranger')

    @subject_slot('value')
    def _action_toogle_detail_view(self, value):
        if value != 0:
            appv = self.application().view
            if self.isShiftDown():
                if appv.is_view_visible('Arranger'):
                    appv.show_view('Session')
                else:
                    appv.show_view('Arranger')
            elif appv.is_view_visible('Detail/Clip'):
                appv.show_view('Detail/DeviceChain')
            else:
                appv.show_view('Detail/Clip')

    @subject_slot('re_enable_automation_enabled')
    def _on_change_reenabled(self):
        if self.song().re_enable_automation_enabled:
            self._reenable_button.turn_on()
        else:
            self._reenable_button.turn_off()

    @subject_slot('value')
    def _do_auto_reenable(self, value):
        if value != 0:
            self.song().re_enable_automation()

    def to_color_edit_mode(self, active):
        pass

    def clear_display_all(self):
        self.send_to_display('', 0)
        self.send_to_display('', 1)
        self.send_to_display('', 2)
        self.send_to_display('', 3)

    def clear_display(self, grid):
        self.send_to_display('', grid)

    def timed_message(self, grid, text, hold = False):
        if USE_DISPLAY == False:
            self.show_message(text)
        else:
            self.display_task.set_func(self.clear_display, grid)
            self.send_to_display(text, grid)
            if hold:
                self.display_task.hold()
            self.display_task.start()

    def timed_message_release(self):
        self.display_task.release()

    def update_bank_display(self):
        if USE_DISPLAY:
            name, bank = self._device._current_bank_details()
            if self._display_device_param:
                prms = len(bank)
                d1 = ''
                for i in range(4):
                    parm = bank[i]
                    if parm:
                        name = parm.name
                        d1 += name[:6] + (i < 3 and '|' or '')
                    else:
                        d1 += '      ' + (i < 3 and '|' or '')

                self.send_to_display(d1, 2)
                d1 = ''
                for i in range(4):
                    parm = bank[i + 4]
                    if parm:
                        name = parm.name
                        d1 += name[:6] + (i < 3 and '|' or '')
                    else:
                        d1 += '      ' + (i < 3 and '|' or '')

                self.send_to_display(d1, 4)
            else:
                self.timed_message(2, 'Bank: ' + name)

    def display_parameters(self, paramlist):
        if USE_DISPLAY == False:
            return

    def send_to_display(self, text, grid = 0):
        if USE_DISPLAY == False:
            return
        if self._diplay_cache[grid] == text:
            return
        self._diplay_cache[grid] = text
        if len(text) > 28:
            text = text[:27]
        msgsysex = [240,
         0,
         0,
         102,
         23,
         18,
         min(grid, 3) * 28]
        filled = text.ljust(28)
        for c in filled:
            msgsysex.append(ord(c))

        msgsysex.append(247)
        self._send_midi(tuple(msgsysex))

    def cleanup(self):
        pass

    def disconnect(self):
        self._pre_serialize()
        self.clear_display_all()
        for button, (track_index, scene_index) in self._bmatrix.iterbuttons():
            if button:
                button.send_color_direct(PColor.OFF[0])

        time.sleep(0.2)
        self._active = False
        self._suppress_send_midi = True
        super(Maschine, self).disconnect()