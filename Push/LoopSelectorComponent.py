#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/LoopSelectorComponent.py
from _Framework.SubjectSlot import subject_slot, Subject
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.Util import product
from itertools import izip
DOUBLE_TAP_DELAY = 3

def create_clip_in_selected_slot(creator, song, clip_length):
    """
    Create a new clip in the selected slot of if none exists, using a
    given creator object.  Fires it if the song is playing and
    displays it in the detail view.
    """
    selected_slot = song.view.highlighted_clip_slot
    if creator and selected_slot and not selected_slot.has_clip:
        creator.create(selected_slot, clip_length)
        song.view.detail_clip = selected_slot.clip
    return selected_slot.clip


def clip_is_new_recording(clip):
    return clip.is_recording and not clip.is_overdubbing


class Paginator(Subject):
    """
    Paginator interface for objects that split continuous time into
    discrete pages.  This can be used as trivial paginator splits time
    into one single infinite-length page.
    """
    __subject_events__ = ('page_index', 'page_length')

    @property
    def page_length(self):
        """
        Length of a given page.
        """
        return 2147483648.0

    @property
    def page_index(self):
        """
        Index of the currently selected page.
        """
        return 0

    def select_page_in_point(self, value):
        """
        Select the page that falls in the given time point. Returns True if page was
        selected.
        """
        pass


