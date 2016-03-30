#Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/LiveControl_2_1_31/LC2SessionComponent.py
from _Framework.SessionComponent import SessionComponent
from _Framework.SceneComponent import SceneComponent
from LC2SceneComponent import LC2SceneComponent
from LC2ClipSlotComponent import LC2ClipSlotComponent
from LC2ChannelStripComponent import LC2ChannelStripComponent
from LC2SessionSnapshot import LC2SessionBank
from LC2Sysex import LC2Sysex, LC2SysexParser
INITIAL_SCROLLING_DELAY = 5
INTERVAL_SCROLLING_DELAY = 1

class LC2SessionComponent(SessionComponent):

    def __init__(self, num_tracks, num_scenes):
        self._scene_count = LC2Sysex.l9() and -1 or 0
        self._num_tracks = num_tracks
        self._height = num_scenes
        self._width = num_tracks
        self._snapshot_bank = LC2SessionBank()
        SessionComponent.__init__(self, num_tracks, num_scenes)
        LC2SceneComponent.set_get_offsets(self._get_offset)
        LC2ChannelStripComponent.set_get_offsets(self._get_offset)
        LC2ClipSlotComponent.set_get_offsets(self._get_offset)
        LC2ChannelStripComponent.set_playing_slot_changed(self._playing_slot_changed)

    def set_sequencer(self, seq):
        self._sequencer = seq

    def _playing_slot_changed(self, index, name):
        self._snapshot_bank.playing_slot_changed(name, index)

    def send_size(self):
        sysex = LC2Sysex('SET_WIDTH')
        sysex.byte(len(self.tracks_to_use()))
        if len(self.song().visible_tracks) < 8:
            sysex.byte(len(self.song().visible_tracks))
            self._width = len(self.song().visible_tracks)
        else:
            sysex.byte(8)
            self._width = 8
        if len(self.song().scenes) < 12:
            sysex.byte(len(self.song().scenes))
            self._height = len(self.song().scenes)
        else:
            sysex.byte(12)
            self._height = 12
        sysex.send()

    def height(self):
        return self._height

    def width(self):
        return self._width

    def _send_init(self):
        for scene in self._scenes:
            scene._send_init()

        self.send_offsets()
        self.send_sends()

    def disconnect(self):
        self._sequencer = None
        LC2SceneComponent.release_attributes()
        LC2ChannelStripComponent.release_attributes()
        LC2ClipSlotComponent.release_attributes()
        SessionComponent.disconnect(self)

    def _create_scene(self, num_tracks = None):
        if self._scene_count == -1:
            sc = SceneComponent(self._num_tracks, self.tracks_to_use, self._scene_count)
        else:
            sc = LC2SceneComponent(self._num_tracks, self.tracks_to_use, self._scene_count)
        self._scene_count += 1
        return sc

    def handle_sysex(self, sysex):
        cmds = [self._launch_clip,
         self._launch_scene,
         self._jump_clip,
         self._set_rows,
         self._set_cols,
         self._track_stop,
         self._stop_all,
         self._set_size,
         self._select_clip,
         self._snapshot,
         self._select_send]
        if sysex[0] < len(cmds):
            cmds[sysex[0]](LC2SysexParser(sysex[1:]))

    def _select_send(self, sysex):
        tid, send = sysex.parse('bb')
        LC2Sysex.log_message(str(tid) + ' ' + str(send))
        self._mixer.channel_strip(tid).select_send(send)

    def _snapshot(self, sysex):
        id, save = sysex.parse('bb')
        if save:
            self._snapshot_bank.add(id)
        else:
            self._snapshot_bank.load(id)

    def _set_size(self, sysex):
        self._height, self._width = sysex.parse('bb')
        self._mixer._send_init()
        self._send_init()
        self.send_offsets()
        self._do_show_highlight()

    def _stop_all(self, sysex):
        self.song().stop_all_clips()

    def _get_offset(self):
        return (self._track_offset,
         self._scene_offset,
         self._width,
         self._height)

    def _set_rows(self, sysex):
        u, l = sysex.parse('bb')
        self.set_offsets(self._track_offset, int(round((127 - u) / 127.0 * len(self.song().scenes), 0)))

    def _set_cols(self, sysex):
        u, l = sysex.parse('bb')
        self.set_offsets(int(round(l / 127.0 * len(self.tracks_to_use()), 0)), self._scene_offset)

    def on_scene_list_changed(self):
        SessionComponent.on_scene_list_changed(self)
        self.send_size()
        self.send_offsets()

    def on_track_list_changed(self):
        SessionComponent.on_track_list_changed(self)
        self.send_size()
        self.send_offsets()
        self.send_sends()

    def send_sends(self):
        sysex = LC2Sysex('RETURN_NAMES')
        sysex.byte(len(self.song().return_tracks))
        for i in range(12):
            if i < len(self.song().return_tracks):
                sysex.trim(self.song().return_tracks[i].name, 15)
            else:
                sysex.ascii('')

        sysex.send()

    def send_offsets(self):
        sysex = LC2Sysex('SET_OFFSETS')
        sc = len(self.song().scenes)
        diff = float(self._height) / float(sc)
        st = float(self.scene_offset()) / float(sc)
        if self._height > sc:
            diff = 1
            st = 0
        sysex.byte(min(127, 127 - int((st + diff) * 127)))
        sysex.byte(min(127, 127 - int(st * 127)))
        tc = len(self.tracks_to_use())
        diff = float(self._width) / float(tc)
        st = float(self._track_offset) / float(tc)
        if self._width > tc:
            diff = 1
            st = 0
        sysex.byte(int(round(st * 127, 0)))
        sysex.byte(int(round((st + diff) * 127, 0)))
        sysex.send()

    def _track_stop(self, sysex):
        track_index = sysex.parse('b') + self._track_offset
        tracks = self.tracks_to_use()
        if track_index in range(len(tracks)) and tracks[track_index] in self.song().tracks:
            tracks[track_index].stop_all_clips()

    def _select_clip(self, sysex):
        x, y, state = sysex.parse('bbb')
        if state and self._sequencer is not None:
            if x + self._track_offset < len(self.tracks_to_use()):
                if y + self._scene_offset < len(self.song().scenes):
                    slot = self.tracks_to_use()[x + self._track_offset].clip_slots[y + self._scene_offset]
                    self._sequencer.select(slot)
                    if slot is not None:
                        if slot.has_clip:
                            self.song().view.selected_track = slot.canonical_parent
                            self.song().view.selected_scene = self.song().scenes[list(slot.canonical_parent.clip_slots).index(slot)]

    def _launch_clip(self, sysex):
        x, y, state = sysex.parse('bbb')
        if state == 1:
            self.scene(y).clip_slot(x).launch()

    def _launch_scene(self, sysex):
        id = sysex.parse('b')
        self.scene(id).fire()

    def _jump_clip(self, sysex):
        id = sysex.parse('b') + self._track_offset
        if id < len(self.song().visible_tracks):
            if self.tracks_to_use()[id].is_foldable:
                self.tracks_to_use()[id].fold_state = not self.tracks_to_use()[id].fold_state
            else:
                slot_idx = self.song().visible_tracks[id].playing_slot_index
                if slot_idx > -1:
                    self.set_offsets(self._track_offset, slot_idx)
                    self.send_offsets()

    def _bank_up(self):
        if LC2Sysex.l9():
            SessionComponent._bank_up(self)
            self.send_offsets()
            if self.scene_offset() == 0:
                self._bank_up_button.turn_off()

    def _bank_down(self):
        if LC2Sysex.l9():
            if len(self.song().scenes) > self.scene_offset() + self.height():
                SessionComponent._bank_down(self)
                self.send_offsets()
            LC2Sysex.log_message(str(len(self.song().scenes)) + ' ' + str(self.scene_offset() + self.height()))
            if len(self.song().scenes) == self.scene_offset() + self.height():
                self._bank_down_button.turn_off()

    def _bank_right(self):
        if LC2Sysex.l9():
            if len(self.tracks_to_use()) > self.track_offset() + self.width():
                SessionComponent._bank_right(self)
                self.send_offsets()
            if len(self.tracks_to_use()) == self.track_offset() + self.width():
                self._bank_right_button.turn_off()

    def _bank_left(self):
        if LC2Sysex.l9():
            if self.track_offset() > 0:
                SessionComponent._bank_left(self)
                self.send_offsets()
            else:
                self._bank_left_button.turn_off()

    def _bank_up_value(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._bank_up_button != None:
                raise AssertionError
                if self.is_enabled():
                    button_is_momentary = self._bank_up_button.is_momentary()
                    if button_is_momentary:
                        self._scroll_up_ticks_delay = value != 0 and INITIAL_SCROLLING_DELAY
                    else:
                        self._scroll_up_ticks_delay = -1
                not self._is_scrolling() and (value is not 0 or not button_is_momentary) and self.set_offsets(self._track_offset, min(len(self.song().scenes) - self.height(), self._scene_offset + self.height()))
                self.send_offsets()

    def _bank_down_value(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._bank_down_button != None:
                raise AssertionError
                if self.is_enabled():
                    button_is_momentary = self._bank_down_button.is_momentary()
                    if button_is_momentary:
                        self._scroll_down_ticks_delay = value != 0 and INITIAL_SCROLLING_DELAY
                    else:
                        self._scroll_down_ticks_delay = -1
                not self._is_scrolling() and (value is not 0 or not button_is_momentary) and self.set_offsets(self._track_offset, max(0, self._scene_offset - self.height()))
                self.send_offsets()

    def _bank_left_value(self, value):
        if self._track_offset > 0:
            SessionComponent._bank_left_value(self, value)
            self.send_offsets()
        else:
            self._bank_left_button.turn_off()

    def _bank_right_value(self, value):
        if self._track_offset < self._width and self._width + self._track_offset < len(self.tracks_to_use()) or self._width < len(self.tracks_to_use()) and self._width + self._track_offset < len(self.tracks_to_use()):
            SessionComponent._bank_right_value(self, value)
            self.send_offsets()
        else:
            self._bank_right_button.turn_off()