#Embedded file name: /Applications/Ableton Live 8.app/Contents/App-Resources/MIDI Remote Scripts/QuNeo/SpecialSessionComponent.py
import Live
from _Framework.EncoderElement import EncoderElement
from _Framework.SessionComponent import SessionComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.SliderElement import SliderElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from ConfigurableButtonElement import ConfigurableButtonElement
from MIDI_Map import *

class SpecialSessionComponent(SessionComponent):
    __module__ = __name__

    def __init__(self, num_tracks, num_scenes, parent):
        SessionComponent.__init__(self, num_tracks, num_scenes)
        self._parent = parent
        self._slot_launch_button = None
        self._clip_loop_start = None
        self._clip_loop_length = None
        self._slot_step_sequencer_buttons = []
        self._note_up_button = None
        self._note_down_button = None
        self._measure_left_button = None
        self._measure_right_button = None
        self._sequencer_clip = None
        self.scale = CHROMATIC_SCALE
        self.notes = []
        self.key_offset = 7
        self._key_index = 36
        self._loc_offset = 0.0
        self.grid_size = 2.0
        self.loop_up_table = 8
        self._clip_slot = None
        self._clip_notes = None
        self.update_key_index(36)
        self.update_measure_offset(0.0)

    def disconnect(self):
        SessionComponent.disconnect(self)
        self._parent = None
        self._sequencer_clip = None
        if self._slot_launch_button != None:
            self._slot_launch_button.remove_value_listener(self._slot_launch_value)
            self._slot_launch_button = None
        if self._clip_loop_start != None:
            self._clip_loop_start.remove_value_listener(self._slot_launch_loop_value)
            self._clip_loop_start = None
        if self._slot_step_sequencer_buttons != None:
            for button in self._slot_step_sequencer_buttons:
                button.remove_value_listener(self._slot_step_sequencer_value)

            self._slot_step_sequencer_buttons = None
        if self._note_up_button != None:
            self._note_up_button.remove_value_listener(self._note_up_value)
            self._note_up_button = None
        if self._note_down_button != None:
            self._note_down_button.remove_value_listener(self._note_down_value)
            self._note_down_button = None

    def create_note(self, value, loc):
        if value:
            x = (value,
             loc,
             0.25,
             127,
             False)
        else:
            None
        return x

    def set_slot_launch_button(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._slot_launch_button != button:
                if self._slot_launch_button != None:
                    self._slot_launch_button.remove_value_listener(self._slot_launch_value)
                self._slot_launch_button = button
                self._slot_launch_button != None and self._slot_launch_button.add_value_listener(self._slot_launch_value)
            self.update()

    def set_seq_note_offset(self, up_button, down_button):
        if not (up_button == None or isinstance(up_button, ButtonElement)):
            raise AssertionError
            if not (down_button == None or isinstance(down_button, ButtonElement)):
                raise AssertionError
                if self._note_up_button != None:
                    self._note_up_button.remove_value_listener(self._note_up_value)
                self._note_up_button = up_button
                if self._note_up_button != None:
                    self._note_up_button.add_value_listener(self._note_up_value)
                self._note_down_button != None and self._note_down_button.remove_value_listener(self._note_down_value)
            self._note_down_button = down_button
            self._note_down_button != None and self._note_down_button.add_value_listener(self._note_down_value)
        self.update()

    def set_seq_measure_offset(self, left_button, right_button):
        if not (left_button == None or isinstance(left_button, ButtonElement)):
            raise AssertionError
            if not (right_button == None or isinstance(right_button, ButtonElement)):
                raise AssertionError
                if self._measure_left_button != None:
                    self._measure_left_button.remove_value_listener(self._measure_left)
                self._measure_left_button = left_button
                if self._measure_left_button != None:
                    self._measure_left_button.add_value_listener(self._measure_left)
                self._measure_right_button != None and self._measure_right_button.remove_value_listener(self._measure_right)
            self._measure_right_button = right_button
            self._measure_right_button != None and self._measure_right_button.add_value_listener(self._measure_right)
        self.update()

    def clear_led(self):
        if self._slot_step_sequencer_buttons != None:
            for button in self._slot_step_sequencer_buttons:
                button.count = 0
                button.note_on()

    def update_key_index(self, value):
        if value != None:
            new_value = value
            if new_value < 0.0 and new_value > 127.0:
                new_value = 0.0
            elif new_value > 127.0:
                new_value = 127.0
            else:
                new_value
            self._key_index = new_value
            if self._slot_step_sequencer_buttons != None:
                for button in self._slot_step_sequencer_buttons:
                    button.count = 0
                    button.note_on()

            self.clear_led()
            self.update_notes()

    def update_measure_offset(self, value):
        new_value = value
        if new_value < 0.0:
            new_value = 0.0
        elif new_value > 127.0:
            new_value = 127.0
        else:
            new_value
        self._loc_offset = new_value
        self.clear_led()
        self.update_notes()

    def update(self):
        if self.song().view.highlighted_clip_slot != None:
            self._sequencer_clip = self.song().view.highlighted_clip_slot.clip
        else:
            self._sequencer_clip = None

    def _measure_left(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._measure_left_button != None:
                raise AssertionError
                new_key_index = self.is_enabled() and value != 0 and -self.grid_size
                real_key_index = new_key_index + self._loc_offset
                self.update_measure_offset(real_key_index)
            else:
                None

    def _measure_right(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._measure_right_button != None:
                raise AssertionError
                new_key_index = self.is_enabled() and value != 0 and self.grid_size
                real_key_index = new_key_index + self._loc_offset
                self.update_measure_offset(real_key_index)
            else:
                None

    def _note_up_value(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._note_up_button != None:
                raise AssertionError
                if self.is_enabled():
                    new_key_index = value != 0 and -self.key_offset
                    real_key_index = new_key_index + self._key_index
                    real_key_index = real_key_index < 0 and 127
                self.update_key_index(real_key_index)
            else:
                None

    def _note_down_value(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._note_down_button != None:
                raise AssertionError
                if self.is_enabled():
                    new_key_index = value != 0 and self.key_offset
                    real_key_index = new_key_index + self._key_index
                    real_key_index = real_key_index > 127 and 0
                self.update_key_index(real_key_index)
            else:
                None

    def set_clip_loop_start(self, slider):
        if not (slider == None or isinstance(slider, EncoderElement)):
            raise AssertionError
            if self._clip_loop_start != slider:
                if self._clip_loop_start != None:
                    self._clip_loop_start.remove_value_listener(self._slot_launch_loop_value)
                self._clip_loop_start = slider
                self._clip_loop_start != None and self._clip_loop_start.add_value_listener(self._slot_launch_loop_value)
            self.update()

    def set_clip_loop_length(self, slider):
        if not (slider == None or isinstance(slider, EncoderElement)):
            raise AssertionError
            if self._clip_loop_length != slider:
                if self._clip_loop_length != None:
                    self._clip_loop_length.remove_value_listener(self._clip_loop_length_value)
                self._clip_loop_length = slider
                self._clip_loop_length != None and self._clip_loop_length.add_value_listener(self._clip_loop_length_value)
            self.update()

    def set_sequencer_buttons(self, buttons):
        if self._slot_step_sequencer_buttons != buttons:
            if self._slot_step_sequencer_buttons != None:
                for button in self._slot_step_sequencer_buttons:
                    button.remove_value_listener(self._slot_step_sequencer_value)

            self._slot_step_sequencer_buttons = buttons
            if self._slot_step_sequencer_buttons != None:
                for button in self._slot_step_sequencer_buttons:
                    raise isinstance(button, ButtonElement) or AssertionError
                    button.add_value_listener(self._slot_step_sequencer_value, identify_sender=True)

            self.update()

    def update_buttons(self):
        for row in range(64):
            for index in range(len(self.new_clip_notes)):
                if self.new_table[row][1] == self.new_clip_notes[index][0] and self.new_table[row][2] == self.new_clip_notes[index][1]:
                    if self._slot_step_sequencer_buttons != None:
                        for note in self._slot_step_sequencer_buttons:
                            if note._note == self.new_table[row][0]:
                                note.count = 1
                                note.note_on()

                    else:
                        None

    def update_quneo_matrix(self):
        self.new_table = []
        for row in range(8):
            for col in range(8):
                self.new_table.append([CLIP_NOTE_MAP[row][col], self._key_index + self.scale[row], self._loc_offset + col / 4.0])

        self.new_clip_notes = []
        if self._clip_notes != None:
            for note in self._clip_notes:
                if note[0] >= self._key_index and note[0] < self._key_index + self.loop_up_table and note[1] >= self._loc_offset and note[1] < self._loc_offset + self.grid_size:
                    self.new_clip_notes.append([note[0], note[1]])

        self.update_buttons()

    def update_notes(self):
        if self._sequencer_clip != None:
            if self._sequencer_clip.is_midi_clip:
                self._sequencer_clip.select_all_notes()
                note_cache = list(self._sequencer_clip.get_selected_notes())
                self._sequencer_clip.deselect_all_notes()
                if self._clip_notes != note_cache:
                    self._clip_notes = note_cache
            self.update_quneo_matrix()

    def _slot_launch_value(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._slot_launch_button != None:
                raise AssertionError
                if self.is_enabled():
                    (value != 0 or not self._slot_launch_button.is_momentary()) and self.song().view.highlighted_clip_slot != None and self.song().view.highlighted_clip_slot.fire()

    def _slot_launch_loop_value(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._clip_loop_start != None:
                raise AssertionError
                if self.is_enabled():
                    if value != 0:
                        if value > 1:
                            new_value = -0.25
                        else:
                            new_value = 0.25
                        if self.song().view.highlighted_clip_slot != None:
                            if self.song().view.highlighted_clip_slot.clip != None:
                                self.song().view.highlighted_clip_slot.clip.looping != False and self.song().view.highlighted_clip_slot.clip.add_loop_start_listener
                                loop_start_pos = self.song().view.highlighted_clip_slot.clip.loop_start
                                loop_end_pos = self.song().view.highlighted_clip_slot.clip.loop_end
                                loop_length = self.song().view.highlighted_clip_slot.clip.length
                                real_value = loop_start_pos + new_value
                                real_value < 0.0 and None
                            else:
                                self.song().view.highlighted_clip_slot.clip.loop_start = real_value
                    else:
                        None

    def _clip_loop_length_value(self, value):
        if not value in range(128):
            raise AssertionError
            if not self._clip_loop_length != None:
                raise AssertionError
                if self.is_enabled():
                    if value != 0:
                        if value > 1:
                            new_value = -0.25
                        else:
                            new_value = 0.25
                        if self.song().view.highlighted_clip_slot != None:
                            if self.song().view.highlighted_clip_slot.clip != None:
                                self.song().view.highlighted_clip_slot.clip.looping != False and self.song().view.highlighted_clip_slot.clip.add_loop_end_listener
                                loop_end_pos = self.song().view.highlighted_clip_slot.clip.loop_end
                                loop_length = self.song().view.highlighted_clip_slot.clip.length
                                real_value = loop_end_pos + new_value
                                return real_value < 0.25 and None
                            else:
                                self.song().view.highlighted_clip_slot.clip.loop_end = real_value
                    else:
                        None

    def _slot_step_sequencer_value(self, value, sender):
        if not value in range(128):
            raise AssertionError
            if not self._slot_step_sequencer_buttons != None:
                raise AssertionError
                if self.is_enabled() and self._sequencer_clip != None and self._sequencer_clip.is_midi_clip and value != 0:
                    for row in range(8):
                        for col in range(8):
                            if sender._note == STEP_SEQUENCER_MAP[row][col]:
                                sender.count += 1
                                sender.note_on()
                                note_value = self._key_index + self.scale[row]
                                loc_value = self._loc_offset + col / 4.0
                                if self._clip_notes != None:
                                    if sender.count == 1:
                                        self._clip_notes.append(self.create_note(note_value, loc_value))
                                    else:
                                        for note in self._clip_notes:
                                            if note_value == note[0] and loc_value == note[1]:
                                                self._clip_notes.remove(note)

                                    self._sequencer_clip.select_all_notes()
                                    self._sequencer_clip.replace_selected_notes(tuple(self._clip_notes))
                                else:
                                    None

        self.update_notes()

    def set_drum_pad_mode(self, value):
        if value == 0:
            self._parent.log_message('!ST VALUE ' + str(value))
        elif value == 1:
            self._parent.log_message('2ND VALUE ' + str(value))
        else:
            None

    def on_selected_track_changed(self):
        if self._slot_step_sequencer_buttons != None:
            for button in self._slot_step_sequencer_buttons:
                button.count = 0
                button.note_on()

        self.on_device_changed()
        self.update()
        self.update_notes()

    def on_device_changed(self):
        if self.song().view.selected_track.view.selected_device != None:
            self.device = self.song().view.selected_track.view.selected_device
            self.device_name = self.device.class_name
            if self.device_name == 'InstrumentImpulse':
                self._key_index = 60
                self.scale = MAJOR_SCALE
                self.key_offset = 0
                self.loop_up_table = 13
            elif self.device_name == 'DrumGroupDevice':
                self._key_index = 36
                self.scale = CHROMATIC_SCALE
                self.key_offset = 7
                self.loop_up_table = 8
            elif self.device_name == 'Collision':
                self._key_index = 36
                self.scale = CHROMATIC_SCALE
                self.key_offset = 7
                self.loop_up_table = 8
            else:
                self.scale = CHROMATIC_SCALE
                self._key_index = 36
                self.key_offset = 7
                self.loop_up_table = 8
        self.update()
        self.update_notes()