#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/NoteEditorComponent.py
from __future__ import with_statement
from functools import partial
from itertools import chain, imap, ifilter
from _Framework.SubjectSlot import subject_slot, Subject
from _Framework.CompoundComponent import CompoundComponent
from _Framework.Util import sign, product, in_range, clamp, forward_property, first
from _Framework import Task, Defaults
from LoopSelectorComponent import create_clip_in_selected_slot
from MatrixMaps import PAD_FEEDBACK_CHANNEL
DEFAULT_VELOCITY = 100
BEAT_TIME_EPSILON = 1e-05

def color_for_note(note):
    velocity = note[3]
    muted = note[4]
    if not muted:
        if velocity == 127:
            return 'Full'
        elif velocity >= 100:
            return 'High'
        else:
            return 'Low'
    else:
        return 'Muted'


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

    def right_boundary(self):
        return max(0, self.start - self.offset + self.length - BEAT_TIME_EPSILON)

    def includes_note(self, note):
        return self.includes_time(note[1])

    def overlaps_note(self, note):
        time, length = note[1:3]
        step_start = self.left_boundary()
        step_end = self.start + self.length - BEAT_TIME_EPSILON
        note_start = int((time + self.offset) / self.length) * self.length
        note_end = note_start + length
        if step_start < note_start:
            return step_end > note_start
        else:
            return step_end < note_end

    def filter_notes(self, notes):
        return filter(self.includes_note, notes)

    def clamp(self, time, extra_time = 0.0):
        return clamp(time + extra_time, self.left_boundary(), self.right_boundary())

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


