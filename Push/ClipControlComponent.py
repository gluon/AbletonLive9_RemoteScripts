#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/ClipControlComponent.py
from __future__ import with_statement
import Live
from contextlib import contextmanager
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.DisplayDataSource import DisplayDataSource
from _Framework.SubjectSlot import subject_slot
from _Framework.ModesComponent import ModesComponent
from _Framework.Util import clamp, second
ONE_THIRTYSECOND_IN_BEATS = 0.125
ONE_SIXTEENTH_IN_BEATS = 0.25
ONE_YEAR_AT_120BPM_IN_BEATS = 63072000.0
GRID_QUANTIZATION_LIST = [Live.Clip.GridQuantization.no_grid,
 Live.Clip.GridQuantization.g_thirtysecond,
 Live.Clip.GridQuantization.g_sixteenth,
 Live.Clip.GridQuantization.g_eighth,
 Live.Clip.GridQuantization.g_quarter,
 Live.Clip.GridQuantization.g_half,
 Live.Clip.GridQuantization.g_bar,
 Live.Clip.GridQuantization.g_2_bars,
 Live.Clip.GridQuantization.g_4_bars,
 Live.Clip.GridQuantization.g_8_bars]

def convert_time_to_bars_beats_sixteenths(time):
    if time is None:
        return '-'
    if time >= 0:
        bars = 1 + int(time / 4.0)
    else:
        bars = int(time / 4.0) if time % 4.0 == 0 else int(time / 4.0) - 1
    beats = 1 + int(time % 4.0)
    sixteenths = 1 + int(time % 1.0 * 4)
    return str(bars) + '.' + str(beats) + '.' + str(sixteenths)


def convert_length_to_bars_beats_sixteenths(length):
    if length is None:
        return '-'
    bars = int(length / 4.0)
    beats = int(length % 4.0)
    sixteenths = int(length % 1.0 * 4)
    return str(bars) + '.' + str(beats) + '.' + str(sixteenths)


def is_new_recording(clip):
    return clip.is_recording and not clip.is_overdubbing


