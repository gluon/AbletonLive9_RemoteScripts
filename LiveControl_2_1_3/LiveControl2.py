#Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/LiveControl_2_13/LiveControl2.py
from __future__ import with_statement
from _Framework.ControlSurface import ControlSurface
from _Framework.SliderElement import SliderElement
from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import *
from LC2Sysex import LC2Sysex, LC2SysexParser
from LC2SessionComponent import LC2SessionComponent
from LC2MixerComponent import LC2MixerComponent
from LC2Modulator import LC2Modulator
from LC2Sequencer import LC2Sequencer
from LC2SessionSnapshot import LC2SessionBank
from LC2TransportComponent import LC2TransportComponent
from LC2ParameterElement import LC2ParameterElement

class LiveControl2(ControlSurface):
    _active_instances = []

    def _combine_active_instances():
        track_offset = 0
        for instance in LiveControl2._active_instances:
            instance._activate_combination_mode(track_offset)
            track_offset += instance._session.width()

    _combine_active_instances = staticmethod(_combine_active_instances)

    def _do_combine(self):
        if self not in LiveControl2._active_instances:
            LiveControl2._active_instances.append(self)
            LiveControl2._combine_active_instances()

    def _activate_combination_mode(self, track_offset):
        if self._session._is_linked():
            self._session._unlink()
        self._session.set_offsets(track_offset, 0)
        self._session._link()

    def _do_uncombine(self):
        if self in LiveControl2._active_instances and LiveControl2._active_instances.remove(self):
            self._session.unlink()
            LiveControl2._combine_active_instances()

    def log_message(self, str):
        pass

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        LC2Sysex.set_log(self.log_message)
        if LC2Sysex.l9():
            with self.component_guard():
                self.do_setup()
        else:
            self.do_setup()

    def do_setup(self):
        if LC2Sysex.l9():
            self._set_suppress_rebuild_requests(True)
        else:
            self.set_suppress_rebuild_requests(True)
        self._suppress_session_highlight = True
        self._suppress_send_midi = True
        LC2Sysex.set_midi_callback(self._send_midi)
        LC2SessionBank.set_song(self.song)
        LC2SessionBank.set_timer_callback(self.schedule_message)
        self._session = LC2SessionComponent(8, 12)
        self._mixer = LC2MixerComponent(8)
        self._session.set_mixer(self._mixer)
        if LC2Sysex.l9():
            self.set_highlighting_session_component(self._session)
        bank_buttons = [ ButtonElement(False, MIDI_NOTE_TYPE, 0, 40 + i) for i in range(4) ]
        self._session.set_scene_bank_buttons(bank_buttons[0], bank_buttons[1])
        self._session.set_track_bank_buttons(bank_buttons[2], bank_buttons[3])
        mixer_controls = [ SliderElement(MIDI_CC_TYPE, 0, i) for i in range(24) ]
        mixer_d_controls = [ LC2ParameterElement(MIDI_CC_TYPE, 0, i + 64) for i in range(32) ]
        toggle_controls = [ ButtonElement(True, MIDI_NOTE_TYPE, 0, i + 1) for i in range(24) ]
        cf = [ ButtonElement(True, MIDI_NOTE_TYPE, 0, i + 30) for i in range(8) ]
        mt = [ ButtonElement(True, MIDI_NOTE_TYPE, 0, i + 50) for i in range(8) ]
        self._mixer.master_strip().set_volume_control(SliderElement(MIDI_CC_TYPE, 0, 33))
        self._mixer.master_strip().set_pan_control(SliderElement(MIDI_CC_TYPE, 0, 34))
        self._mixer.set_prehear_volume_control(SliderElement(MIDI_CC_TYPE, 0, 35))
        self._mixer.set_crossfader_control(SliderElement(MIDI_CC_TYPE, 0, 40))
        for i in range(8):
            idx = i * 3
            ch = self._mixer.channel_strip(i)
            ch.set_invert_mute_feedback(True)
            ch.set_mute_button(toggle_controls[idx])
            ch.set_solo_button(toggle_controls[idx + 1])
            ch.set_arm_button(toggle_controls[idx + 2])
            ch.set_volume_control(mixer_controls[idx])
            ch.set_pan_control(mixer_controls[idx + 1])
            ch.set_send_control(mixer_controls[idx + 2])
            ch.set_crossfade_toggle(cf[i])
            ch.set_monitor_toggle(mt[i])
            ch.set_device_controls(tuple(mixer_d_controls[i * 4:i * 4 + 4]))

        self._modulator = LC2Modulator()
        self.set_device_component(self._modulator)
        device_controls = [ LC2ParameterElement(MIDI_CC_TYPE, 1, i, True) for i in range(16) ]
        self._modulator.set_parameter_controls(tuple(device_controls))
        device_buttons = [ ButtonElement(False, MIDI_NOTE_TYPE, 1, i) for i in range(4) ]
        self._modulator.set_on_off_button(device_buttons[0])
        self._modulator.set_lock_button(device_buttons[1])
        self._modulator.set_bank_nav_buttons(device_buttons[2], device_buttons[3])
        self._sequencer = LC2Sequencer()
        self._session.set_sequencer(self._sequencer)
        self._transport = LC2TransportComponent()
        tbuttons = [ ButtonElement(True, MIDI_NOTE_TYPE, 0, 110 + i) for i in range(12) ]
        self._transport.set_stop_button(tbuttons[0])
        self._transport.set_play_button(tbuttons[1])
        self._transport.set_record_button(tbuttons[2])
        self._transport.set_overdub_button(tbuttons[3])
        self._transport.set_back_to_arranger_button(tbuttons[4])
        self._transport.set_follow_button(tbuttons[5])
        self._transport.set_metronome_button(tbuttons[6])
        self._transport.set_tap_tempo_button(tbuttons[7])
        self._transport.set_tempo_buttons(tbuttons[9], tbuttons[8])
        self._transport.set_launch_quant_button(SliderElement(MIDI_CC_TYPE, 0, 120))
        self._transport.set_record_quant_button(SliderElement(MIDI_CC_TYPE, 0, 121))
        self._last_time = ''
        if LC2Sysex.l9():

            def wrapper(delta):
                self._on_time_changed()
                return Task.RUNNING

            self._tasks.add(Task.FuncTask(wrapper, self._on_time_changed))
        else:
            self._register_timer_callback(self._on_time_changed)
        self.song().add_tempo_listener(self._on_tempo_changed)
        for component in self.components:
            component.set_enabled(False)

        if LC2Sysex.l9():
            self._set_suppress_rebuild_requests(False)
        else:
            self.set_suppress_rebuild_requests(False)

    def refresh_state(self):
        ControlSurface.refresh_state(self)
        self.schedule_message(5, self._init)

    def disconnect(self):
        self._do_uncombine()
        if LC2Sysex.l9():
            task = self._tasks.find(self._on_time_changed)
            self._tasks.remove(task)
        else:
            self._unregister_timer_callback(self._on_time_changed)
        self.song().remove_tempo_listener(self._on_tempo_changed)
        ControlSurface.disconnect(self)
        LC2Sysex.release_attributes()
        LC2SessionBank.release_attributes()

    def handle_sysex(self, sysex):
        if list(sysex).count(247) == 0:
            count = 1
        else:
            count = list(sysex).count(247)
        LC2Sysex.log_message(str(sysex))
        LC2Sysex.log_message('sysex count' + str(count))
        msysex = [ [] for i in range(count + 1) ]
        id = 0
        start = list(sysex).index(240)
        for i, b in enumerate(sysex):
            if i >= start:
                msysex[id].append(b)
                if b == 247:
                    id += 1

        LC2Sysex.log_message(str(msysex))
        pages = [self._session,
         self._mixer,
         self._sequencer,
         self._modulator]
        for sysex in msysex:
            if len(sysex) > 1:
                if sysex[1] == 5:
                    if sysex[2] == 1:
                        self._init()
                    elif sysex[2] == 2:
                        sysex = LC2SysexParser(sysex[3:])
                        interface = sysex.parse('b')
                        LC2Sysex.log_message('interface change: ' + str(interface))
                        if interface == 0 or interface == 1 or interface == 2:
                            self._mixer.set_enabled(1)
                        else:
                            self._mixer.set_enabled(0)
                elif sysex[1] < len(pages):
                    pages[sysex[1]].handle_sysex(sysex[2:])

    def _init(self):
        self._suppress_send_midi = False
        self._suppress_session_highlight = False
        for component in self.components:
            component.set_enabled(True)

        self._session.send_size()
        self._on_time_changed()
        self._on_tempo_changed()
        self._transport.send_init()
        self._modulator.send_params()
        sysex = LC2Sysex('RESET')
        sysex.send()

    def suggest_input_port(self):
        return 'Daemon Input '

    def suggest_output_port(self):
        return 'Daemon Output '

    def _on_tempo_changed(self):
        sysex = LC2Sysex('TEMPO')
        sysex.ascii(str(int(round(self.song().tempo, 0))))
        sysex.send()

    def _on_time_changed(self):
        smpt = self.song().get_current_smpte_song_time(0)
        if smpt.hours > 0:
            time = smpt.hours < 10 and '0' + str(smpt.hours) or str(smpt.hours) + ':' or '' + (smpt.minutes < 10 and '0' + str(smpt.minutes) or str(smpt.minutes)) + ':' + (smpt.seconds < 10 and '0' + str(smpt.seconds) or str(smpt.seconds))
            sysex = time != self._last_time and LC2Sysex('TIME')
            sysex.ascii(time)
            sysex.send()
            self._last_time = time

    def _do_send_midi(self, midi_event_bytes):
        if not self._suppress_send_midi:
            self._c_instance.send_midi(midi_event_bytes)
            return True