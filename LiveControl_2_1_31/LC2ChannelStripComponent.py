#Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/LiveControl_2_1_31/LC2ChannelStripComponent.py
from _Framework.ChannelStripComponent import ChannelStripComponent
from LC2ChannelDeviceComponent import LC2ChannelDeviceComponent
from LC2Sysex import LC2Sysex

class LC2ChannelStripComponent(ChannelStripComponent):

    @staticmethod
    def set_get_offsets(func):
        LC2ChannelStripComponent._get_offset = func

    @staticmethod
    def set_playing_slot_changed(func):
        LC2ChannelStripComponent.playing_slot_changed = func

    @staticmethod
    def release_attributes():
        LC2ChannelStripComponent._get_offset = None
        LC2ChannelStripComponent.playing_slot_changed = None

    def __init__(self, id):
        self._monitor_toggle = None
        ChannelStripComponent.__init__(self)
        self._track_id = id
        self._device = LC2ChannelDeviceComponent()

    def _send_init(self):
        self._send_state()
        self._on_selected_device_changed()

    def set_track(self, track):
        if self._track is not None:
            try:
                self._track.remove_color_listener(self._on_color_changed)
                self._track.remove_devices_listener(self._on_devices_changed)
                self._track.view.remove_selected_device_listener(self._on_selected_device_changed)
            except:
                pass

            if self._track in self.song().tracks and not self._track.is_foldable:
                self._track.remove_current_monitoring_state_listener(self._on_monitor_changed)
                self._track.remove_playing_slot_index_listener(self._on_playing_slot_changed)
        ChannelStripComponent.set_track(self, track)
        if track is not None:
            self._track.add_color_listener(self._on_color_changed)
            self._track.add_devices_listener(self._on_devices_changed)
            self._track.view.add_selected_device_listener(self._on_selected_device_changed)
            if track in self.song().tracks and not track.is_foldable:
                self._track.add_current_monitoring_state_listener(self._on_monitor_changed)
                self._track.add_playing_slot_index_listener(self._on_playing_slot_changed)
        self._on_selected_device_changed()

    def _on_playing_slot_changed(self):
        if hasattr(self, 'playing_slot_changed'):
            if self._track is not None:
                if self._track.playing_slot_index > -1:
                    self.playing_slot_changed(self._track.playing_slot_index, self._track.name)

    def set_monitor_toggle(self, control):
        if self._monitor_toggle is not None:
            self._monitor_toggle.remove_value_listener(self._on_monitor_value)
        self._monitor_toggle = control
        if control is not None:
            self._monitor_toggle.add_value_listener(self._on_monitor_value)

    def _on_monitor_value(self, value):
        if self.is_enabled():
            if self._track is not None and self._track in self.song().tracks:
                if value != 0 or not self._monitor_toggle.is_momentary():
                    self._track.current_monitoring_state = (self._track.current_monitoring_state + 1) % 3

    def _on_monitor_changed(self):
        if self.is_enabled() and self._monitor_toggle != None:
            if self._track != None and self._track in self.song().tracks and not self._track.is_foldable:
                self._monitor_toggle.send_value(self._track.current_monitoring_state)
            else:
                self._monitor_toggle.send_value(1)

    def _on_routing_changed2(self):
        self._on_routing_changed()

    def _on_routing_changed3(self):
        self._on_routing_changed()

    def _on_routing_changed4(self):
        self._on_routing_changed()

    def _on_routing_changed(self):
        if self._track_id < 8:
            self._send_routings()
            sysex = LC2Sysex('TRACK_ROUTING')
            sysex.byte(self._track_id)
            if self._track is not None:
                objs = [self._track.input_routings,
                 self._track.current_input_routing,
                 self._track.input_sub_routings,
                 self._track.current_input_sub_routing,
                 self._track.output_routings,
                 self._track.current_output_routing,
                 self._track.output_sub_routings,
                 self._track.current_output_sub_routing]
                for i in range(4):
                    if objs[i * 2 + 1] in objs[i * 2]:
                        sysex.byte(list(objs[i * 2]).index(objs[i * 2 + 1]))
                    elif objs[i * 2 + 1] == 'None':
                        sysex.byte(len(objs[i * 2]) - 1)
                    else:
                        sysex.byte(127)

            else:
                sysex.byte(127)
                sysex.byte(127)
                sysex.byte(127)
                sysex.byte(127)
            sysex.send()

    def _send_routings(self):
        if self._track_id < 8:
            if self._track is not None:
                for id, type in enumerate([self._track.input_routings,
                 self._track.input_sub_routings,
                 self._track.output_routings,
                 self._track.output_sub_routings]):
                    sysex = LC2Sysex('TRACK_ROUTING_LIST')
                    sysex.byte(self._track_id)
                    sysex.byte(id)
                    sysex.byte(min(12, len(type)))
                    for i in range(12):
                        if i < len(type):
                            sysex.trim(type[i], 10)
                        else:
                            sysex.ascii(' ')

                    sysex.send()

            else:
                for i in range(4):
                    sysex = LC2Sysex('TRACK_ROUTING_LIST')
                    sysex.byte(self._track_id)
                    sysex.byte(i)
                    sysex.byte(0)
                    for j in range(12):
                        sysex.ascii('')

                    sysex.send()

    def _on_selected_device_changed(self):
        if self._track is not None:
            if hasattr(self._track, 'view'):
                self._device.set_device(self._track.view.selected_device)
            else:
                self._device.set_device(None)
        else:
            self._device.set_device(None)
        name = ''
        if self._track is not None:
            if self._track.view.selected_device is not None:
                name = self._track.view.selected_device.name
        sysex = LC2Sysex('TRACK_DEVICE_NAME')
        sysex.byte(self._track_id)
        sysex.ascii(name)
        sysex.send()

    def set_device_controls(self, controls):
        self._device.set_parameter_controls(controls)

    def set_device_bank_controls(self, up, down):
        self._device.set_bank_controls(up, down)

    def _on_track_name_changed(self):
        ChannelStripComponent._on_track_name_changed(self)
        self._send_state()

    def _on_color_changed(self):
        self._send_state()

    def _on_devices_changed(self):
        self._send_devices()

    def _send_state(self):
        if hasattr(self, '_get_offset'):
            offsets = self._get_offset()
            if self._track_id < offsets[2]:
                has_track = 0
                if self._track is not None and self._track in self.song().tracks:
                    has_track = 1
                    if self._track.has_midi_input:
                        has_track = 2
                sysex = LC2Sysex('TRACK')
                sysex.byte(self._track_id)
                sysex.byte(has_track)
                sysex.ascii(self._track is not None and self._track.name or '')
                sysex.rgb(self._track is not None and self._track.color or 0)
                if self._track in self.song().tracks:
                    sysex.ascii(str(list(self.song().tracks).index(self._track) + 1))
                elif self._track in self.song().return_tracks:
                    sysex.ascii(chr(list(self.song().return_tracks).index(self._track) + 65))
                else:
                    sysex.ascii(' ')
                sysex.send()
                self._send_devices()

    def _send_devices(self):
        if hasattr(self, '_get_offset'):
            offsets = self._get_offset()
            if self._track_id < 8 and self._track_id < offsets[2]:
                sysex = LC2Sysex('TRACK_DEVICES')
                sysex.byte(self._track_id)
                if self._track is not None:
                    sysex.byte(min(8, len(self._track.devices)))
                else:
                    sysex.byte(0)
                for i in range(8):
                    if self._track is not None:
                        if i < len(self._track.devices):
                            name = unicode(self._track.devices[i].name)
                        else:
                            name = ''
                    else:
                        name = ''
                    sysex.ascii(name)

                sysex.send()

    def playing_position(self):
        if self.is_enabled():
            if self._track is not None and self._track in self.song().visible_tracks:
                idx = self._track.playing_slot_index
            else:
                idx = -3
            if idx > -1:
                clip = self._track.clip_slots[idx].clip
                if clip is not None:
                    val = abs(int((clip.playing_position - clip.loop_start) / (clip.loop_end - clip.loop_start) * 127))
                    return val > 127 and 127 or val
                else:
                    return 0
            else:
                return 0

    def track_meters(self):
        if self._track is not None:
            if self._track.has_audio_output:
                l = int(self._track.output_meter_left * 127)
                r = int(self._track.output_meter_right * 127)
            else:
                l = 0
                r = 0
            return [l, r]
        else:
            return [0, 0]

    def update(self):
        ChannelStripComponent.update(self)
        if self._allow_updates:
            if self.is_enabled():
                if self._track in self.song().tracks:
                    self._on_monitor_changed()
                self._on_selected_device_changed()
                self._on_monitor_changed()
                self._send_state()
        else:
            self._update_requests += 1

    def select_device(self, id):
        if self._track is not None:
            if id < len(self._track.devices):
                self.song().view.select_device(self._track.devices[id])

    def device_bank(self, ud):
        if self._track is not None:
            self._device.bank(ud)

    def _on_cf_assign_changed(self):
        if self.is_enabled() and self._crossfade_toggle != None:
            if self._track != None and (self._track in self.song().tracks or self._track in self.song().return_tracks):
                self._crossfade_toggle.send_value(self._track.mixer_device.crossfade_assign)
            else:
                self._crossfade_toggle.send_value(1)

    def set_send_control(self, control):
        self._send_control = control
        self.set_send_controls(tuple([control] + [ None for i in range(11) ]))

    def select_send(self, id):
        controls = [ None for i in range(12) ]
        controls[id] = self._send_control
        self.set_send_controls(tuple(controls))

    def set_routing(self, type, val):
        return
        if self._track is not None:
            types = ['current_input_routing',
             'current_input_sub_routing',
             'current_output_routing',
             'current_output_sub_routing']
            vals = [self._track.input_routings,
             self._track.input_sub_routings,
             self._track.output_routings,
             self._track.output_sub_routings]
            if type < len(types):
                if val < len(vals[type]):
                    if getattr(self._track, types[type]) != vals[type][val]:
                        setattr(self._track, types[type], vals[type][val])

    def select(self):
        if self._track is not None:
            self.song().view.selected_track = self._track