class LoopSettingsComponent(ControlSurfaceComponent):
    """
    Component for managing loop settings of a clip
    """

    def __init__(self, *a, **k):
        super(LoopSettingsComponent, self).__init__(*a, **k)
        self._clip = None
        self._name_sources = [ DisplayDataSource() for _ in xrange(4) ]
        self._value_sources = [ DisplayDataSource() for _ in xrange(4) ]
        self._clip_is_looping = False
        self._clip_loop_start = None
        self._clip_loop_end = None
        self._clip_loop_length = None
        self._lowest_note_time = 0.0
        self._encoder_factor = 4.0
        self._shift_button = None

    def _get_clip(self):
        return self._clip

    def _set_clip(self, clip):
        self._clip = clip
        self._on_looping_changed.subject = clip
        self._on_loop_start_changed.subject = clip
        self._on_loop_end_changed.subject = clip
        self._on_clip_notes_changed.subject = clip if clip != None and clip.is_midi_clip else None
        self.update()

    clip = property(_get_clip, _set_clip)

    def set_shift_button(self, button):
        self._shift_button = button
        self._on_shift_value.subject = button
        self._update_encoder_factor()

    def set_encoders(self, encoders):
        self._on_clip_start_value.subject = encoders[0] if encoders else None
        self._on_clip_position_value.subject = encoders[1] if encoders else None
        self._on_clip_end_value.subject = encoders[2] if encoders else None
        self._on_clip_looping_value.subject = encoders[3] if encoders else None

    def set_name_display(self, display):
        if display:
            display.set_data_sources(self._name_sources)

    def set_value_display(self, display):
        if display:
            display.set_data_sources(self._value_sources)

    @subject_slot('value')
    def _on_shift_value(self, value):
        self._update_encoder_factor()

    def _update_encoder_factor(self):
        if self.is_enabled():
            old_factor = self._encoder_factor
            if self._shift_button and self._shift_button.is_pressed() and self._clip != None:
                self._encoder_factor = 2.0
            else:
                self._encoder_factor = self._one_measure_in_beats() * 2.0
            if old_factor != self._encoder_factor and self._clip != None:
                self._clip_loop_start = self._clip.loop_start
                self._clip_loop_end = self._clip.loop_end
                self._update_loop_length()

    def _calc_new_loop_start(self, value):
        self._clip_loop_start = max(self._clip_loop_start + value * self._one_measure_in_beats() * self._encoder_factor, min(0.0, self._clip_loop_start))
        round_up = value > 0
        loop_start = self._round_beats(self._clip_loop_start, round_up)
        if loop_start < 0.0:
            lowest_event_time = min(0, self._clip.start_marker, self._lowest_note_time)
            if lowest_event_time >= self._clip_loop_start:
                loop_start = max(self._clip_loop_start, loop_start)
        return loop_start

    def _round_beats(self, value, round_up = False):
        factor = 0.5 if round_up else -0.5
        rounded = 0.0
        if self._shift_button and self._shift_button.is_pressed():
            rounded = int(round(value + factor))
        else:
            measure = self._one_measure_in_beats()
            rounded = int(round(value / measure + factor) * measure)
        return float(rounded)

    @contextmanager
    def _clip_view_update_guard(self):
        clip = self._clip
        old_loop_start, old_loop_end = clip.loop_start, clip.loop_end
        yield
        if clip.loop_start < old_loop_start or clip.loop_end > old_loop_end:
            self._clip.view.show_loop()

    @subject_slot('normalized_value')
    def _on_clip_start_value(self, value):
        if self._clip != None:
            with self._clip_view_update_guard():
                loop_start = self._calc_new_loop_start(value)
                if loop_start < self._clip.loop_end:
                    self._clip.loop_start = loop_start
                elif not self._clip.looping:
                    self._clip_loop_start = self._clip.loop_end - ONE_SIXTEENTH_IN_BEATS
                    self._clip.loop_start = self._clip_loop_start
                else:
                    self._clip_loop_start = self._clip.loop_start

    @subject_slot('normalized_value')
    def _on_clip_position_value(self, value):
        if self._clip != None and not is_new_recording(self._clip):
            loop_start = self._calc_new_loop_start(value)
            loop_end = loop_start + self._clip_loop_length
            self._clip_loop_start = loop_start
            self._clip_loop_end = loop_end
            if value > 0:
                self._clip.loop_end = loop_end
                self._clip.loop_start = loop_start
            else:
                self._clip.loop_start = loop_start
                self._clip.loop_end = loop_end
            self._clip.view.show_loop()

    @subject_slot('looping')
    def _on_looping_changed(self):
        if self.is_enabled():
            if self._clip != None:
                self._clip_is_looping = True if self._clip.looping else False
            self._update_is_looping_source()
            self._update_loop_end_source()

    @subject_slot('loop_start')
    def _on_loop_start_changed(self):
        if self._clip != None:
            self._clip_loop_start = self._on_clip_start_value.subject and not self._on_clip_start_value.subject.is_pressed() and self._on_clip_position_value.subject and not self._on_clip_position_value.subject.is_pressed() and self._clip.loop_start
        self._update_loop_length()
        self._update_loop_start_source()
        self._update_position_source()
        self._update_loop_end_source()

    @subject_slot('loop_end')
    def _on_loop_end_changed(self):
        if self._clip != None:
            self._clip_loop_end = self._on_clip_end_value.subject and not self._on_clip_end_value.subject.is_pressed() and self._on_clip_position_value.subject and not self._on_clip_position_value.subject.is_pressed() and self._clip.loop_end
        self._update_loop_length()
        self._update_position_source()
        self._update_loop_end_source()

    @subject_slot('notes')
    def _on_clip_notes_changed(self):
        self._lowest_note_time = 0.0
        if self._clip != None and self._clip.is_midi_clip:
            earliest_time = -ONE_YEAR_AT_120BPM_IN_BEATS
            negative_notes = self._clip.get_notes(earliest_time, 0, -earliest_time, 128)
            self._lowest_note_time = min([0.0] + map(second, negative_notes))

    @subject_slot('normalized_value')
    def _on_clip_end_value(self, value):
        if self._clip != None and not is_new_recording(self._clip):
            self._clip_loop_end += value * self._one_measure_in_beats() * self._encoder_factor
            if self._clip_loop_end <= self._clip.loop_start:
                if not self._clip.looping:
                    self._clip_loop_end = self._clip.loop_start + ONE_SIXTEENTH_IN_BEATS
                    self._clip.loop_end = self._clip_loop_end
            else:
                loop_end = self._round_beats(self._clip_loop_end, value > 0)
                if loop_end > self._clip.loop_start:
                    self._clip.loop_end = loop_end
                    self._clip.view.show_loop()

    @subject_slot('normalized_value')
    def _on_clip_looping_value(self, value):
        if self._clip != None:
            if self._clip.is_midi_clip or self._clip.is_audio_clip and self._clip.warping:
                if value >= 0 and not self._clip_is_looping or value < 0 and self._clip_is_looping:
                    self._clip.looping = not self._clip.looping
                    self._on_looping_changed()

    def _update_is_looping_source(self):
        self._name_sources[0].set_display_string('LoopStrt' if self._clip_is_looping else 'ClipStrt')
        self._name_sources[2].set_display_string('Length' if self._clip_is_looping else 'End')

    def _update_loop_length(self):
        if self._clip and self._clip_loop_end is not None and self._clip_loop_start is not None:
            self._clip_loop_length = self._clip.loop_end - self._clip.loop_start

    def _update_loop_start_source(self):
        self._value_sources[0].set_display_string(convert_time_to_bars_beats_sixteenths(self._clip.loop_start) if self._clip else '-')

    def _update_loop_end_source(self):
        if self._clip and not is_new_recording(self._clip):
            self._value_sources[2].set_display_string(convert_length_to_bars_beats_sixteenths(self._clip_loop_length) if self._clip_is_looping else convert_time_to_bars_beats_sixteenths(self._clip.loop_end))
            self._value_sources[3].set_display_string('On' if self._clip_is_looping else 'Off')
        else:
            self._value_sources[2].set_display_string('-')
            self._value_sources[3].set_display_string('-')

    def _update_position_source(self):
        self._value_sources[1].set_display_string(convert_time_to_bars_beats_sixteenths(self._clip.loop_start) if self._clip else '-')

    def _one_measure_in_beats(self):
        return 4.0 * self.song().signature_numerator / self.song().signature_denominator

    def update(self):
        super(LoopSettingsComponent, self).update()
        if self.is_enabled():
            for index, label in enumerate(['Start',
             'Position',
             'Length',
             'Loop']):
                self._name_sources[index].set_display_string(label)

            self._update_encoder_factor()
            self._on_loop_start_changed()
            self._on_loop_end_changed()
            self._on_looping_changed()
            self._on_clip_notes_changed()