class LoopSelectorComponent(ControlSurfaceComponent):
    """
    Component that uses a button matrix to display the timeline of a
    clip. It allows you to select the loop of the clip and a page
    within it of a given Paginator object.
    """

    def __init__(self, clip_creator = None, measure_length = 4.0, follow_detail_clip = False, *a, **k):
        super(LoopSelectorComponent, self).__init__(*a, **k)
        self._clip_creator = clip_creator
        self._sequencer_clip = None
        self._paginator = Paginator()
        self._loop_start = 0
        self._loop_end = 0
        self._loop_length = 0
        self._is_following = True
        self._follow_button = None
        self._select_button = None
        self._loop_selector_matrix = None
        self._pressed_matrix_buttons = []
        self._measure_colors = []
        self._measure_length = measure_length
        self._last_playhead_measure = -1
        if follow_detail_clip:
            self._on_detail_clip_changed.subject = self.song().view
        self._on_session_record_changed.subject = self.song()

    @property
    def is_following(self):
        return self._is_following

    def set_paginator(self, paginator):
        self._paginator = paginator or Paginator()
        self._on_page_index_changed.subject = paginator
        self._on_page_length_changed.subject = paginator
        self._update_measure_colors()

    @subject_slot('page_index')
    def _on_page_index_changed(self):
        self._update_measure_colors()

    @subject_slot('page_length')
    def _on_page_length_changed(self):
        self._update_measure_colors()

    def set_follow_button(self, button):
        self._follow_button = button
        self._on_follow_value.subject = button
        self._update_follow_button()

    def set_select_button(self, button):
        self._select_button = button

    @subject_slot('detail_clip')
    def _on_detail_clip_changed(self):
        clip = self.song().view.detail_clip
        self.set_detail_clip(clip)

    def set_detail_clip(self, clip):
        self._on_playing_position_changed.subject = clip
        self._on_playing_status_changed.subject = clip
        self._on_loop_start_changed.subject = clip
        self._on_loop_end_changed.subject = clip
        self._sequencer_clip = clip
        self._on_loop_changed()

    def _update_follow_button(self):
        if self.is_enabled() and self._follow_button:
            self._follow_button.set_light(self._is_following)

    @subject_slot('loop_start')
    def _on_loop_start_changed(self):
        self._on_loop_changed()

    @subject_slot('loop_end')
    def _on_loop_end_changed(self):
        self._on_loop_changed()

    def _on_loop_changed(self):
        if self._sequencer_clip:
            self._loop_start = self._sequencer_clip.loop_start
            self._loop_end = self._sequencer_clip.loop_end
            self._loop_length = self._loop_end - self._loop_start
        else:
            self._loop_start = 0
            self._loop_end = 0
            self._loop_length = 0
        self._update_measure_colors()

    def set_loop_selector_matrix(self, matrix):
        self._loop_selector_matrix = matrix
        self._on_loop_selector_matrix_value.subject = matrix
        if matrix:
            matrix.reset()
        self._update_measure_colors()

    def update(self):
        self._update_measure_and_playhead_leds(force_redraw=True)
        self._update_follow_button()

    @subject_slot('is_recording')
    def _on_is_recording_changed(self):
        self._update_measure_colors()

    @subject_slot('playing_position')
    def _on_playing_position_changed(self):
        self._update_measure_and_playhead_leds()
        self._update_page_selection()

    @subject_slot('playing_status')
    def _on_playing_status_changed(self):
        self._update_measure_and_playhead_leds()

    @subject_slot('session_record')
    def _on_session_record_changed(self):
        self._update_measure_and_playhead_leds(force_redraw=True)

    def _update_page_selection(self):
        if self.is_enabled() and self._is_following and self._sequencer_clip and (self._sequencer_clip.is_playing or self._sequencer_clip.is_recording):
            position = self._sequencer_clip.playing_position
            self._paginator.select_page_in_point(position)

    def _update_measure_and_playhead_leds(self, force_redraw = False):
        if self.is_enabled() and self._sequencer_clip and (self._sequencer_clip.is_playing or self._sequencer_clip.is_recording):
            position = self._sequencer_clip.playing_position
            measure = int(position / self._one_measure_in_beats())
            measure_colors = self._measure_colors
            if measure != self._last_playhead_measure or force_redraw:
                if measure < len(measure_colors):
                    old_measure_value = self._measure_colors[measure]
                    measure_colors[measure] = 'LoopSelector.PlayheadRecord' if self.song().session_record else 'LoopSelector.Playhead'
                    if clip_is_new_recording(self._sequencer_clip):
                        old_tail_values = measure_colors[measure + 1:]
                        measure_colors[measure + 1:] = ['LoopSelector.OutsideLoop'] * len(old_tail_values)
                    self._update_measure_leds()
                    measure_colors[measure] = old_measure_value
                    if clip_is_new_recording(self._sequencer_clip):
                        measure_colors[measure + 1:] = old_tail_values
                else:
                    self._update_measure_leds()
            self._last_playhead_measure = measure
        else:
            self._update_measure_leds()

    def _get_width(self):
        return self._loop_selector_matrix.width() if self._loop_selector_matrix else 1

    def _get_height(self):
        return self._loop_selector_matrix.height() if self._loop_selector_matrix else 1

    def _update_measure_colors(self):
        """
        Update the offline array mapping the timeline of the clip to buttons.
        """
        width = self._get_width()
        height = self._get_height()
        size = width * height
        one_measure = self._one_measure_in_beats()
        loop_start_index = int(self._loop_start / one_measure)
        loop_end_index = min(size, int(self._loop_end / one_measure))
        loop_length = loop_end_index - loop_start_index + int(self._loop_end % one_measure != 0)
        before_loop = min(loop_start_index, size)
        display_loop = min(loop_length, size - before_loop)
        after_loop = max(0, size - display_loop - before_loop)
        measure_colors = ['LoopSelector.OutsideLoop'] * before_loop + ['LoopSelector.InsideLoop'] * display_loop + ['LoopSelector.OutsideLoop'] * after_loop
        page_length = self._paginator.page_length
        page_index = self._paginator.page_index
        step_seq_page_length = max(page_length / one_measure, 1)
        step_seq_page_start = int(page_index * page_length / one_measure)
        step_seq_page_end = int(min(step_seq_page_start + step_seq_page_length, size))
        for button_index in xrange(step_seq_page_start, step_seq_page_end):
            if measure_colors[button_index] is 'LoopSelector.InsideLoop':
                measure_colors[button_index] = 'LoopSelector.SelectedPage'

        self._measure_colors = measure_colors
        self._update_measure_and_playhead_leds(force_redraw=True)

    def _update_measure_leds(self):
        """ update hardware leds to match precomputed map """
        if self.is_enabled() and self._loop_selector_matrix:
            width = self._loop_selector_matrix.width()
            height = self._loop_selector_matrix.height()
            matrix_idx = product(xrange(height), xrange(width))
            for (row, col), color in izip(matrix_idx, self._measure_colors):
                self._loop_selector_matrix.set_light(col, row, color)

    @subject_slot('value')
    def _on_loop_selector_matrix_value(self, value, x, y, is_momentary):
        if self.is_enabled():
            if value or not is_momentary:
                if (y, x) not in self._pressed_matrix_buttons:
                    self._on_press_loop_selector_matrix(x, y)
        if (not is_momentary or not value) and (y, x) in self._pressed_matrix_buttons:
            self._pressed_matrix_buttons.remove((y, x))

    def _on_press_loop_selector_matrix(self, x, y):
        self._pressed_matrix_buttons.append((y, x))
        if not self._select_button or not self._select_button.is_pressed():
            if self._sequencer_clip == None and not self.song().view.highlighted_clip_slot.has_clip:
                clip_measures = x + 1 + y * self._get_width()
                create_clip_in_selected_slot(self._clip_creator, self.song(), clip_measures * self._one_measure_in_beats())
            elif self._sequencer_clip != None:
                if self._sequencer_clip.is_recording:
                    infinite_recording = not self._sequencer_clip.is_overdubbing
                    if not infinite_recording:
                        y_low, x_low = min(self._pressed_matrix_buttons, key=reversed)
                        self._select_page_in_pad(x_low, y_low) == True and self._set_loop_in_live()
        elif not self._is_following:
            self._select_page_in_pad(x, y)

    def _select_page_in_pad(self, x, y):
        step_index = x + y * self._get_width()
        step_time = step_index * self._one_measure_in_beats()
        result = self._paginator.select_page_in_point(step_time)
        return result

    def _set_loop_in_live(self):
        if self._sequencer_clip != None:
            start_y, start_x = min(self._pressed_matrix_buttons)
            end_y, end_x = max(self._pressed_matrix_buttons)
            width = self._get_width()
            measure = self._one_measure_in_beats()
            loop_start = measure * (start_x + start_y * width)
            loop_end = measure * (end_x + end_y * width + 1)
            if loop_start >= self._sequencer_clip.loop_end:
                self._sequencer_clip.loop_end = loop_end
                self._sequencer_clip.loop_start = loop_start
                self._sequencer_clip.end_marker = loop_end
                self._sequencer_clip.start_marker = loop_start
            else:
                self._sequencer_clip.loop_start = loop_start
                self._sequencer_clip.loop_end = loop_end
                self._sequencer_clip.start_marker = loop_start
                self._sequencer_clip.end_marker = loop_end
            self._sequencer_clip.view.show_loop()

    def _one_measure_in_beats(self):
        return self._measure_length * self.song().signature_numerator / self.song().signature_denominator

    @subject_slot('value')
    def _on_follow_value(self, value):
        if self.is_enabled() and value:
            self._is_following = not self._is_following
            if self._is_following:
                self._follow_button.turn_on()
            else:
                self._follow_button.turn_off()