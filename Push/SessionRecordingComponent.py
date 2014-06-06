#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/SessionRecordingComponent.py
from functools import partial
from _Framework.SessionRecordingComponent import SessionRecordingComponent
from _Framework.Util import forward_property
from _Framework.SubjectSlot import subject_slot
from _Framework import Task
from ActionWithOptionsComponent import ToggleWithOptionsComponent
from consts import MessageBoxText
from MessageBoxComponent import Messenger
import Live
_Q = Live.Song.Quantization
LAUNCH_QUANTIZATION = (_Q.q_quarter,
 _Q.q_half,
 _Q.q_bar,
 _Q.q_2_bars,
 _Q.q_4_bars,
 _Q.q_8_bars,
 _Q.q_8_bars,
 _Q.q_8_bars)
LENGTH_OPTION_NAMES = ('1 Beat', '2 Beats', '1 Bar', '2 Bars', '4 Bars', '8 Bars', '16 Bars', '32 Bars')
LENGTH_LABELS = ('Recording length:', '', '', '')

def song_selected_slot(song):
    view = song.view
    scene = view.selected_scene
    track = view.selected_track
    scene_index = list(song.scenes).index(scene)
    try:
        slot = track.clip_slots[scene_index]
    except IndexError:
        slot = None

    return slot


class FixedLengthSessionRecordingComponent(SessionRecordingComponent, Messenger):

    def __init__(self, *a, **k):
        super(FixedLengthSessionRecordingComponent, self).__init__(*a, **k)
        self._fixed_length = self.register_component(ToggleWithOptionsComponent())
        self._length_selector = self._fixed_length.options
        self._length_selector.option_names = LENGTH_OPTION_NAMES
        self._length_selector.selected_option = 3
        self._length_selector.labels = LENGTH_LABELS
        self._on_selected_fixed_length_option_changed.subject = self._length_selector
        length, _ = self._get_selected_length()
        self._clip_creator.fixed_length = length

    length_layer = forward_property('_length_selector')('layer')

    def _length_should_be_fixed(self):
        return self._fixed_length.is_active

    def _get_selected_length(self):
        song = self.song()
        length = 2.0 ** self._length_selector.selected_option
        quant = LAUNCH_QUANTIZATION[self._length_selector.selected_option]
        if self._length_selector.selected_option > 1:
            length = length * song.signature_numerator / song.signature_denominator
        return (length, quant)

    def set_length_button(self, button):
        self._fixed_length.action_button.set_control_element(button)
        self._on_length_value.subject = button
        self._length_press_state = None

    @subject_slot('selected_option')
    def _on_selected_fixed_length_option_changed(self, _):
        length, _ = self._get_selected_length()
        self._clip_creator.fixed_length = length

    @subject_slot('value')
    def _on_length_value(self, value):
        if value:
            self._on_length_press()
        else:
            self._on_length_release()

    def _on_length_press(self):
        song = self.song()
        slot = song_selected_slot(song)
        if slot == None:
            return
        clip = slot.clip
        if slot.is_recording and not clip.is_overdubbing:
            self._length_press_state = (slot, clip.playing_position)

    def _on_length_release(self):
        song = self.song()
        slot = song_selected_slot(song)
        if slot == None:
            return
        clip = slot.clip
        if self._length_press_state is not None:
            press_slot, press_position = self._length_press_state
            if press_slot == slot and self._length_should_be_fixed() and slot.is_recording and not clip.is_overdubbing:
                length, _ = self._get_selected_length()
                one_bar = 4.0 * song.signature_numerator / song.signature_denominator
                loop_end = int(press_position / one_bar) * one_bar
                loop_start = loop_end - length
                if loop_start >= 0.0:
                    clip.loop_end = loop_end
                    clip.end_marker = loop_end
                    clip.loop_start = loop_start
                    clip.start_marker = loop_start
                    self._tasks.add(Task.sequence(Task.delay(0), Task.run(partial(slot.fire, force_legato=True, launch_quantization=_Q.q_no_q))))
                    self.song().overdub = False
                self._fixed_length.is_active = False
        self._length_press_state = None

    def _handle_limitation_error_on_scene_creation(self):
        self.expect_dialog(MessageBoxText.SCENE_LIMIT_REACHED)