class AudioClipSettingsComponent(ControlSurfaceComponent):
    """
    Component for managing settings of an audio clip
    """

    def __init__(self, *a, **k):
        super(AudioClipSettingsComponent, self).__init__(*a, **k)
        self._clip = None
        self._warp_mode_names = {Live.Clip.WarpMode.beats: 'Beats',
         Live.Clip.WarpMode.tones: 'Tones',
         Live.Clip.WarpMode.texture: 'Texture',
         Live.Clip.WarpMode.repitch: 'Repitch',
         Live.Clip.WarpMode.complex: 'Complex',
         Live.Clip.WarpMode.complex_pro: 'ComplexPro',
         Live.Clip.WarpMode.rex: 'Rex'}
        self._available_warp_modes = []
        self._pitch_fine = None
        self._pitch_coarse = None
        self._gain = None
        self._warping = None
        self._warp_mode = None
        self._warp_mode_encoder_value = 0.0
        self._encoder_factor = 1.0
        self._name_sources = [ DisplayDataSource() for _ in xrange(4) ]
        self._value_sources = [ DisplayDataSource() for _ in xrange(4) ]
        self._shift_button = None

    def _get_clip(self):
        return self._clip

    def _set_clip(self, clip):
        self._clip = clip
        if clip:
            self._available_warp_modes = list(clip.available_warp_modes)
            self._update_warp_mode()
            self._warping = clip.warping
            self._gain = clip.gain
            self._pitch_fine = clip.pitch_fine
            self._pitch_coarse = clip.pitch_coarse
        self._on_pitch_fine_changed.subject = clip
        self._on_pitch_coarse_changed.subject = clip
        self._on_gain_changed.subject = clip
        self._on_warp_mode_changed.subject = clip
        self._on_warping_changed.subject = clip
        self._shift_button = None
        self.update()

    clip = property(_get_clip, _set_clip)

    def set_encoders(self, encoders):
        self._on_clip_warp_mode_value.subject = encoders[0] if encoders else None
        self._on_clip_detune_value.subject = encoders[1] if encoders else None
        self._on_clip_transpose_value.subject = encoders[2] if encoders else None
        self._on_clip_gain_value.subject = encoders[3] if encoders else None

    def set_shift_button(self, button):
        self._shift_button = button
        self._on_shift_value.subject = button
        self._update_encoder_factor()

    def set_name_display(self, display):
        if display:
            display.set_data_sources(self._name_sources)

    def set_value_display(self, display):
        if display:
            display.set_data_sources(self._value_sources)

    @subject_slot('value')
    def _on_shift_value(self, value):
        self._update_encoder_factor()

    def _update_encoder_factor(self):
        if self.is_enabled():
            if self._shift_button and self._shift_button.is_pressed():
                self._encoder_factor = 0.1
            else:
                self._encoder_factor = 1.0

    @subject_slot('normalized_value')
    def _on_clip_warp_mode_value(self, value):
        if self._clip != None:
            self._warp_mode_encoder_value = clamp(self._warp_mode_encoder_value + value, 0.0, 1.0)
            if self._clip.warping:
                warp_mode_index = int(self._warp_mode_encoder_value * (len(self._available_warp_modes) - 1))
                self._clip.warp_mode = self._available_warp_modes[warp_mode_index]

    @subject_slot('normalized_value')
    def _on_clip_gain_value(self, value):
        if self._clip != None:
            delta = value * self._encoder_factor
            new_gain = self._clip.gain + delta
            self._clip.gain = clamp(new_gain, 0.0, 1.0)

    @subject_slot('normalized_value')
    def _on_clip_transpose_value(self, value):
        if self._clip != None:
            self._pitch_coarse = clamp(self._pitch_coarse + value * 96 * self._encoder_factor, -48.0, 48.0)
            self._clip.pitch_coarse = int(self._pitch_coarse)

    @subject_slot('normalized_value')
    def _on_clip_detune_value(self, value):
        if self._clip != None:
            self._pitch_fine = self._pitch_fine + value * 100.0 * self._encoder_factor
            self._clip.pitch_fine = int(self._pitch_fine)
            if self._pitch_fine < -50.0:
                if self._clip.pitch_coarse > -48:
                    self._pitch_fine += 50
                else:
                    self._pitch_fine = -49
            elif self._pitch_fine > 50:
                if self._clip.pitch_coarse < 48:
                    self._pitch_fine -= 50
                else:
                    self._pitch_fine = 49.0

    @subject_slot('warp_mode')
    def _on_warp_mode_changed(self):
        if self.is_enabled():
            self._update_warp_mode()
            self._update_warp_mode_source()

    @subject_slot('warping')
    def _on_warping_changed(self):
        if self.is_enabled():
            if self._clip:
                self._warping = self._clip.warping
            self._update_warp_mode_source()

    @subject_slot('gain')
    def _on_gain_changed(self):
        if self.is_enabled():
            if self._clip:
                self._gain = self._clip.gain
            self._update_gain_source()

    @subject_slot('pitch_fine')
    def _on_pitch_fine_changed(self):
        if self.is_enabled():
            if self._clip:
                self._pitch_fine = self._on_clip_detune_value.subject and not self._on_clip_detune_value.subject.is_pressed() and self._clip.pitch_fine
            self._update_pitch_fine_source()

    @subject_slot('pitch_coarse')
    def _on_pitch_coarse_changed(self):
        if self.is_enabled():
            if self._clip:
                self._pitch_coarse = self._on_clip_transpose_value.subject and not self._on_clip_transpose_value.subject.is_pressed() and self._clip.pitch_coarse
            self._update_pitch_coarse_source()

    def _update_warp_mode(self):
        if self.is_enabled() and self._clip:
            warp_mode = self._clip.warp_mode
            if warp_mode in self._available_warp_modes:
                self._warp_mode = warp_mode
                if self._on_clip_warp_mode_value.subject:
                    if not self._on_clip_warp_mode_value.subject.is_pressed():
                        self._warp_mode_encoder_value = len(self._available_warp_modes) > 1 and self._warping and float(self._available_warp_modes.index(self._warp_mode)) / float(len(self._available_warp_modes) - 1)
                    else:
                        self._warp_mode_encoder_value = 0.0

    def _update_warp_mode_source(self):
        if self._clip and self._warp_mode != None:
            value = self._warp_mode_names[self._warp_mode] if self._warping else 'Off'
        else:
            value = '-'
        self._value_sources[0].set_display_string(value)

    def _update_gain_source(self):
        value = self._clip.gain_display_string if self._clip and self._gain != None else '-'
        self._value_sources[3].set_display_string(value)

    def _update_pitch_fine_source(self):
        value = str(int(self._pitch_fine)) + ' ct' if self._clip and self._clip.pitch_fine != None else '-'
        self._value_sources[1].set_display_string(value)

    def _update_pitch_coarse_source(self):
        value = str(int(self._pitch_coarse)) + ' st' if self._clip and self._clip.pitch_coarse != None else '-'
        self._value_sources[2].set_display_string(value)

    def update(self):
        super(AudioClipSettingsComponent, self).update()
        if self.is_enabled():
            for index, label in enumerate(['WarpMode',
             'Detune',
             'Transpose',
             'Gain']):
                self._name_sources[index].set_display_string(label)

            self._update_warp_mode()
            self._update_warp_mode_source()
            self._update_gain_source()
            self._update_pitch_fine_source()
            self._update_pitch_coarse_source()
            self._update_encoder_factor()