class NoteEditorComponent(CompoundComponent, Subject):
    __subject_events__ = ('page_length', 'active_steps', 'notes_changed')

    def __init__(self, settings_mode = None, clip_creator = None, grid_resolution = None, *a, **k):
        super(NoteEditorComponent, self).__init__(*a, **k)
        self.loop_steps = False
        self.full_velocity = False
        self._selected_page_point = 0
        self._page_index = 0
        self._clip_creator = clip_creator
        self._matrix = None
        self._width = 0
        self._height = 0
        self._sequencer_clip = None
        self._step_colors = []
        if settings_mode:
            self._settings_mode = self.register_component(settings_mode)
            self._mute_button = None
            self._pressed_steps = []
            self._modified_steps = []
            self._pressed_step_callback = None
            self._modify_task = self._tasks.add(Task.run(self._do_modification))
            self._modify_task.kill()
            self._modify_all_notes_enabled = False
            self._step_tap_tasks = {}
            self._clip_notes = []
            self._note_index = 36
            self._grid_resolution = grid_resolution
            self._on_resolution_changed.subject = self._grid_resolution
            self._nudge_offset = 0
            self._length_offset = 0
            self._velocity_offset = 0
            self._settings_mode and self._settings_mode.add_editor(self)
            self._settings = settings_mode.settings
            self._on_setting_changed.subject = self._settings
        self._triplet_factor = 1.0
        self._update_from_grid()
        self.background_color = 'NoteEditor.StepEmpty'

    note_settings_layer = forward_property('_settings')('layer')

    @property
    def page_index(self):
        return self._page_index

    @property
    def page_length(self):
        return self._get_step_count() * self._get_step_length() * self._triplet_factor

    @property
    def can_change_page(self):
        return not self._pressed_steps and not self._modified_steps

    def set_selected_page_point(self, point):
        if not self.can_change_page:
            raise AssertionError
            self._selected_page_point = point
            index = int(point / self.page_length) if self.page_length != 0 else 0
            self._page_index = index != self._page_index and index
            self._on_clip_notes_changed()

    def _get_modify_all_notes_enabled(self):
        return self._modify_all_notes_enabled

    def _set_modify_all_notes_enabled(self, enabled):
        if enabled != self._modify_all_notes_enabled:
            self._modify_all_notes_enabled = enabled
            if self._settings_mode:
                self._settings_mode.selected_mode = 'enabled' if enabled else 'disabled'
                self._settings_mode.selected_setting = 'pad_settings'
            self._on_clip_notes_changed()

    modify_all_notes_enabled = property(_get_modify_all_notes_enabled, _set_modify_all_notes_enabled)

    def set_detail_clip(self, clip):
        self._sequencer_clip = clip
        self._on_clip_notes_changed.subject = clip
        self._on_clip_notes_changed()

    def _get_editing_note(self):
        return self._note_index

    def _set_editing_note(self, note_index):
        self._note_index = note_index
        self._on_clip_notes_changed()

    editing_note = property(_get_editing_note, _set_editing_note)

    def set_mute_button(self, button):
        self._mute_button = button
        self._on_mute_value.subject = button

    def set_button_matrix(self, matrix):
        last_page_length = self.page_length
        self._matrix = matrix
        self._on_matrix_value.subject = matrix
        if matrix:
            self._width = matrix.width()
            self._height = matrix.height()
            matrix.reset()
            for button, _ in ifilter(first, matrix.iterbuttons()):
                button.set_channel(PAD_FEEDBACK_CHANNEL)

        for task in self._step_tap_tasks.itervalues():
            task.kill()

        def trigger_modification_task(x, y):
            trigger = partial(self._trigger_modification, (x, y), done=True)
            return self._tasks.add(Task.sequence(Task.wait(Defaults.MOMENTARY_DELAY), Task.run(trigger))).kill()

        self._step_tap_tasks = dict([ ((x, y), trigger_modification_task(x, y)) for x, y in product(xrange(self._width), xrange(self._height)) ])
        if matrix and last_page_length != self.page_length:
            self._on_clip_notes_changed()
            self.notify_page_length()
        else:
            self._update_editor_matrix()

    def update(self):
        super(NoteEditorComponent, self).update()
        self._update_editor_matrix_leds()
        self._grid_resolution.update()

    def _get_clip_notes_time_range(self):
        if self._modify_all_notes_enabled:
            time_length = self._get_step_count() * 4.0
            time_start = 0
        else:
            time_length = self.page_length
            time_start = self._page_index * time_length
        return (time_start - self._time_step(0).offset, time_length)

    @subject_slot('notes')
    def _on_clip_notes_changed(self):
        """ get notes from clip for offline array """
        if self._sequencer_clip and self._note_index != None:
            time_start, time_length = self._get_clip_notes_time_range()
            self._clip_notes = self._sequencer_clip.get_notes(time_start, self._note_index, time_length, 1)
        else:
            self._clip_notes = []
        self._update_editor_matrix()
        self.notify_notes_changed()

    def _update_editor_matrix(self):
        """
        update offline array of button LED values, based on note
        velocity and mute states
        """
        step_colors = ['NoteEditor.StepDisabled'] * self._get_step_count()
        width = self._width
        coords_to_index = lambda (x, y): x + y * width
        editing_indices = set(map(coords_to_index, self._modified_steps))
        selected_indices = set(map(coords_to_index, self._pressed_steps))
        last_editing_notes = []
        for time_step, index in self._visible_steps():
            notes = time_step.filter_notes(self._clip_notes)
            if len(notes) > 0:
                last_editing_notes = []
                if index in selected_indices:
                    color = 'NoteEditor.StepSelected'
                elif index in editing_indices:
                    note_color = color_for_note(most_significant_note(notes))
                    color = 'NoteEditor.StepEditing.' + note_color
                    last_editing_notes = notes
                else:
                    note_color = color_for_note(most_significant_note(notes))
                    color = 'NoteEditor.Step.' + note_color
            elif any(imap(time_step.overlaps_note, last_editing_notes)):
                color = 'NoteEditor.StepEditing.' + note_color
            elif index in editing_indices or index in selected_indices:
                color = 'NoteEditor.StepSelected'
                last_editing_notes = []
            else:
                color = self.background_color
                last_editing_notes = []
            step_colors[index] = color

        self._step_colors = step_colors
        self._update_editor_matrix_leds()

    def _visible_steps(self):
        first_time = self.page_length * self._page_index
        steps_per_page = self._get_step_count()
        step_length = self._get_step_length()
        indices = range(steps_per_page)
        if self._is_triplet_quantization():
            indices = filter(lambda k: k % 8 not in (6, 7), indices)
        return [ (self._time_step(first_time + k * step_length), index) for k, index in enumerate(indices) ]

    def _update_editor_matrix_leds(self):
        """ update hardware LEDS to match offline array values """
        if self.is_enabled() and self._matrix:
            for row, col in product(xrange(self._height), xrange(self._width)):
                index = row * self._width + col
                color = self._step_colors[index]
                self._matrix.set_light(col, row, color)

    def _get_step_count(self):
        return self._width * self._height

    def _get_step_start_time(self, x, y):
        """ returns step starttime in beats, based on step coordinates """
        raise in_range(x, 0, self._width) or AssertionError
        raise in_range(y, 0, self._height) or AssertionError
        page_time = self._page_index * self._get_step_count() * self._triplet_factor
        step_time = x + y * self._width * self._triplet_factor
        return (page_time + step_time) * self._get_step_length()

    def _get_step_length(self):
        return self._grid_resolution.step_length

    def _update_from_grid(self):
        quantization, is_triplet = self._grid_resolution.clip_grid
        self._triplet_factor = 1.0 if not is_triplet else 0.75
        if self._clip_creator:
            self._clip_creator.grid_quantization = quantization
            self._clip_creator.is_grid_triplet = is_triplet
        if self._sequencer_clip:
            self._sequencer_clip.view.grid_quantization = quantization
            self._sequencer_clip.view.grid_is_triplet = is_triplet

    @subject_slot('value')
    def _on_mute_value(self, value):
        if self.is_enabled() and value:
            self._trigger_modification(immediate=True)

    @subject_slot('index')
    def _on_resolution_changed(self):
        self._release_active_steps()
        self._update_from_grid()
        self.set_selected_page_point(self._selected_page_point)
        self.notify_page_length()
        self._on_clip_notes_changed()

    @subject_slot('value')
    def _on_matrix_value(self, value, x, y, is_momentary):
        if self.is_enabled():
            if self._sequencer_clip == None and value or not is_momentary:
                clip = create_clip_in_selected_slot(self._clip_creator, self.song())
                self.set_detail_clip(clip)
            if self._note_index != None:
                width = self._width * self._triplet_factor if self._is_triplet_quantization() else self._width
                if x < width and y < self._height:
                    if value or not is_momentary:
                        self._on_press_step((x, y))
                    else:
                        self._on_release_step((x, y))
                    self._update_editor_matrix()

    @subject_slot('value')
    def _on_any_touch_value(self, value, x, y, is_momentary):
        pass

    @property
    def active_steps(self):

        def get_time_range((x, y)):
            time = self._get_step_start_time(x, y)
            return (time, time + self._get_step_length())

        return imap(get_time_range, chain(self._pressed_steps, self._modified_steps))

    def _release_active_steps(self):
        for step in self._pressed_steps + self._modified_steps:
            self._on_release_step(step, do_delete_notes=False)

    def _on_release_step(self, step, do_delete_notes = True):
        self._step_tap_tasks[step].kill()
        if step in self._pressed_steps:
            if do_delete_notes:
                self._delete_notes_in_step(step)
            self._pressed_steps.remove(step)
            self._add_note_in_step(step)
        if step in self._modified_steps:
            self._modified_steps.remove(step)
        self.notify_active_steps()

    def _on_press_step(self, step):
        if self._sequencer_clip != None and step not in self._pressed_steps and step not in self._modified_steps:
            self._step_tap_tasks[step].restart()
            self._pressed_steps.append(step)
        self.notify_active_steps()

    def _time_step(self, time):
        if self.loop_steps and self._sequencer_clip != None and self._sequencer_clip.looping:
            return LoopingTimeStep(time, self._get_step_length(), self._sequencer_clip.loop_start, self._sequencer_clip.loop_end)
        else:
            return TimeStep(time, self._get_step_length())

    def _add_note_in_step(self, step, modify_existing = True):
        """
        Add note in given step if there are none in there, otherwise
        select the step for potential deletion or modification
        """
        if self._sequencer_clip != None:
            x, y = step
            time = self._get_step_start_time(x, y)
            notes = self._time_step(time).filter_notes(self._clip_notes)
            if notes:
                if modify_existing:
                    most_significant_velocity = most_significant_note(notes)[3]
                    if self._mute_button and self._mute_button.is_pressed() or most_significant_velocity != 127 and self.full_velocity:
                        self._trigger_modification(step, immediate=True)
            else:
                pitch = self._note_index
                mute = self._mute_button and self._mute_button.is_pressed()
                velocity = 127 if self.full_velocity else DEFAULT_VELOCITY
                note = (pitch,
                 time,
                 self._get_step_length(),
                 velocity,
                 mute)
                self._sequencer_clip.set_notes((note,))
                self._sequencer_clip.deselect_all_notes()
                self._trigger_modification(step, done=True)
                return True
        return False

    def _delete_notes_in_step(self, (x, y)):
        """ Delete all notes in the given step """
        if self._sequencer_clip:
            time_step = self._time_step(self._get_step_start_time(x, y))
            for time, length in time_step.connected_time_ranges():
                self._sequencer_clip.remove_notes(time, self._note_index, length, 1)

    @subject_slot('setting_changed')
    def _on_setting_changed(self, index, value):
        if self.is_enabled():
            if index == 1:
                self._nudge_offset += value
            elif index == 2:
                self._length_offset += value
            elif index == 3:
                self._velocity_offset += value
            self._trigger_modification()

    def notify_modification(self):
        """
        Tell the note editor about changes to pressed steps, so further modifications
        by the note editor are ignored.
        """
        self._trigger_modification(done=True)

    def _trigger_modification(self, step = None, done = False, immediate = False):
        """
        Because the modification of notes is slow, we
        accumulate modification events and perform all of them
        alltogether in a task. Call this function whenever a given set
        of steps (or potentially all steps) are to be modified.
        
        If done=True, we just notify that the given steps have been
        modified without actually executing the task.
        """
        needs_update = False
        if step is None:
            needs_update = bool(self._pressed_steps)
            self._modified_steps += self._pressed_steps
            self._pressed_steps = []
        else:
            if step not in self._modified_steps:
                self._modified_steps.append(step)
            if step in self._pressed_steps:
                self._pressed_steps.remove(step)
            needs_update = True
        if not done:
            if immediate:
                self._do_modification()
                self._modify_task.kill()
            elif self._modify_task.is_killed:
                self._modify_task.restart()
        if needs_update:
            self._update_editor_matrix()

    def _reset_modifications(self):
        self._velocity_offset = 0
        self._length_offset = 0
        self._nudge_offset = 0

    def _do_modification(self):
        if self._modify_all_notes_enabled:
            new_notes = self._modify_all_notes()
            self._replace_notes(new_notes)
        elif self._modified_steps:
            notes_added = map(lambda s: self._add_note_in_step(s, False), self._modified_steps)
            if any(notes_added):
                self._modify_task.restart()
            else:
                new_notes = self._modify_step_notes(self._modified_steps)
                self._replace_notes(new_notes)
        self._reset_modifications()

    def _replace_notes(self, new_notes):
        if new_notes != self._clip_notes:
            clip = self._sequencer_clip
            time_start, time_length = self._get_clip_notes_time_range()
            clip.remove_notes(time_start, self._note_index, time_length, 1)
            clip.set_notes(tuple(new_notes))
            clip.deselect_all_notes()

    def _modify_all_notes(self):
        """ modify all notes in the current pitch """
        return self._modify_notes_in_time(TimeStep(0.0, MAX_CLIP_LENGTH), self._clip_notes)

    def _limited_nudge_offset(self, steps, notes, nudge_offset):
        limited_nudge_offset = MAX_CLIP_LENGTH
        for x, y in steps:
            time_step = self._time_step(self._get_step_start_time(x, y))
            for note in time_step.filter_notes(notes):
                time_after_nudge = time_step.clamp(note[1], nudge_offset)
                limited_nudge_offset = min(limited_nudge_offset, abs(note[1] - time_after_nudge))

        return sign(nudge_offset) * limited_nudge_offset

    def _modify_step_notes(self, steps):
        """ Return a new list with all notes within steps modified. """
        notes = self._clip_notes
        self._nudge_offset = self._limited_nudge_offset(steps, notes, self._nudge_offset)
        for x, y in steps:
            time_step = self._time_step(self._get_step_start_time(x, y))
            notes = self._modify_notes_in_time(time_step, notes)

        return notes

    def _modify_notes_in_time(self, time_step, notes):
        step_notes = time_step.filter_notes(self._clip_notes)
        step_mute = all(map(lambda note: note[4], step_notes))
        return map(partial(self._modify_single_note, step_mute, time_step), notes)

    def _modify_single_note(self, step_mute, time_step, (pitch, time, length, velocity, mute)):
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
            time = time_step.clamp(time, self._nudge_offset)
            if self._length_offset <= -time_step.length and length + self._length_offset < time_step.length:
                if length > time_step.length:
                    length = time_step.length
            else:
                length = max(0, length + self._length_offset)
            velocity = 127 if self.full_velocity else clamp(velocity + self._velocity_offset, 1, 127)
            mute = not step_mute if self._mute_button and self._mute_button.is_pressed() else mute
        return (pitch,
         time,
         length,
         velocity,
         mute)

    def _min_max_for_notes(self, notes, start_time, min_max_values = None):
        for note in notes:
            note_values = list(note[:4])
            note_values[1] -= start_time
            for index, value in enumerate(note_values):
                if not min_max_values:
                    min_max_values = [(99999, -99999)] * 4
                min_value, max_value = min_max_values[index]
                min_max_values[index] = (min(value, min_value), max(value, max_value))

        return min_max_values

    def get_min_max_note_values(self):
        if self._modify_all_notes_enabled and len(self._clip_notes) > 0:
            return self._min_max_for_notes(self._clip_notes, 0.0)
        elif len(self._pressed_steps) + len(self._modified_steps) > 0:
            min_max_values = None
            for x, y in chain(self._modified_steps, self._pressed_steps):
                start_time = self._get_step_start_time(x, y)
                min_max_values = self._min_max_for_notes(self._time_step(start_time).filter_notes(self._clip_notes), start_time, min_max_values)

            return min_max_values

    def _is_triplet_quantization(self):
        return self._triplet_factor == 0.75