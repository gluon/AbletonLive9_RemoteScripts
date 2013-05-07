#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/NoteEditorComponent.py
from __future__ import with_statement
import Live
GridQuantization = Live.Clip.GridQuantization
from contextlib import contextmanager
from functools import partial
from _Framework.SubjectSlot import subject_slot
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.Util import sign, product, in_range, clamp
from _Framework import Task, Defaults
from LoopSelectorComponent import create_clip_in_selected_slot, Paginator
from MatrixMaps import PAD_FEEDBACK_CHANNEL
STEP_PARAM_NAMES = (' ', ' ', ' ', ' ', ' ', '<Nudge>', 'Note Length', 'Velocity')
STEP_SEQ_WIDTH = 8
STEP_SEQ_HEIGHT = 4
STEP_SEQ_SIZE = STEP_SEQ_WIDTH * STEP_SEQ_HEIGHT
STEP_SEQ_OVERALL_LENGTH = STEP_SEQ_SIZE * 4.0
STEP_STATE_INITIAL = -1
STEP_STATE_DONT_DELETE = 0
STEP_STATE_ALLOW_DELETE = 1
STEP_STATE_ADDED_MUTED = 2
DEFAULT_VELOCITY = 100
QUANTIZATION_FACTOR = 24
BEAT_TIME_EPSILON = 1.0000000000000006e-05
QUANTIZATION_LIST = [2.0,
 3.0,
 4.0,
 6.0,
 8.0,
 12.0,
 16.0,
 24.0]
CLIP_VIEW_GRID_LIST = tuple(product([GridQuantization.g_thirtysecond,
 GridQuantization.g_sixteenth,
 GridQuantization.g_eighth,
 GridQuantization.g_quarter], [True, False]))
CLIP_LENGTH_LIST = [2.0,
 4.0,
 4.0,
 8.0,
 8.0,
 16.0,
 16.0,
 32.0]

def color_for_note(note):
    velocity = note[3]
    muted = note[4]
    if not muted:
        if velocity == 127:
            return 'NoteEditor.StepFullVelocity'
        elif velocity >= 100:
            return 'NoteEditor.StepHighVelocity'
        else:
            return 'NoteEditor.Step'
    else:
        return 'NoteEditor.StepMuted'


def most_significant_note(notes):
    return max(notes, key=lambda n: n[3])


MAX_CLIP_LENGTH = 100000000
RELATIVE_OFFSET = 0.25

class TimeStep(object):
    """
    A fixed step (time range) for the step sequencer
    """

    def __init__(self, start, length, clip_start = 0.0, clip_end = MAX_CLIP_LENGTH, *a, **k):
        super(TimeStep, self).__init__(*a, **k)
        self.start = start
        self.length = length
        self.clip_start = clip_start
        self.clip_end = clip_end

    @property
    def offset(self):
        return self.length * RELATIVE_OFFSET

    def left_boundary(self):
        return max(0, self.start - self.offset + BEAT_TIME_EPSILON)

    def includes_note(self, note):
        return self.includes_time(note[1])

    def filter_notes(self, notes):
        return filter(self.includes_note, notes)

    def clamp(self, time, extra_time = 0.0):
        return clamp(time + extra_time, self.left_boundary(), self.start - self.offset + self.length - BEAT_TIME_EPSILON)

    def includes_time(self, time):
        return in_range(time - self.start + self.offset, 0, self.length)

    def connected_time_ranges(self):
        return [(self.start - self.offset, self.length)]


class LoopingTimeStep(TimeStep):

    def clamp(self, time, extra_time = 0.0):
        result = clamp(self._looped_time(time, extra_time), self.left_boundary(), self.start - self.offset + self.length - BEAT_TIME_EPSILON)
        if result < self.clip_start:
            return result - self.clip_start + self.clip_end
        else:
            return result

    def connected_time_ranges(self):
        """
        Returns a list of (start_time, length) ranges representing the
        step in terms of continuous time ranges that can be used by
        functions like clip.remove_notes
        """
        if self.start - self.offset < self.clip_start:
            return [(self.clip_start, self.length - self.offset), (self.clip_end - self.offset, self.offset)]
        else:
            return [(self.start - self.offset, self.length)]

    def _looped_time(self, time, extra_time = 0.0):
        if in_range(time, self.clip_end - self.offset, self.clip_end):
            time = time - self.clip_end + self.clip_start
        return time + extra_time

    def includes_time(self, time):
        return in_range(self._looped_time(time) + self.offset - self.start, 0, self.length) and in_range(time, self.clip_start, self.clip_end)


