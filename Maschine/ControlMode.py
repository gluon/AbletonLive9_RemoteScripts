#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\ControlMode.py
"""
Created on 04.11.2013

@author: Eric Ahrens
"""
from _Framework.SubjectSlot import subject_slot
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from _Framework.DeviceBankRegistry import DeviceBankRegistry
from _Generic.Devices import *
from MaschineMode import MaschineMode
from MIDI_Map import *
CM_LEVEL = 0
CM_PAN = 1
CM_SEND = 2
CM_DEVICE = 3
BASIC_COLORS = (PColor.MIX_MODE_VOLUME,
 PColor.MIX_MODE_PANNING,
 PColor.MIX_MODE_SEND,
 PColor.MIX_MODE_DEVICE)
N_PARM_RANGE = 127

def is_equal(val1, val2):
    if val1 == val2:
        return True
    if abs(val1 - val2) < 0.005:
        return True
    return False


class ControlTrackElement:

    def __init__(self, index, *a, **k):
        self._button = None
        self._track = None
        self._index = index
        self._callback = None
        self._color = None
        self._dev_param = None

    def set_button(self, button, select_callback):
        if not self._button:
            self._button = button
            self._button.add_value_listener(self.select)
            self._callback = select_callback

    def set_color(self, color):
        self._color = color

    def set_parm(self, parm):
        self._dev_param = parm

    def turn_on(self):
        if self._button and self._color:
            self._button.send_color_direct(self._color[0])

    def turn_off(self):
        if self._button and self._color:
            self._button.send_color_direct(self._color[1])

    def select(self, value):
        if value > 0 and self._callback:
            self._callback(self._index)

    def set_track(self, track):
        self._track = track

    def release(self):
        if self._button:
            self._button.remove_value_listener(self.select)
            self._button = None
        self.track = None
        self._dev_param = None


