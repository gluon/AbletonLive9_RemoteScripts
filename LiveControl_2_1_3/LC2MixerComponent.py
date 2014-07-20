#Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/LiveControl_2_13/LC2MixerComponent.py
from _Framework.MixerComponent import MixerComponent
from LC2ChannelStripComponent import LC2ChannelStripComponent
from LC2Sysex import LC2Sysex, LC2SysexParser

class LC2MixerComponent(MixerComponent):

    def __init__(self, num_tracks):
        self._meter_cache = [ 0 for i in range(num_tracks * 2 + 2) ]
        self._pos_cache = [ 0 for i in range(num_tracks) ]
        MixerComponent.__init__(self, num_tracks)
        self._register_timer_callback(self._update_lemur)
        self._selected_strip = None

    def tracks_to_use(self):
        return tuple(list(self.song().visible_tracks) + list(self.song().return_tracks))

    def disconnect(self):
        self._unregister_timer_callback(self._update_lemur)
        MixerComponent.disconnect(self)

    def _create_strip(self):
        return LC2ChannelStripComponent(len(self._channel_strips))

    def handle_sysex(self, sysex):
        cmds = [self._select_device,
         self._device_bank,
         self._set_routing,
         self._select_track]
        if sysex[0] < len(cmds):
            cmds[sysex[0]](LC2SysexParser(sysex[1:]))

    def _select_track(self, sysex):
        id = sysex.parse('b')
        if id < len(self._channel_strips):
            self.channel_strip(id).select()

    def _set_routing(self, sysex):
        tid, type, val = sysex.parse('bbb')
        if tid < 8:
            self.channel_strip(tid).set_routing(type, val)

    def _device_bank(self, sysex):
        ch, ud = sysex.parse('bb')
        if ch < len(self._channel_strips):
            self.channel_strip(ch).device_bank(ud)

    def _select_device(self, sysex):
        tr, id = sysex.parse('bb')
        LC2Sysex.log_message('device select:' + str(tr) + ' ' + str(id))
        if tr < len(self._channel_strips):
            self.channel_strip(tr).select_device(id)

    def _send_init(self):
        for tr in self._channel_strips:
            tr._send_init()

    def _update_lemur(self):
        if self.is_enabled():
            update = 0
            sysex = LC2Sysex('CLIP_POSITION')
            update2 = 0
            sysex2 = LC2Sysex('TRACK_METERS')
            for id, tr in enumerate(self._channel_strips):
                pos = tr.playing_position()
                sysex.byte(pos)
                meter = tr.track_meters()
                sysex2.byte(meter[0])
                sysex2.byte(meter[1])
                if self._meter_cache[id * 2] != meter[0]:
                    self._meter_cache[id * 2] = meter[0]
                    update2 = 1
                if self._meter_cache[id * 2 + 1] != meter[1]:
                    self._meter_cache[id * 2 + 1] = meter[1]
                    update2 = 1
                if self._pos_cache[id] != pos:
                    self._pos_cache[id] = pos
                    update = 1

            mmeter = self._master_strip.track_meters()
            sysex2.byte(mmeter[0])
            sysex2.byte(mmeter[1])
            if self._meter_cache[16] != mmeter[0]:
                self._meter_cache[16] = mmeter[0]
                update2 = 1
            if self._meter_cache[17] != mmeter[1]:
                self._meter_cache[17] = mmeter[1]
                update2 = 1
            if update:
                sysex.send()
            if update2:
                sysex2.send()