class ClipNameComponent(ControlSurfaceComponent):
    """
    Component for showing the clip name
    """
    num_label_segments = 4

    def __init__(self, *a, **k):
        super(ClipNameComponent, self).__init__(*a, **k)
        self._clip = None
        self._name_data_sources = [ DisplayDataSource() for _ in xrange(self.num_label_segments) ]
        self._name_data_sources[0].set_display_string('Clip Selection:')

    def _get_clip(self):
        return self._clip

    def _set_clip(self, clip):
        self._clip = clip
        self._update_clip_name()
        self._on_name_changed.subject = clip
        self.update()

    clip = property(_get_clip, _set_clip)

    def set_display(self, display):
        if display:
            display.set_num_segments(self.num_label_segments)
            for idx in xrange(self.num_label_segments):
                display.segment(idx).set_data_source(self._name_data_sources[idx])

    @subject_slot('name')
    def _on_name_changed(self):
        if self.is_enabled():
            self._update_clip_name()

    def _name_for_clip(self, clip):
        if clip:
            return clip.name if clip.name else '[unnamed]'
        else:
            return '[none]'

    def _update_clip_name(self):
        self._name_data_sources[1].set_display_string(self._name_for_clip(self._clip))

    def update(self):
        super(ClipNameComponent, self).update()
        if self.is_enabled():
            self._update_clip_name()


