#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/LoopSelectorComponent.py
from __future__ import with_statement
from functools import partial
from _Framework import Task
from _Framework import Defaults
from _Framework.Control import ButtonControl
from _Framework.SubjectSlot import subject_slot, Subject
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.Util import contextmanager, clamp
from itertools import izip

def create_clip_in_selected_slot(creator, song, clip_length = None):
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
    __subject_events__ = ('page', 'page_index', 'page_length')

    @property
    def can_change_page(self):
        return True

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
        return True


class LoopSelectorComponent(ControlSurfaceComponent):
    """
    Component that uses a button matrix to display the timeline of a
    clip. It allows you to select the loop of the clip and a page
    within it of a given Paginator object.
    """
    next_page_button = ButtonControl()
    prev_page_button = ButtonControl()
    __subject_events__ = ('is_following',)

    def __init__(self, clip_creator = None, measure_length = 4.0, follow_detail_clip = False, paginator = None, *a, **k):
        super(LoopSelectorComponent, self).__init__(*a, **k)
        self._clip_creator = clip_creator
        self._sequencer_clip = None
        self._paginator = Paginator()
        self._loop_start = 0
        self._loop_end = 0
        self._loop_length = 0
        self._is_following = False
        self._follow_button = None
        self._select_button = None
        self._short_loop_selector_matrix = None
        self._loop_selector_matrix = None
        self._pressed_pages = []
        self._page_colors = []
        self._measure_length = measure_length
        self._last_playhead_page = -1
        self._follow_task = self._tasks.add(Task.sequence(Task.wait(Defaults.MOMENTARY_DELAY), Task.run(partial(self._set_is_following, True))))
        self._follow_task.kill()
        if follow_detail_clip:
            self._on_detail_clip_changed.subject = self.song().view
        self._on_session_record_changed.subject = self.song()
        self._on_song_playback_status_changed.subject = self.song()
        if paginator is not None:
            self.set_paginator(paginator)

    def _get_is_following(self):
        return self._can_follow and self._is_following

    def _set_is_following(self, value):
        self._is_following = value
        self.notify_is_following(value)

    is_following = property(_get_is_following, _set_is_following)

    def set_paginator(self, paginator):
        self._paginator = paginator or Paginator()
        self._on_page_index_changed.subject = paginator
        self._on_page_length_changed.subject = paginator
        self._update_page_colors()

    @subject_slot('page_index')
    def _on_page_index_changed(self):
        self._update_page_colors()

    @subject_slot('page_length')
    def _on_page_length_changed(self):
        self._update_page_colors()
        self._update_follow_button()
        self._select_start_page_if_out_of_loop_range()

    def set_follow_button(self, button):
        self._follow_button = button
        self._on_follow_value.subject = button
        self._update_follow_button()

    def set_select_button(self, button):
        self._select_button = button

    @subject_slot('detail_clip')
    def _on_detail_clip_changed(self):
        self.set_detail_clip(self.song().view.detail_clip)

    def set_detail_clip(self, clip):
        if clip != self._sequencer_clip:
            self._is_following = clip != None and (self._is_following or clip_is_new_recording(clip))
            self._on_playing_position_changed.subject = clip
            self._on_playing_status_changed.subject = clip
            self._on_loop_start_changed.subject = clip
            self._on_loop_end_changed.subject = clip
            self._on_is_recording_changed.subject = clip
            self._sequencer_clip = clip
            self._select_start_page_if_out_of_loop_range()
            self._on_loop_changed()

    def _update_follow_button(self):
        if self.is_enabled() and self._follow_button:
            self._follow_button.set_light(self.is_following)

    def _select_start_page_if_out_of_loop_range(self):
        if self._sequencer_clip:
            page_start = self._paginator.page_index * self._paginator.page_length
            if self._sequencer_clip and (page_start <= self._sequencer_clip.loop_start or page_start >= self._sequencer_clip.loop_end):
                self._paginator.select_page_in_point(self._sequencer_clip.loop_start)
        else:
            self._paginator.select_page_in_point(0)

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
        self._update_page_colors()

    def set_loop_selector_matrix(self, matrix):
        self._loop_selector_matrix = matrix
        self._on_loop_selector_matrix_value.subject = matrix
        if matrix:
            matrix.reset()
        self._update_page_colors()

    def set_short_loop_selector_matrix(self, matrix):
        self._short_loop_selector_matrix = matrix
        self._on_short_loop_selector_matrix_value.subject = matrix
        if matrix:
            matrix.reset()
        self._update_page_colors()

    def update(self):
        super(LoopSelectorComponent, self).update()
        self._update_page_and_playhead_leds()
        self._update_follow_button()

    @subject_slot('is_recording')
    def _on_is_recording_changed(self):
        self.is_following = self._is_following or clip_is_new_recording(self._sequencer_clip)

    @subject_slot('playing_position')
    def _on_playing_position_changed(self):
        self._update_page_and_playhead_leds()
        self._update_page_selection()

    @subject_slot('playing_status')
    def _on_playing_status_changed(self):
        self._update_page_and_playhead_leds()

    @subject_slot('session_record')
    def _on_session_record_changed(self):
        self._update_page_and_playhead_leds()

    @subject_slot('is_playing')
    def _on_song_playback_status_changed(self):
        self._update_page_and_playhead_leds()

    def _has_running_clip(self):
        return self._sequencer_clip != None and (self._sequencer_clip.is_playing or self._sequencer_clip.is_recording)

    def _update_page_selection(self):
        if self.is_enabled() and self.is_following and self._has_running_clip():
            position = self._sequencer_clip.playing_position
            self._paginator.select_page_in_point(position)

    def _update_page_and_playhead_leds(self):

        @contextmanager
        def save_page_color(page_colors, page):
            old_page_value = page_colors[page]
            yield
            page_colors[page] = old_page_value

        @contextmanager
        def replace_and_restore_tail_colors(page_colors, page):
            if clip_is_new_recording(self._sequencer_clip):
                old_tail_values = page_colors[page + 1:]
                page_colors[page + 1:] = ['LoopSelector.OutsideLoop'] * len(old_tail_values)
            yield
            if clip_is_new_recording(self._sequencer_clip):
                page_colors[page + 1:] = old_tail_values

        if self.is_enabled() and self._has_running_clip():
            position = self._sequencer_clip.playing_position
            visible_page = int(position / self._page_length_in_beats) - self.page_offset
            page_colors = self._page_colors
            if 0 <= visible_page < len(page_colors):
                with save_page_color(page_colors, visible_page):
                    if self.song().is_playing:
                        page_colors[visible_page] = 'LoopSelector.PlayheadRecord' if self.song().session_record else 'LoopSelector.Playhead'
                    with replace_and_restore_tail_colors(page_colors, visible_page):
                        self._update_page_leds()
            else:
                self._update_page_leds()
            self._last_playhead_page = visible_page
        else:
            self._update_page_leds()

    def _get_size(self):
        return max(len(self._loop_selector_matrix or []), len(self._short_loop_selector_matrix or []), 1)

    def _get_loop_in_pages(self):
        page_length = self._page_length_in_beats
        loop_start = int(self._loop_start / page_length)
        loop_end = int(self._loop_end / page_length)
        loop_length = loop_end - loop_start + int(self._loop_end % page_length != 0)
        return (loop_start, loop_length)

    def _selected_pages_range(self):
        size = self._get_size()
        page_length = self._page_length_in_beats
        seq_page_length = max(self._paginator.page_length / page_length, 1)
        seq_page_start = int(self._paginator.page_index * self._paginator.page_length / page_length)
        seq_page_end = int(min(seq_page_start + seq_page_length, self.page_offset + size))
        return (seq_page_start, seq_page_end)

    def _update_page_colors(self):
        """
        Update the offline array mapping the timeline of the clip to buttons.
        """
        page_length = self._page_length_in_beats
        size = self._get_size()

        def calculate_page_colors():
            l_start, l_length = self._get_loop_in_pages()
            page_offset = self.page_offset
            pages_per_measure = int(self._one_measure_in_beats / page_length)

            def color_for_page(absolute_page):
                if l_start <= absolute_page < l_start + l_length:
                    return 'LoopSelector.InsideLoopStartBar' if absolute_page % pages_per_measure == 0 else 'LoopSelector.InsideLoop'
                else:
                    return 'LoopSelector.OutsideLoop'

            return map(color_for_page, xrange(page_offset, page_offset + size))

        def mark_selected_pages(page_colors):
            for page_index in xrange(*self._selected_pages_range()):
                button_index = page_index - self.page_offset
                if page_colors[button_index].startswith('LoopSelector.InsideLoop'):
                    page_colors[button_index] = 'LoopSelector.SelectedPage'

        page_colors = calculate_page_colors()
        mark_selected_pages(page_colors)
        self._page_colors = page_colors
        self._update_page_and_playhead_leds()

    def _update_page_leds(self):
        self._update_page_leds_in_matrix(self._loop_selector_matrix)
        self._update_page_leds_in_matrix(self._short_loop_selector_matrix)

    def _update_page_leds_in_matrix(self, matrix):
        """ update hardware leds to match precomputed map """
        if self.is_enabled() and matrix:
            for button, color in izip(matrix, self._page_colors):
                if button:
                    button.set_light(color)

    def _jump_to_page(self, next_page):
        start, length = self._get_loop_in_pages()
        if next_page >= start + length:
            next_page = start
        elif next_page < start:
            next_page = start + length - 1
        self._paginator.select_page_in_point(next_page * self._page_length_in_beats)

    @next_page_button.pressed
    def next_page_button(self, button):
        if self.is_following:
            self.is_following = False
        else:
            _, end = self._selected_pages_range()
            self._jump_to_page(end)
            self._follow_task.restart()

    @next_page_button.released
    def next_page_button(self, button):
        self._follow_task.kill()

    @prev_page_button.pressed
    def prev_page_button(self, button):
        if self.is_following:
            self.is_following = False
        else:
            begin, end = self._selected_pages_range()
            self._jump_to_page(begin - (end - begin))
            self._follow_task.restart()

    @prev_page_button.released
    def prev_page_button(self, button):
        self._follow_task.kill()

    @subject_slot('value')
    def _on_short_loop_selector_matrix_value(self, value, x, y, is_momentary):
        page = x + y * self._short_loop_selector_matrix.width()
        if self.is_enabled():
            if value or not is_momentary:
                self._pressed_pages = [page]
                self._try_set_loop()
                self._pressed_pages = []

    @subject_slot('value')
    def _on_loop_selector_matrix_value(self, value, x, y, is_momentary):
        page = x + y * self._loop_selector_matrix.width()
        if self.is_enabled():
            if value or not is_momentary:
                if page not in self._pressed_pages:
                    self._on_press_loop_selector_matrix(page)
        if (not is_momentary or not value) and page in self._pressed_pages:
            self._pressed_pages.remove(page)

    def _quantize_page_index(self, page_index, quant):
        page_length = self._page_length_in_beats
        return quant * float(int(page_length * page_index / quant))

    def _on_press_loop_selector_matrix(self, page):

        def create_clip(pages):
            measure = self._one_measure_in_beats
            length = self._quantize_page_index(pages, measure) + measure
            create_clip_in_selected_slot(self._clip_creator, self.song(), length)

        def handle_page_press_on_clip(page):
            l_start, l_length = self._get_loop_in_pages()
            page_in_loop = l_start <= page < l_start + l_length
            buttons_pressed = len(self._pressed_pages)
            if buttons_pressed == 1 and page_in_loop:
                self._try_select_page(page)
            elif buttons_pressed > 1 or not page_in_loop:
                self._try_set_loop()

        self._pressed_pages.append(page)
        absolute_page = page + self.page_offset
        if not self._select_button or not self._select_button.is_pressed():
            if self._sequencer_clip == None and not self.song().view.highlighted_clip_slot.has_clip:
                create_clip(absolute_page)
            elif self._sequencer_clip != None:
                handle_page_press_on_clip(absolute_page)
        elif not self.is_following:
            self._try_select_page(absolute_page)

    def _try_select_page(self, page):
        step_time = page * self._page_length_in_beats
        if self._paginator.select_page_in_point(step_time):
            self.is_following = False
            return True
        return False

    def _try_set_loop(self):
        did_set_loop = False
        if self._sequencer_clip:
            if not clip_is_new_recording(self._sequencer_clip):
                lowest_page = min(self._pressed_pages) + self.page_offset
                if self._try_select_page(lowest_page):
                    self._set_loop_in_live()
                    did_set_loop = True
            if did_set_loop:
                self.is_following = True
        return did_set_loop

    def _set_loop_in_live(self):
        quant = self._page_length_in_beats
        start_page = min(self._pressed_pages) + self.page_offset
        end_page = max(self._pressed_pages) + self.page_offset
        loop_start = self._quantize_page_index(start_page, quant)
        loop_end = self._quantize_page_index(end_page, quant) + quant
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

    @property
    def _can_follow(self):
        return True

    @property
    def _page_length_in_beats(self):
        return clamp(self._paginator.page_length, 0.5, self._one_measure_in_beats)

    @property
    def _one_measure_in_beats(self):
        return self._measure_length * self.song().signature_numerator / self.song().signature_denominator

    @property
    def page_offset(self):
        size = max(self._loop_selector_matrix.width() * self._loop_selector_matrix.height() if self._loop_selector_matrix else 0, 1)
        page_index = self._paginator.page_index
        page_length = self._paginator.page_length
        selected_page_index = int(page_index * page_length / self._page_length_in_beats)
        return size * int(selected_page_index / size)

    @subject_slot('value')
    def _on_follow_value(self, value):
        if self.is_enabled() and value:
            if self._can_follow:
                self.is_following = not self.is_following
                self._update_follow_button()