#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Serato/SpecialChanStripComponent.py
from _Framework.ChannelStripComponent import ChannelStripComponent

class SpecialChanStripComponent(ChannelStripComponent):

    def __init__(self):
        ChannelStripComponent.__init__(self)
        self._serato_interface = None
        self._index = -1

    def disconnect(self):
        self._remove_send_listeners()
        if self._track != None:
            self._track.remove_color_listener(self._on_track_color_changed)
            self._track.mixer_device.volume.remove_value_listener(self._on_volume_changed)
            self._track.remove_has_midi_output_listener(self._on_output_type_changed)
        ChannelStripComponent.disconnect(self)
        self._on_volume_changed()
        self._on_mute_changed()
        self._on_arm_changed()
        self._on_send_a_changed()
        self._on_send_b_changed()
        self._on_level_changed()
        self._on_track_name_changed()
        self._on_track_color_changed()
        self._update_track_index()
        self._serato_interface = None

    def set_track(self, track):
        self._remove_send_listeners()
        self._remove_level_listener()
        if self._track != None:
            self._track.remove_color_listener(self._on_track_color_changed)
            self._track.mixer_device.volume.remove_value_listener(self._on_volume_changed)
            self._track.remove_has_midi_output_listener(self._on_output_type_changed)
        ChannelStripComponent.set_track(self, track)
        if self._track != None:
            self._track.add_color_listener(self._on_track_color_changed)
            self._track.mixer_device.volume.add_value_listener(self._on_volume_changed)
            self._track.add_has_midi_output_listener(self._on_output_type_changed)
        self._add_send_listeners()
        self._on_volume_changed()
        self._on_output_type_changed()
        self._update_track_index()

    def set_index(self, index):
        raise index > -1 or AssertionError
        self._index = index
        self.update()
        self._on_send_a_changed()
        self._on_send_b_changed()
        self._on_volume_changed()
        self._on_output_type_changed()
        self._update_track_index()

    def set_serato_interface(self, serato_interface):
        raise serato_interface != None or AssertionError
        self._serato_interface = serato_interface
        self.update()
        self._on_send_a_changed()
        self._on_send_b_changed()
        self._on_volume_changed()
        self._update_track_index()

    def set_track_volume(self, volume):
        if not (0.0 <= volume and volume <= 1.0):
            raise AssertionError
            self._track.mixer_device.volume.value = self._track != None and self._track.mixer_device.volume.is_enabled and volume

    def set_send(self, index, amount):
        if not (0.0 <= amount and amount <= 1.0):
            raise AssertionError
            if self._track != None and len(self._track.mixer_device.sends) > index:
                self._track.mixer_device.sends[index].value = self._track.mixer_device.sends[index].is_enabled and amount

    def is_track_selected(self):
        return self._track == self.song().view.selected_track

    def update(self):
        if self._allow_updates:
            if self.is_enabled():
                self._on_mute_changed()
                self._on_solo_changed()
                self._on_arm_changed()
                self._on_track_name_changed()
                self._on_track_color_changed()
        else:
            self._update_requests += 1

    def _on_sends_changed(self):
        self._remove_send_listeners()
        self._add_send_listeners()

    def _on_mute_changed(self):
        if self._track != self.song().master_track and self._serato_interface != None and self._index > -1:
            value_to_send = 1
            if self._track != None:
                value_to_send = int(not self._track.mute)
            self._serato_interface.PySCA_SetTrackActiveState(self._index + 1, value_to_send)

    def _on_solo_changed(self):
        if self._track != self.song().master_track and self._serato_interface != None and self._index > -1:
            value_to_send = 0
            if self._track != None:
                value_to_send = int(self._track.solo)
            self._serato_interface.PySCA_SetTrackSoloState(self._index + 1, value_to_send)

    def _on_arm_changed(self):
        if (self._track in self.song().tracks or self._track == None) and self._serato_interface != None and self._index > -1:
            value_to_send = 0
            if self._track != None and self._track.can_be_armed:
                value_to_send = int(self._track.arm)
            self._serato_interface.PySCA_SetTrackRecordState(self._index + 1, value_to_send)

    def _on_track_name_changed(self):
        if self._serato_interface != None and self._index > -1:
            name = ''
            if self._track != None:
                name = self._track.name
            self._serato_interface.PySCA_SetTrackLabel(self._index + 1, name)

    def _on_track_color_changed(self):
        if self._serato_interface != None and self._index > -1:
            color = -1
            if self._track != None:
                color = self._track.color
            self._serato_interface.PySCA_SetTrackColor(self._index + 1, color)

    def _on_send_a_changed(self):
        if (self._track in self.song().tracks or self._track == None) and self._serato_interface != None and self._index > -1:
            value_to_send = 0.0
            if self._track != None and len(self._track.mixer_device.sends) > 0:
                value_to_send = self._track.mixer_device.sends[0].value
            self._serato_interface.PySCA_SetTrackSendAState(self._index + 1, value_to_send)

    def _on_send_b_changed(self):
        if (self._track in self.song().tracks or self._track == None) and self._serato_interface != None and self._index > -1:
            value_to_send = 0.0
            if self._track != None and len(self._track.mixer_device.sends) > 1:
                value_to_send = self._track.mixer_device.sends[1].value
            self._serato_interface.PySCA_SetTrackSendBState(self._index + 1, value_to_send)

    def _on_volume_changed(self):
        if self._serato_interface != None:
            if self._track == self.song().master_track:
                self._serato_interface.PySCA_SetMasterGainState(self._track.mixer_device.volume.value)
            elif self._index > -1:
                value_to_send = 0.0
                if self._track != None:
                    value_to_send = self._track.mixer_device.volume.value
                self._serato_interface.PySCA_SetTrackGainState(self._index + 1, value_to_send)

    def _on_output_type_changed(self):
        self._remove_level_listener()
        self._add_level_listener()
        self._on_level_changed()

    def _on_level_changed(self):
        if self._serato_interface != None:
            level = 0.0
            if self._track != None:
                if self._track.has_midi_output:
                    level = self._track.output_meter_level
                elif self._track.has_audio_output:
                    level = max(self._track.output_meter_left, self._track.output_meter_right)
            if self._track == self.song().master_track:
                self._serato_interface.PySCA_SetMasterLevel(-1, level)
            elif self._index > -1:
                self._serato_interface.PySCA_SetTrackLevel(self._index + 1, level)

    def _remove_send_listeners(self):
        if self._track != None:
            send_callbacks = (self._on_send_a_changed, self._on_send_b_changed)
            for index in range(2):
                if index < len(self._track.mixer_device.sends):
                    send = self._track.mixer_device.sends[index]
                    if send.value_has_listener(send_callbacks[index]):
                        send.remove_value_listener(send_callbacks[index])

    def _add_send_listeners(self):
        if self._track != None:
            send_callbacks = (self._on_send_a_changed, self._on_send_b_changed)
            for index in range(2):
                if index < len(self._track.mixer_device.sends):
                    self._track.mixer_device.sends[index].add_value_listener(send_callbacks[index])
                    send_callbacks[index]()

    def _remove_level_listener(self):
        if self._track != None:
            if self._track.has_audio_output:
                if self._track.output_meter_right_has_listener(self._on_level_changed):
                    self._track.remove_output_meter_right_listener(self._on_level_changed)
                if self._track.output_meter_left_has_listener(self._on_level_changed):
                    self._track.remove_output_meter_left_listener(self._on_level_changed)
            elif self._track.output_meter_level_has_listener(self._on_level_changed):
                self._track.remove_output_meter_level_listener(self._on_level_changed)

    def _add_level_listener(self):
        if self._track != None:
            if self._track.has_audio_output:
                if not self._track.output_meter_right_has_listener(self._on_level_changed):
                    self._track.add_output_meter_right_listener(self._on_level_changed)
                if not self._track.output_meter_left_has_listener(self._on_level_changed):
                    self._track.add_output_meter_left_listener(self._on_level_changed)
            elif not self._track.output_meter_level_has_listener(self._on_level_changed):
                self._track.add_output_meter_level_listener(self._on_level_changed)

    def _update_track_index(self):
        if self._serato_interface != None and self._index > -1:
            self._serato_interface.PySCA_SetTrackNumber(self._index + 1, self._identifier())

    def _encode_track_identifier(self, identifier):
        raise len(identifier) <= 4 or AssertionError
        result = 0
        for index in range(min(4, len(identifier))):
            raise identifier[index].isdigit() or identifier[index].isupper() or AssertionError
            byte = ord(identifier[index])
            result += byte << (3 - index) * 8

        return result

    def _identifier(self):
        track_id = ''
        tracks = self.song().tracks
        returns = self.song().return_tracks
        if self._track != None:
            if self._track in tracks:
                track_id = str(list(tracks).index(self._track) + 1)
            elif self._track in returns:
                track_id = str(chr(ord('A') + list(returns).index(self._track)))
            elif self._track == self.song().master_track:
                track_id = 'M'
        return self._encode_track_identifier(track_id)