class ControlMode(MaschineMode):
    _mode = CM_LEVEL
    _track_sel_index = 0
    _track_off = 0
    _knob_section = None
    _parm_raster_value = 1
    _parm = None
    _parm_is_quant = False
    _selected_sends_index = 0
    _bank_index = 0
    _parm_index = 0
    _device_parm = None
    _banks = None
    _device = None
    _device_list = None
    _in_clear_mode = False

    def __init__(self, button_index, mono_chrome = False, *a, **k):
        super(ControlMode, self).__init__(button_index, *a, **k)
        self._device_bank_registry = DeviceBankRegistry()
        self._device_bank_registry.add_device_bank_listener(self._on_device_bank_changed)
        self.track_selections = tuple((ControlTrackElement(idx) for idx in range(8)))
        self._is_monochrome = mono_chrome
        self.main_buttons = ([None, self._do_select_level],
         [None, self._do_select_pan],
         [None, self._do_select_send],
         [None, self._do_select_device])
        self.nav_buttons = ([None, self._do_nav1],
         [None, self._do_nav2],
         [None, self._do_nav3],
         [None, self._do_nav4])
        self.song().add_return_tracks_listener(self.return_tracks_changed)

    def connect_main_knob(self, knobsection):
        self._knob_section = knobsection

    def knob_adjust(self, inc, shift, pushdown):
        if self._parm:
            if pushdown:
                value = self.change_parm(inc, self._parm, False)
                self._parm.value = value
            else:
                count = 0
                while count < 4:
                    value = self.change_parm(inc, self._parm, False)
                    self._parm.value = value
                    count += 1

        elif self._device_parm:
            if self._parm_is_quant:
                val = self.change_parm(inc, self._device_parm, True)
                self._device_parm.value = val
            else:
                new_value = self.change_parm(inc, self._device_parm, False)
                self._device_parm.value = new_value
                if not is_equal(self._device_parm.value, new_value):
                    self.parm_is_quant = True
                if not self.parm_is_quant and not pushdown:
                    count = 0
                    while count < 3:
                        value = self.change_parm(inc, self._device_parm, False)
                        self._device_parm.value = value
                        count += 1

    def change_parm(self, delta, parm, is_quant):
        if is_quant:
            parm_range = parm.max - parm.min + 1
            new_val = min(parm.max, max(parm.min, parm.value + delta))
            return float(new_val)
        else:
            parm_range = parm.max - parm.min
            self._parm_raster_value = min(N_PARM_RANGE, max(0, self._parm_raster_value + delta))
            return float(self._parm_raster_value) / float(N_PARM_RANGE) * parm_range + parm.min

    def get_mode_id(self):
        return CONTROL_MODE

    def navigate(self, dir, modifier, alt_modifier = False):
        tracks = self.song().tracks
        nr_of_tracks = len(tracks)
        new_off = self._track_off + dir
        if new_off >= 0 and new_off + 8 <= nr_of_tracks:
            self._track_off = new_off
            self._track_sel_index += dir
            self.canonical_parent.show_message('Control assigned to Tracks ' + str(self._track_off + 1) + ' to ' + str(self._track_off + 9))
            self._assign(False)

    def unbind(self):
        pass

    def nr_of_parms_in_bank(self, device, bank_index):
        if device == None:
            return 0
        nr_of_parms = len(device.parameters)
        bip = nr_of_parms - 8 * bank_index
        if bip < 8:
            return bip
        return 8

    def _assign(self, register = True):
        tracks = self.song().tracks
        bmatrix = self.canonical_parent._bmatrix
        for button, (column, row) in bmatrix.iterbuttons():
            if button:
                if register:
                    self.canonical_parent._forwarding_registry[MIDI_NOTE_ON_STATUS, button.get_identifier()] = button
                    self.canonical_parent._forwarding_registry[MIDI_NOTE_OFF_STATUS, button.get_identifier()] = button
                    button.set_to_notemode(False)
                if row < 2:
                    index = row * 4 + column
                    tindex = index + self._track_off
                    track = None
                    if tindex < len(tracks):
                        track = tracks[tindex]
                    self.track_selections[index].set_button(button, self._do_track_selection)
                    self.track_selections[index].set_track(track)
                elif row < 3:
                    if not self.main_buttons[column][0]:
                        self.main_buttons[column][0] = button
                        button.add_value_listener(self.main_buttons[column][1])
                else:
                    if not self.nav_buttons[column][0]:
                        self.nav_buttons[column][0] = button
                        button.add_value_listener(self.nav_buttons[column][1])
                    if self._mode == CM_LEVEL or self._mode == CM_PAN:
                        button.send_color_direct(PColor.OFF[1])

        self._mode_sel()

    def _set_send_color(self, nr_ret_tracks, index, button):
        if index == 3:
            button.send_color_direct(PColor.OFF[0])
            if nr_ret_tracks > index:
                col = max(21, (21 + (self._selected_sends_index - 3) * 20) % 127)
                if self._selected_sends_index >= 3:
                    col = max(21, (21 + (self._selected_sends_index - 3) * 20) % 127)
                    button.send_color_direct((col,
                     120,
                     127,
                     1,
                     0))
                else:
                    button.send_color_direct((21, 120, 20, 0, 0))
        elif nr_ret_tracks > index:
            if index == self._selected_sends_index:
                button.send_color_direct(PColor.MIX_SELECT_SEND[0])
            else:
                button.send_color_direct(PColor.MIX_SELECT_SEND[1])
        else:
            button.send_color_direct(PColor.OFF[0])

    def _turn_off_nav_buttons(self):
        for button, callback in self.nav_buttons:
            if button:
                button.send_color_direct(PColor.OFF[0])

    def _set_up_control_send(self):
        nr_of_tracks = len(self.song().return_tracks)
        for idx in range(4):
            self._set_send_color(nr_of_tracks, idx, self.nav_buttons[idx][0])

    def _assign_device_nav(self):
        if self._device:
            idx = list(self._device_list).index(self._device)
            nr_of_dev = len(self._device_list)
            if idx > 0:
                self.nav_buttons[0][0].send_color_direct(PColor.DEVICE_LEFT[0])
            else:
                self.nav_buttons[0][0].send_color_direct(PColor.DEVICE_LEFT[1])
            if idx < nr_of_dev - 1:
                self.nav_buttons[1][0].send_color_direct(PColor.DEVICE_RIGHT[0])
            else:
                self.nav_buttons[1][0].send_color_direct(PColor.DEVICE_RIGHT[1])
            nr_of_banks = len(self._banks)
            if self._bank_index > 0:
                self.nav_buttons[2][0].send_color_direct(PColor.BANK_LEFT[0])
            else:
                self.nav_buttons[2][0].send_color_direct(PColor.BANK_LEFT[1])
            if self._bank_index < nr_of_banks - 1:
                self.nav_buttons[3][0].send_color_direct(PColor.BANK_RIGHT[0])
            else:
                self.nav_buttons[3][0].send_color_direct(PColor.BANK_RIGHT[1])
        else:
            self.nav_buttons[0][0].send_color_direct(PColor.DEVICE_LEFT[1])
            self.nav_buttons[1][0].send_color_direct(PColor.DEVICE_RIGHT[1])
            self.nav_buttons[2][0].send_color_direct(PColor.BANK_LEFT[1])
            self.nav_buttons[3][0].send_color_direct(PColor.BANK_RIGHT[1])

    def _assign_device_selection(self):
        if not self._device:
            self._update_device()
        device = self._device
        self._parm = None
        self._device_parm = None
        if device:
            is_on = device.parameters[0].value == 1
            if len(self._banks) > 0:
                bank = self._banks[self._bank_index]
                for parameter, track_sel in zip(bank, self.track_selections):
                    track_sel.set_parm(parameter)
                    if parameter:
                        track_sel.set_color(is_on and PColor.MIX_MODE_DEVICE or PColor.MIX_MODE_DEVICE_OFF)
                        if self._parm_index == track_sel._index:
                            track_sel.turn_on()
                            self._assign_device_parm(parameter)
                        else:
                            track_sel.turn_off()
                    else:
                        track_sel.set_color(PColor.OFF)
                        track_sel.turn_off()

            else:
                for track_sel in self.track_selections:
                    track_sel.set_parm(None)
                    track_sel.set_color(PColor.OFF)
                    track_sel.turn_off()

        else:
            for track_sel in self.track_selections:
                track_sel.set_color(PColor.OFF)
                track_sel.turn_off()

        self._assign_device_nav()

    def _mode_sel(self):
        self.main_buttons[0][0].send_color_direct(self._mode == CM_LEVEL and PColor.MIX_MODE_VOLUME[0] or PColor.MIX_MODE_VOLUME[1])
        self.main_buttons[1][0].send_color_direct(self._mode == CM_PAN and PColor.MIX_MODE_PANNING[0] or PColor.MIX_MODE_PANNING[1])
        self.main_buttons[2][0].send_color_direct(self._mode == CM_SEND and PColor.MIX_MODE_SEND[0] or PColor.MIX_MODE_SEND[1])
        self.main_buttons[3][0].send_color_direct(self._mode == CM_DEVICE and PColor.MIX_MODE_DEVICE[0] or PColor.MIX_MODE_DEVICE[1])
        reassign_parms = False
        if self._mode <= CM_SEND:
            max_index = 0
            for track_sel in self.track_selections:
                if track_sel._track:
                    max_index = track_sel._index

            if self._track_sel_index > max_index:
                self._track_sel_index = max_index
                reassign_parms = True
            for track_sel in self.track_selections:
                if track_sel._track:
                    track_sel.set_color(BASIC_COLORS[self._mode])
                else:
                    track_sel.set_color(PColor.OFF)
                if track_sel._index == self._track_sel_index:
                    track_sel.turn_on()
                else:
                    track_sel.turn_off()

            if self._mode == CM_SEND:
                nr_of_tracks = len(self.song().return_tracks)
                if self._selected_sends_index > nr_of_tracks - 1:
                    reassign_parms = True
                    self._selected_sends_index = nr_of_tracks - 1
                for idx in range(4):
                    self._set_send_color(nr_of_tracks, idx, self.nav_buttons[idx][0])

            else:
                self._turn_off_nav_buttons()
        else:
            self._assign_device_selection()
        if reassign_parms:
            self._assign_parameters()

    def _assign_device_parm(self, param):
        self.parm_device_message(param)
        self._device_parm = param
        if param.is_quantized:
            self._parm_is_quant = True
        else:
            self._parm_is_quant = False
            parm_range = param.max - param.min
            self._parm_raster_value = int((param.value - param.min) / parm_range * N_PARM_RANGE + 0.1)

    def parm_device_message(self, param):
        self.canonical_parent.show_message(' Control ' + str(param.name))

    def _get_mixer_parm(self, track):
        if self._mode == CM_LEVEL:
            return track.mixer_device.volume
        elif self._mode == CM_PAN:
            return track.mixer_device.panning
        elif self._mode == CM_SEND:
            nr_of_ret_tracks = len(track.mixer_device.sends)
            if self._selected_sends_index < nr_of_ret_tracks and self._selected_sends_index != -1:
                return track.mixer_device.sends[self._selected_sends_index]

    def _assign_mixer_parm(self, track):
        self._device_parm = None
        if self._mode == CM_LEVEL:
            self._parm = track.mixer_device.volume
        elif self._mode == CM_PAN:
            self._parm = track.mixer_device.panning
        elif self._mode == CM_SEND:
            self._device_parm = None
            nr_of_ret_tracks = len(track.mixer_device.sends)
            if self._selected_sends_index < nr_of_ret_tracks and self._selected_sends_index != -1:
                self._parm = track.mixer_device.sends[self._selected_sends_index]
        self.parm_is_quant = False
        if self._parm:
            parm_range = self._parm.max - self._parm.min
            self._parm_raster_value = int((self._parm.value - self._parm.min) / parm_range * N_PARM_RANGE + 0.1)

    def _assign_parameters(self):
        current = self.track_selections[self._track_sel_index]
        track = current._track
        if track:
            self._assign_mixer_parm(track)

    def _do_track_selection(self, button_index):
        self._knob_section.set_override(self.knob_adjust)
        track_sel = self.track_selections[button_index]
        if self._mode == CM_DEVICE:
            if track_sel._dev_param:
                if self._in_clear_mode:
                    cs = self.song().view.highlighted_clip_slot
                    if cs and cs.has_clip:
                        cs.clip.clear_envelope(track_sel._dev_param)
                else:
                    current = self.track_selections[self._parm_index]
                    current.turn_off()
                    self._parm_index = button_index
                    track_sel.turn_on()
                    self._assign_device_parm(track_sel._dev_param)
        else:
            current = self.track_selections[self._track_sel_index]
            if self._in_clear_mode and track_sel._track:
                parm = self._get_mixer_parm(track_sel._track)
                cs = self.song().view.highlighted_clip_slot
                if parm and cs and cs.has_clip:
                    cs.clip.clear_envelope(parm)
            elif button_index != self._track_sel_index and track_sel._track:
                current.turn_off()
                track_sel.turn_on()
                current = track_sel
                self._track_sel_index = button_index
                self._assign_mixer_parm(track_sel._track)

    def _do_select_level(self, value):
        self._knob_section.set_override(self.knob_adjust)
        if value > 0 and self._mode != CM_LEVEL:
            self._mode = CM_LEVEL
            self._mode_sel()
            self._assign_parameters()
            if self.canonical_parent.is_monochrome():
                self.canonical_parent.show_message('Control Mode Focus: Track Levels')

    def _do_select_pan(self, value):
        self._knob_section.set_override(self.knob_adjust)
        if value > 0 and self._mode != CM_PAN:
            self._mode = CM_PAN
            self._mode_sel()
            self._assign_parameters()
            if self.canonical_parent.is_monochrome():
                self.canonical_parent.show_message('Control Mode Focus: Track Panning')

    def _do_select_send(self, value):
        self._knob_section.set_override(self.knob_adjust)
        if value > 0 and self._mode != CM_SEND:
            self._mode = CM_SEND
            self._mode_sel()
            self._assign_parameters()
            if self.canonical_parent.is_monochrome():
                self.canonical_parent.show_message('Control Mode Focus: Track Sends')

    def _do_select_device(self, value):
        self._knob_section.set_override(self.knob_adjust)
        if value > 0 and self._mode == CM_DEVICE and self.isShiftDown():
            if self._device:
                parm = self._device.parameters[0]
                if parm.value == 0:
                    parm.value = 1
                else:
                    parm.value = 0
        if value > 0 and self._mode != CM_DEVICE:
            self._mode = CM_DEVICE
            self._mode_sel()
            self._assign_device_selection()
            if self.canonical_parent.is_monochrome():
                self.canonical_parent.show_message('Control Mode Focus: Device')

    def _do_nav1(self, value):
        self._knob_section.set_override(self.knob_adjust)
        if value > 0:
            if self._mode == CM_SEND:
                nr_of_tracks = len(self.song().return_tracks)
                if nr_of_tracks > 0:
                    self._selected_sends_index = 0
                    self._set_up_control_send()
                    self._assign_parameters()
                    self.canonical_parent.show_message('Control Mode Focus: Send A')
            elif self._mode == CM_DEVICE and self._device:
                if not self.application().view.is_view_visible('Detail') or not self.application().view.is_view_visible('Detail/DeviceChain'):
                    self.application().view.show_view('Detail')
                    self.application().view.show_view('Detail/DeviceChain')
                direction = Live.Application.Application.View.NavDirection.left
                self.application().view.scroll_view(direction, 'Detail/DeviceChain', False)

    def _do_nav2(self, value):
        self._knob_section.set_override(self.knob_adjust)
        if value > 0:
            if self._mode == CM_SEND:
                nr_of_tracks = len(self.song().return_tracks)
                if nr_of_tracks > 1:
                    self._selected_sends_index = 1
                    self._set_up_control_send()
                    self._assign_parameters()
                    self.canonical_parent.show_message('Control Mode Focus: Send B')
            elif self._mode == CM_DEVICE and self._device:
                if not self.application().view.is_view_visible('Detail') or not self.application().view.is_view_visible('Detail/DeviceChain'):
                    self.application().view.show_view('Detail')
                    self.application().view.show_view('Detail/DeviceChain')
                direction = Live.Application.Application.View.NavDirection.right
                self.application().view.scroll_view(direction, 'Detail/DeviceChain', False)

    def _do_nav3(self, value):
        self._knob_section.set_override(self.knob_adjust)
        if value > 0:
            if self._mode == CM_SEND:
                nr_of_tracks = len(self.song().return_tracks)
                if nr_of_tracks > 2:
                    self._selected_sends_index = 2
                    self._set_up_control_send()
                    self._assign_parameters()
                    self.canonical_parent.show_message('Control Mode Focus: Send C')
            elif self._mode == CM_DEVICE and self._device and len(self._banks) > 0:
                self._bank_index = max(0, self._bank_index - 1)
                bank = self._banks[self._bank_index]
                name = self._parameter_bank_names()[self._bank_index]
                self._device_bank_registry.set_device_bank(self._device, self._bank_index)
                self._assign_device_selection()
                self.canonical_parent.show_message(' Bank : ' + name)

    def _do_nav4(self, value):
        self._knob_section.set_override(self.knob_adjust)
        if value > 0:
            if self._mode == CM_SEND:
                nr_of_tracks = len(self.song().return_tracks)
                if nr_of_tracks > 3:
                    if self._selected_sends_index < 3 or self._selected_sends_index + 1 == nr_of_tracks:
                        self._selected_sends_index = 3
                    else:
                        self._selected_sends_index += 1
                    self._set_up_control_send()
                    self._assign_parameters()
                    self.canonical_parent.show_message('Control Mode Focus: Send ' + SENDS[self._selected_sends_index])
            elif self._mode == CM_DEVICE and self._device and len(self._banks) > 0:
                max_bank = len(self._banks) - 1
                self._bank_index = min(max_bank, self._bank_index + 1)
                name = self._parameter_bank_names()[self._bank_index]
                self._device_bank_registry.set_device_bank(self._device, self._bank_index)
                self._assign_device_selection()
                self.canonical_parent.show_message(' Bank : ' + name)

    def _release(self):
        for track_sel in self.track_selections:
            track_sel.release()

        for button, callback in self.main_buttons:
            if button:
                button.remove_value_listener(callback)

        for button, callback in self.nav_buttons:
            if button:
                button.remove_value_listener(callback)

        for idx in range(4):
            self.main_buttons[idx][0] = None
            self.nav_buttons[idx][0] = None

        self._device_parameters_changed.subject = None
        self._device_active_changed.subject = None

    def _on_device_bank_changed(self, device, bank):
        if device == self._device:
            self._bank_index = bank
            self._assign_device_selection()

    def _update_device(self):
        self._device = self.song().appointed_device
        if self._device:
            self._parm_index = 0
            track = self._device.canonical_parent
            devices = track.devices
            self._device_list = track.devices
            self._device_parameters_changed.subject = self._device
            self._device_active_changed.subject = self._device.parameters[0]
            self._banks = parameter_banks(self._device)
            self._bank_index = self._device_bank_registry.get_device_bank(self._device)
        else:
            self._device_parameters_changed.subject = None
            self._device_active_changed.subject = None

    def _device_changed(self):
        if self._active:
            self._bank_index = 0
            if self._mode == CM_DEVICE:
                self._update_device()
                self._assign_device_selection()

    def return_tracks_changed(self):
        if self._active:
            self._assign(False)

    @subject_slot('parameters')
    def _device_parameters_changed(self):
        if self._active and self._mode == CM_DEVICE:
            self._banks = parameter_banks(self._device)
            self._bank_index = self._device_bank_registry.get_device_bank(self._device)
            self._assign_device_selection()

    @subject_slot('value')
    def _device_active_changed(self):
        if self._active and self._mode == CM_DEVICE:
            self._assign_device_selection()

    def on_track_list_changed(self):
        if self._active:
            for track_sel in self.track_selections:
                track_sel.release()

            self._assign(False)

    def _parameter_bank_names(self):
        return parameter_bank_names(self._device)

    def enter(self):
        self._active = True
        self._assign()
        if self._knob_section:
            self._knob_section.set_override(self.knob_adjust)
            self._assign_parameters()

    def exit(self):
        self._active = False
        self._release()
        if self._knob_section:
            self._knob_section.reset_overide()

    def enter_clear_state(self):
        self._in_clear_mode = True

    def exit_clear_state(self):
        self._in_clear_mode = False

    def disconnect(self):
        if self._active:
            self._release()
        self.song().remove_return_tracks_listener(self.return_tracks_changed)
        self._device_bank_registry.remove_device_bank_listener(self._on_device_bank_changed)
        self._device_parameters_changed.subject = None
        super(MaschineMode, self).disconnect()