class NoteEditorComponent(ControlSurfaceComponent, Paginator):

    def __init__(self, clip_creator = None, playhead = None, *a, **k):
        super(NoteEditorComponent, self).__init__(*a, **k)
        self.loop_steps = False
        self._selected_page_point = 0
        self._page_index = 0
        self._clip_creator = clip_creator
        self._matrix = None
        self._sequencer_clip = None
        self._step_colors = ['NoteEditor.StepEmpty'] * STEP_SEQ_SIZE
        self._note_settings_layer = None
        self._top_data_sources = map(DisplayDataSource, STEP_PARAM_NAMES)
        self._bottom_data_sources = [ DisplayDataSource() for _ in xrange(8) ]
        self._show_settings_task = self._tasks.add(Task.sequence(Task.wait(Defaults.MOMENTARY_DELAY), Task.run(self._show_settings)))
        self._show_settings_task.kill()
        self._full_velocity_button = None
        self._mute_button = None
        self._full_velocity = False
        self._velocity_offset = 0
        self._length_offset = 0
        self._nudge_offset = 0
        self._attribute_deltas = [ None for _ in xrange(3) ]
        self._pressed_steps = []
        self._modified_steps = []
        self._pressed_step_callback = None
        self._quantization_buttons = []
        self._quantization_button_slots = self.register_slot_manager()
        self._modify_task = self._tasks.add(Task.run(self._do_modification))
        self._modify_task.kill()
        self._modify_all_notes_enabled = False
        self._step_tap_tasks = dict([ ((x, y), self._tasks.add(Task.sequence(Task.wait(Defaults.MOMENTARY_DELAY), Task.run(partial(self._trigger_modification, (x, y), done=True))))) for x, y in product(xrange(STEP_SEQ_WIDTH), xrange(STEP_SEQ_HEIGHT)) ])
        for task in self._step_tap_tasks.itervalues():
            task.kill()

        self._clip_notes = []
        self._note_index = 36
        self._triplet_factor = 1.0
        self._set_quantization_index(3)
        self._playhead = playhead
        self._playhead_notes = range(92, 100) + range(84, 92) + range(76, 84) + range(68, 76)
        self._playhead_triplet_notes = range(92, 98) + range(84, 90) + range(76, 82) + range(68, 74)
        with self._playhead_update_guard():
            self._update_full_playhead()

    @property
    def page_index(self):
        return self._page_index

    @property
    def page_length(self):
        return STEP_SEQ_SIZE * self._get_step_length() * self._triplet_factor

    def select_page_in_point(self, point):
        if not self._pressed_steps and not self._modified_steps:
            self._selected_page_point = point
            index = int(point / self.page_length)
            if index != self._page_index:
                self._page_index = index
                self._on_clip_notes_changed()
                with self._playhead_update_guard():
                    self._update_playhead_offset()
                self.notify_page_index()
            return True
        else:
            return False

    def _show_settings(self):
        layer = self._note_settings_layer
        if layer and self.is_enabled():
            layer.grab(self)

    def _request_show_settings(self):
        if self._show_settings_task.is_killed:
            self._show_settings_task.restart()

    def _hide_settings(self):
        self._show_settings_task.kill()
        layer = self._note_settings_layer
        self._attribute_deltas = [ None for _ in xrange(3) ]
        self._update_attributes_display()
        if layer:
            layer.release(self)

    def _get_note_settings_layer(self):
        return self._note_settings_layer

    def _set_note_settings_layer(self, layer):
        raise not self._note_settings_layer or not self._note_settings_layer.owner or AssertionError
        self._note_settings_layer = layer

    note_settings_layer = property(_get_note_settings_layer, _set_note_settings_layer)

    def _get_modify_all_notes_enabled(self):
        return self._modify_all_notes_enabled

    def _set_modify_all_notes_enabled(self, enabled):
        if enabled != self._modify_all_notes_enabled:
            self._modify_all_notes_enabled = enabled
            if enabled:
                self._show_settings()
            else:
                self._hide_settings()
            self._on_clip_notes_changed()

    modify_all_notes_enabled = property(_get_modify_all_notes_enabled, _set_modify_all_notes_enabled)

    def set_encoder_controls(self, controls):
        if controls:
            self.set_velocity_control(controls[7])
            self.set_length_control(controls[6])
            self.set_nudge_control(controls[5])
        else:
            self.set_velocity_control(None)
            self.set_length_control(None)
            self.set_nudge_control(None)

    def set_encoder_touch_buttons(self, controls):
        self._on_any_touch_value.subject = controls
        if controls:
            self.set_velocity_touch_button(controls[7])
            self.set_length_touch_button(controls[6])
            self.set_nudge_touch_button(controls[5])
        else:
            self.set_velocity_touch_button(None)
            self.set_length_touch_button(None)
            self.set_nudge_touch_button(None)

    def set_top_display_line(self, display):
        if display:
            display.set_data_sources(self._top_data_sources)

    def set_bottom_display_line(self, display):
        if display:
            display.set_data_sources(self._bottom_data_sources)

    def set_clear_display_line1(self, display):
        if display:
            display.reset()

    def set_clear_display_line2(self, display):
        if display:
            display.reset()

    def _data_sources_for_line(self, line_index):
        return (None, None, None, None, None, None, None, None) if line_index > 0 else self._top_data_sources

    def set_detail_clip(self, clip):
        self._sequencer_clip = clip
        self._on_clip_notes_changed.subject = clip
        self._on_playing_status_changed.subject = clip
        self._on_loop_start_changed.subject = clip
        self._on_loop_end_changed.subject = clip
        self._on_start_marker_changed.subject = clip
        self._on_song_is_playing_changed.subject = self.song() if clip else None
        self._on_clip_changed()
        self._on_clip_notes_changed()

    def set_editing_note(self, note_index):
        self._note_index = note_index
        self._on_clip_notes_changed()

    def set_mute_button(self, button):
        self._mute_button = button
        self._on_mute_value.subject = button

    def set_full_velocity_button(self, button):
        self._full_velocity_button = button
        self._on_full_velocity_value.subject = button

    def set_button_matrix(self, matrix):
        self._matrix = matrix
        self._on_matrix_value.subject = matrix
        if matrix != None:
            matrix.reset()
            for button, _ in matrix.iterbuttons():
                if button:
                    button.set_channel(PAD_FEEDBACK_CHANNEL)

        self._update_editor_matrix()

    def set_velocity_control(self, control):
        self._on_velocity_value.subject = control

    def set_length_control(self, control):
        self._on_length_value.subject = control

    def set_nudge_control(self, control):
        self._on_nudge_value.subject = control

    def set_velocity_touch_button(self, control):
        self._on_velocity_touch_value.subject = control

    def set_length_touch_button(self, control):
        self._on_length_touch_value.subject = control

    def set_nudge_touch_button(self, control):
        self._on_nudge_touch_value.subject = control

    def set_quantization_buttons(self, buttons):
        self._quantization_button_slots.disconnect()
        self._quantization_buttons = buttons or []
        for button in self._quantization_buttons:
            if button:
                button.set_on_off_values('NoteEditor.QuantizationSelected', 'NoteEditor.QuantizationUnselected')
            self._quantization_button_slots.register_slot(button, self._on_quantization_button_value, 'value', dict(identify_sender=True))

        self._update_quantization_buttons()

    def set_full_velocity(self, active):
        self._full_velocity = active

    def update(self):
        self._update_editor_matrix_leds()
        self._update_quantization_buttons()
        self._restore_playhead_state()
        self._update_note_settings()

    def _update_note_settings(self):
        if not self.is_enabled():
            self._hide_settings()

    @subject_slot('start_marker')
    def _on_start_marker_changed(self):
        self._on_clip_changed()

    @subject_slot('loop_start')
    def _on_loop_start_changed(self):
        self._on_clip_changed()

    @subject_slot('loop_end')
    def _on_loop_end_changed(self):
        self._on_clip_changed()

    def _on_clip_changed(self):
        with self._playhead_update_guard():
            self._update_playhead_clip()

    def _restore_playhead_state(self):
        clip_playing = self._sequencer_clip and self._sequencer_clip.is_playing
        self._playhead.enabled = clip_playing and self.is_enabled()

    def _update_playhead_offset(self):
        raise self._playhead.enabled == False or AssertionError
        page_length = self.page_length
        self._playhead.start_time = page_length * self._page_index
        self._playhead.step_length = page_length / len(self._playhead.notes)

    def _update_playhead_clip(self):
        if not self._playhead.enabled == False:
            raise AssertionError
            clip = self._sequencer_clip
            loop_start = clip and clip.loop_start
            loop_end = clip.loop_end
            loop_length = loop_end - loop_start
            self._playhead.clip_loop = (loop_start, loop_length)
            self._playhead.clip_start_time = clip.start_time
            self._playhead.clip_start_marker = clip.start_marker

    def _update_playhead_notes(self):
        raise self._playhead.enabled == False or AssertionError
        self._playhead.notes = self._playhead_notes if not self._is_triplet_quantization() else self._playhead_triplet_notes

    def _update_full_playhead(self):
        self._update_playhead_notes()
        self._update_playhead_offset()
        self._update_playhead_clip()

    @contextmanager
    def _playhead_update_guard(self):
        self._playhead.enabled = False
        yield
        raise self._playhead.enabled == False or AssertionError
        self._restore_playhead_state()

    @subject_slot('playing_status')
    def _on_playing_status_changed(self):
        with self._playhead_update_guard():
            self._update_playhead_clip()

    @subject_slot('is_playing')
    def _on_song_is_playing_changed(self):
        with self._playhead_update_guard():
            self._update_playhead_clip()

    def _get_clip_notes_time_range(self):
        if self._modify_all_notes_enabled:
            time_length = STEP_SEQ_OVERALL_LENGTH
            time_start = 0
        else:
            time_length = self.page_length
            time_start = self._page_index * time_length
        return (time_start, time_length)

    @subject_slot('notes')
    def _on_clip_notes_changed(self):
        """ get notes from clip for offline array """
        if self._sequencer_clip:
            time_start, time_length = self._get_clip_notes_time_range()
            self._clip_notes = self._sequencer_clip.get_notes(time_start, self._note_index, time_length, 1)
        else:
            self._clip_notes = []
        self._update_editor_matrix()

    def _update_editor_matrix(self):
        """
        update offline array of button LED values, based on note
        velocity and mute states
        """
        step_colors = ['NoteEditor.StepDisabled'] * STEP_SEQ_SIZE
        for time_step, index in self._visible_steps():
            notes = time_step.filter_notes(self._clip_notes)
            step_colors[index] = color_for_note(most_significant_note(notes)) if len(notes) > 0 else 'NoteEditor.StepEmpty'

        self._step_colors = step_colors
        self._update_editor_matrix_leds()

    def _visible_steps(self):
        first_time = self.page_length * self._page_index
        steps_per_page = STEP_SEQ_WIDTH * STEP_SEQ_HEIGHT
        step_length = self._get_step_length()
        indices = range(steps_per_page)
        if self._is_triplet_quantization():
            indices = filter(lambda k: k % 8 not in (6, 7), indices)
        return [ (self._time_step(first_time + k * step_length), indices[k]) for k in range(len(indices)) ]

    def _update_editor_matrix_leds(self):
        """ update hardware LEDS to match offline array values """
        if self.is_enabled() and self._matrix:
            for row, col in product(xrange(STEP_SEQ_HEIGHT), xrange(STEP_SEQ_WIDTH)):
                index = row * STEP_SEQ_WIDTH + col
                color = self._step_colors[index]
                self._matrix.set_light(col, row, color)

    def _get_step_start_time(self, x, y):
        """ returns step starttime in beats, based on step coordinates """
        raise in_range(x, 0, STEP_SEQ_WIDTH) or AssertionError
        raise in_range(y, 0, STEP_SEQ_HEIGHT) or AssertionError
        page_time = self._page_index * STEP_SEQ_SIZE * self._triplet_factor
        step_time = x + y * STEP_SEQ_WIDTH * self._triplet_factor
        return (page_time + step_time) * self._get_step_length()

    def _get_step_length(self):
        return QUANTIZATION_LIST[self._quantization_index] / QUANTIZATION_FACTOR

    def _set_quantization_index(self, index):
        self._quantization_index = index
        quantization, is_triplet = CLIP_VIEW_GRID_LIST[self._quantization_index]
        self._triplet_factor = 1.0 if not is_triplet else 0.75
        if self._clip_creator:
            self._clip_creator.grid_quantization = quantization
            self._clip_creator.is_grid_triplet = is_triplet
        if self._sequencer_clip:
            self._sequencer_clip.view.grid_quantization = quantization
            self._sequencer_clip.view.grid_is_triplet = is_triplet

    def _update_quantization_buttons(self):
        if self.is_enabled():
            for index, button in enumerate(self._quantization_buttons):
                if button != None:
                    if index is self._quantization_index:
                        button.turn_on()
                    else:
                        button.turn_off()

    @subject_slot('value')
    def _on_mute_value(self, value):
        if self.is_enabled():
            if value:
                self._trigger_modification(immediate=True)

    @subject_slot('value')
    def _on_full_velocity_value(self, value):
        if self.is_enabled():
            if value:
                self._trigger_modification(immediate=True)

    @subject_slot('normalized_value')
    def _on_velocity_value(self, value):
        if self.is_enabled():
            self._velocity_offset += value * 128
            self._trigger_modification()

    @subject_slot('normalized_value')
    def _on_length_value(self, value):
        if self.is_enabled():
            self._length_offset += self._get_beat_time_increment_from_delta(value)
            self._trigger_modification()

    @subject_slot('normalized_value')
    def _on_nudge_value(self, value):
        if self.is_enabled():
            self._nudge_offset += self._get_beat_time_increment_from_delta(value)
            self._trigger_modification()

    @subject_slot('value')
    def _on_quantization_button_value(self, value, sender):
        if self.is_enabled() and value or not sender.is_momentary():
            self._set_quantization_index(list(self._quantization_buttons).index(sender))
            self.notify_page_length()
            self.select_page_in_point(self._selected_page_point)
            self._on_clip_notes_changed()
            with self._playhead_update_guard():
                self._update_full_playhead()
            self._update_quantization_buttons()

    @subject_slot('value')
    def _on_matrix_value(self, value, x, y, is_momentary):
        if self.is_enabled():
            if self._sequencer_clip == None and value or not is_momentary:
                clip = create_clip_in_selected_slot(self._clip_creator, self.song(), CLIP_LENGTH_LIST[self._quantization_index])
                self.set_detail_clip(clip)
            if not self._is_triplet_quantization() or x < STEP_SEQ_WIDTH * self._triplet_factor:
                if value or not is_momentary:
                    self._on_press_step((x, y))
                else:
                    self._on_release_step((x, y))

    @subject_slot('value')
    def _on_any_touch_value(self, value, x, y, is_momentary):
        pass

    @subject_slot('value')
    def _on_velocity_touch_value(self, value):
        if self.is_enabled():
            self._attribute_deltas[2] = 0 if value else None
            self._update_attributes_display()

    @subject_slot('value')
    def _on_length_touch_value(self, value):
        if self.is_enabled():
            self._attribute_deltas[1] = 0 if value else None
            self._update_attributes_display()

    @subject_slot('value')
    def _on_nudge_touch_value(self, value):
        if self.is_enabled():
            self._attribute_deltas[0] = 0 if value else None
            self._update_attributes_display()

    def _sign_for_value(self, value):
        return '+' if value > 0 else ('-' if value < 0 else '')

    def _update_attributes_display(self):
        if self._attribute_deltas[0] != None:
            self._bottom_data_sources[5].set_display_string(self._sign_for_value(self._attribute_deltas[0]))
        else:
            self._bottom_data_sources[5].set_display_string('')
        if self._attribute_deltas[1] != None:
            self._bottom_data_sources[6].set_display_string(self._sign_for_value(self._attribute_deltas[1]))
        else:
            self._bottom_data_sources[6].set_display_string('')
        if self._attribute_deltas[2] != None:
            self._bottom_data_sources[7].set_display_string(str(self._attribute_deltas[2]))
        else:
            self._bottom_data_sources[7].set_display_string('')

    def _on_release_step(self, step):
        self._step_tap_tasks[step].kill()
        if step in self._pressed_steps:
            self._delete_notes_in_step(step)
            self._pressed_steps.remove(step)
        if step in self._modified_steps:
            self._modified_steps.remove(step)
        if not self._pressed_steps and not self._modified_steps and not self._modify_all_notes_enabled:
            self._hide_settings()

    def _on_press_step(self, step):
        if not self._pressed_steps and not self._modified_steps:
            self._request_show_settings()
        if step not in self._pressed_steps and step not in self._modified_steps:
            self._attribute_deltas = [ (None if delta == None else 0) for delta in self._attribute_deltas ]
            self._update_attributes_display()
            self._step_tap_tasks[step].restart()
            self._pressed_steps.append(step)
            self._add_note_in_step(step)

    def _time_step(self, time):
        if self.loop_steps and self._sequencer_clip != None and self._sequencer_clip.looping:
            return LoopingTimeStep(time, self._get_step_length(), self._sequencer_clip.loop_start, self._sequencer_clip.loop_end)
        else:
            return TimeStep(time, self._get_step_length())

    def _add_note_in_step(self, step):
        """
        Add note in given step if there are none in there, otherwise
        select the step for potential deletion or modification
        """
        x, y = step
        time = self._get_step_start_time(x, y)
        notes = self._time_step(time).filter_notes(self._clip_notes)
        if not (self._full_velocity_button and self._full_velocity_button.is_pressed()):
            full_velocity = self._full_velocity
            if notes:
                most_significant_velocity = most_significant_note(notes)[3]
                (self._mute_button.is_pressed() or most_significant_velocity != 127 and full_velocity) and self._trigger_modification(step, immediate=True)
        else:
            pitch = self._note_index
            mute = self._mute_button.is_pressed()
            velocity = 127 if full_velocity else DEFAULT_VELOCITY
            note = (pitch,
             time,
             self._get_step_length(),
             velocity,
             mute)
            self._sequencer_clip.set_notes((note,))
            self._sequencer_clip.deselect_all_notes()
            self._trigger_modification(step, done=True)

    def _delete_notes_in_step(self, (x, y)):
        """ Delete all notes in the given step """
        if self._sequencer_clip:
            time_step = self._time_step(self._get_step_start_time(x, y))
            for time, length in time_step.connected_time_ranges():
                self._sequencer_clip.remove_notes(time, self._note_index, length, 1)

    def _trigger_modification(self, step = None, done = False, immediate = False):
        """
        Because the modification of notes is slow, we
        accumulate modification events and perform all of them
        alltogether in a task. Call this function whenever a given set
        of steps (or potentially all steps) are to be modified.
        
        If done=True, we just notify that the given steps have been
        modified without actually executing the task.
        """
        if step is None:
            self._modified_steps += self._pressed_steps
            self._pressed_steps = []
        else:
            if step not in self._modified_steps:
                self._modified_steps.append(step)
            if step in self._pressed_steps:
                self._pressed_steps.remove(step)
        if not done:
            if immediate:
                self._do_modification()
                self._modify_task.kill()
            elif self._modify_task.is_killed:
                self._modify_task.restart()

    def _do_modification(self):
        attribute_deltas = [ 0 for _ in xrange(3) ]
        if self._modify_all_notes_enabled:
            new_notes = self._modify_all_notes(attribute_deltas)
            self._replace_notes(new_notes)
        elif self._modified_steps:
            new_notes = self._modify_step_notes(self._modified_steps, attribute_deltas)
            self._replace_notes(new_notes)
        for i, delta in enumerate(attribute_deltas):
            if self._attribute_deltas[i] != None:
                self._attribute_deltas[i] += delta

        self._velocity_offset = 0
        self._length_offset = 0
        self._nudge_offset = 0
        self._update_attributes_display()

    def _replace_notes(self, new_notes):
        if new_notes != self._clip_notes:
            clip = self._sequencer_clip
            time_start, time_length = self._get_clip_notes_time_range()
            clip.remove_notes(time_start, self._note_index, time_length, 1)
            clip.set_notes(tuple(new_notes))
            clip.deselect_all_notes()

    def _modify_all_notes(self, attribute_deltas):
        """ modify all notes in the current pitch """
        return self._modify_notes_in_time(TimeStep(0.0, MAX_CLIP_LENGTH), self._clip_notes, attribute_deltas)

    def _limited_nudge_offset(self, steps, notes, nudge_offset):
        limited_nudge_offset = MAX_CLIP_LENGTH
        for x, y in steps:
            time_step = self._time_step(self._get_step_start_time(x, y))
            for note in time_step.filter_notes(notes):
                time_after_nudge = time_step.clamp(note[1], nudge_offset)
                limited_nudge_offset = min(limited_nudge_offset, abs(note[1] - time_after_nudge))

        return sign(nudge_offset) * limited_nudge_offset

    def _modify_step_notes(self, steps, attribute_deltas):
        """ Return a new list with all notes within steps modified. """
        notes = self._clip_notes
        self._nudge_offset = self._limited_nudge_offset(steps, notes, self._nudge_offset)
        for x, y in steps:
            time_step = self._time_step(self._get_step_start_time(x, y))
            notes = self._modify_notes_in_time(time_step, notes, attribute_deltas)

        return notes

    def _modify_notes_in_time(self, time_step, notes, attribute_deltas):
        step_notes = time_step.filter_notes(self._clip_notes)
        step_mute = all(map(lambda note: note[4], step_notes))
        return map(partial(self._modify_single_note, step_mute, time_step, attribute_deltas), notes)

    def _modify_single_note(self, step_mute, time_step, attribute_deltas, (pitch, time, length, velocity, mute)):
        """
        Return a modified version of the passed in note taking into
        account current modifiers. If the note is not within
        the given step, returns the note as-is.
        
        If the time_step is inside a loop, the last part of the loop
        is considered as being the same as the part just before the
        loop, so the resulting note may, in this case, jump between
        the beginning and the end.
        """
        if time_step.includes_time(time):
            current_time = time
            current_length = length
            current_velocity = velocity
            time = time_step.clamp(time, self._nudge_offset)
            length = max(0, length + self._length_offset)
            full_velocity = self._full_velocity_button and self._full_velocity_button.is_pressed() or self._full_velocity
            velocity = 127 if full_velocity else clamp(velocity + self._velocity_offset, 1, 127)
            mute = not step_mute if self._mute_button.is_pressed() else mute
            attribute_deltas[0] = self._delta_value(attribute_deltas[0], time - current_time, self._nudge_offset > 0)
            attribute_deltas[1] = self._delta_value(attribute_deltas[1], length - current_length, self._length_offset > 0)
            attribute_deltas[2] = self._delta_value(attribute_deltas[2], velocity - current_velocity, self._velocity_offset > 0)
        return (pitch,
         time,
         length,
         velocity,
         mute)

    def _delta_value(self, current_delta, requested_delta, up):
        if abs(requested_delta) > BEAT_TIME_EPSILON:
            return (max if up else min)(requested_delta, current_delta)
        else:
            return current_delta

    def _is_triplet_quantization(self):
        return self._triplet_factor == 0.75

    def _get_beat_time_increment_from_delta(self, delta):
        """ takes relative encoder delta and returns a beat time increment """
        return self._get_step_length() * delta