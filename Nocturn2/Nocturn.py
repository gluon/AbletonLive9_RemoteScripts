#
# Copyright (C) 2009 Guillermo Ruiz Troyano
#
# This file is part of Nocturn Remote Script for Live (Nocturn RS4L).
#
#    Nocturn RS4L is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Nocturn RS4L is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Nocturn RS4L.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact info:
#    Guillermo Ruiz Troyano, ruiztroyano@gmail.com
#

import Live
import MidiRemoteScript
from consts import *
from MixerController import MixerController
from DeviceController import DeviceController
from SceneController import SceneController
from PlayingController import PlayingController
class Nocturn:
	__module__ = __name__
	__doc__ = 'Automap script for the Novation Nocturn.'

	def __init__(self, c_instance):
		self._c_instance = c_instance
		self._base_track_index = 0
		self.mixer_controller = MixerController(self)
		self.device_controller = DeviceController(self)
		self.scene_controller = SceneController(self)
		self.playing_controller = PlayingController(self)
		self._components = [ self.mixer_controller, self.device_controller,
		                     self.scene_controller, self.playing_controller ]
		self.song().add_visible_tracks_listener(self._on_visible_tracks_changed)


	def disconnect(self):
		if (self.song().visible_tracks_has_listener(self._on_visible_tracks_changed)):
			self.song().remove_visible_tracks_listener(self._on_visible_tracks_changed)
		for c in self._components:
			c.disconnect()

	def application(self):
		return Live.Application.get_application()

	def song(self):
		return self._c_instance.song()
	
	def show_message(self, message):
		self._c_instance.show_message(message)
		
	def log(self, message):
	    self._c_instance.log_message(message)

	def suggest_input_port(self):
		return 'Automap MIDI'

	def suggest_output_port(self):
		return 'Automap MIDI'

	def can_lock_to_devices(self):
		return True

	def lock_to_device(self, device):
		if (self.device_controller):
			self.device_controller.lock_to_device(device)
		
	def unlock_from_device(self, device):
		if (self.device_controller):
			self.device_controller.unlock_from_device(device)

	def set_appointed_device(self, device):
		if (self.device_controller):
			self.device_controller.set_appointed_device(device)

	def toggle_lock(self):
	    self._c_instance.toggle_lock()

	def suggest_map_mode(self, cc_no, channel):
		return Live.MidiMap.MapMode.absolute

	def supports_pad_translation(self):
		return False

	def instance_identifier(self):
		return self._c_instance.instance_identifier()

	def connect_script_instances(self, instanciated_scripts):
		pass

	def request_rebuild_midi_map(self):
		self._c_instance.request_rebuild_midi_map()

	def send_midi(self, midi_event_bytes):
		self._c_instance.send_midi(midi_event_bytes)

	def refresh_state(self):
		self.request_rebuild_midi_map()

	def build_midi_map(self, midi_map_handle):
		script_handle = self._c_instance.handle()
		for c in self._components:
			c.build_midi_map(script_handle, midi_map_handle)

	def update_display(self):
		for c in self._components:
			c.update_display()

	def receive_midi(self, midi_bytes):
		if (((midi_bytes[0] & 240) == NOTE_ON_STATUS) or ((midi_bytes[0] & 240) == NOTE_OFF_STATUS)):
			channel = (midi_bytes[0] & 15)
			note = midi_bytes[1]
			velocity = midi_bytes[2]
			for c in self._components:
				c.receive_note(channel, note, velocity)
		elif ((midi_bytes[0] & 240) == CC_STATUS):
			channel = (midi_bytes[0] & 15)
			cc_no = midi_bytes[1]
			cc_value = midi_bytes[2]
			for c in self._components:
				c.receive_midi_cc(channel, cc_no, cc_value)
		elif ((midi_bytes[0] & 240) == PB_STATUS):
			channel = (midi_bytes[0] & 15)
			pb_value = (midi_bytes[2]<<7)+midi_bytes[1]
			for c in self._components:
				c.receive_pitchbend(channel, pb_value)

	
	def bank_tracks(self):
		end = min(self._base_track_index+NUM_STRIPS,len(self.song().visible_tracks));
		return self.song().visible_tracks[self._base_track_index:end]
	
	def bank_clip_slots(self):
		scn_index = list(self.song().scenes).index(self.song().view.selected_scene)
		tracks = self.bank_tracks()
		slots = list()
		for t in tracks:
			slots.append(t.clip_slots[scn_index])
		return slots
		
	def track_bank_index(self):
		return self._base_track_index/NUM_STRIPS
	
	def set_track_bank(self, index):
		index *= NUM_STRIPS
		old_index = self._base_track_index
		self._base_track_index = (index < len(self.song().visible_tracks)) and index
		if (self._base_track_index != old_index):
			for c in self._components:
				c.on_selected_track_bank()


	def _on_visible_tracks_changed(self):
		self.set_track_bank(self.track_bank_index())