class ClipControlComponent(ModesComponent):
    """
    Component that modifies clip properties
    """

    def __init__(self, loop_layer = None, audio_layer = None, clip_name_layer = None, *a, **k):
        super(ClipControlComponent, self).__init__(*a, **k)
        self._audio_clip_settings, self._loop_settings, self._clip_name = self.register_components(AudioClipSettingsComponent(is_enabled=False, layer=audio_layer), LoopSettingsComponent(is_enabled=False, layer=loop_layer), ClipNameComponent(is_enabled=False, layer=clip_name_layer))
        self.add_mode('no_clip', (self._clip_name,))
        self.add_mode('midi', (self._loop_settings, self._clip_name))
        self.add_mode('audio', (self._loop_settings, self._audio_clip_settings, self._clip_name))
        self.selected_mode = 'no_clip'
        self._update_clip()
        self._on_detail_clip_changed.subject = self.song().view

    def on_selected_scene_changed(self):
        self._update_clip()

    def on_selected_track_changed(self):
        self._update_clip()

    @subject_slot('detail_clip')
    def _on_detail_clip_changed(self):
        self._update_clip()

    def update(self):
        super(ClipControlComponent, self).update()
        if self.is_enabled():
            self._update_clip()

    def _update_mode(self):
        track = self.song().view.selected_track
        new_mode = 'no_clip'
        if track.clip_slots and (track.has_midi_input or track.has_audio_input):
            new_mode = 'midi' if track.has_midi_input else 'audio'
        self.selected_mode = new_mode

    def _update_clip(self):
        self._update_mode()
        clip = self.song().view.detail_clip if self.is_enabled() else None
        audio_clip = clip if clip and clip.is_audio_clip else None
        self._clip_name.clip = clip
        self._loop_settings.clip = clip
        self._audio_clip_settings.clip = audio_clip