#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/NoteRepeatComponent.py
from _Framework.ModesComponent import ModesComponent
from _Framework import Task
from _Framework.CompoundComponent import CompoundComponent
from _Framework.SubjectSlot import subject_slot
from ActionWithOptionsComponent import OptionsComponent
t = 3.0 / 2.0
NOTE_REPEAT_FREQUENCIES = [32 * t,
 32,
 16 * t,
 16,
 8 * t,
 8,
 4 * t,
 4]
del t

class DummyNoteRepeat(object):
    repeat_rate = 1.0
    enabled = False


class NoteRepeatComponent(CompoundComponent):
    """
    Component for setting up the note repeat
    """

    def __init__(self, *a, **k):
        super(NoteRepeatComponent, self).__init__(*a, **k)
        self._aftertouch = None
        self._last_record_quantization = None
        self._note_repeat = None
        self._options = self.register_component(OptionsComponent())
        self._options.selected_color = 'NoteRepeat.RateSelected'
        self._options.unselected_color = 'NoteRepeat.RateUnselected'
        self._options.option_names = map(str, range(8))
        self._options.selected_option = 5
        self._on_selected_option_changed.subject = self._options
        self.set_note_repeat(None)

    def on_enabled_changed(self):
        if self.is_enabled():
            self._enable_note_repeat()
        else:
            self._disable_note_repeat()

    def update(self):
        super(NoteRepeatComponent, self).update()
        self._update_aftertouch()

    def _update_aftertouch(self):
        if self._aftertouch:
            self._aftertouch.reset()

    def set_aftertouch_control(self, control):
        self._aftertouch = control
        self._update_aftertouch()

    def set_select_buttons(self, buttons):
        self._options.select_buttons.set_control_element(buttons)

    def set_note_repeat(self, note_repeat):
        if not note_repeat:
            note_repeat = DummyNoteRepeat()
            self._note_repeat.enabled = self._note_repeat != None and False
        self._note_repeat = note_repeat
        self._update_note_repeat(enabled=self.is_enabled())

    def set_pad_parameters(self, element):
        if element:
            element.reset()

    def _enable_note_repeat(self):
        self._last_record_quantization = self.song().midi_recording_quantization
        self._set_recording_quantization(False)
        self._update_note_repeat(enabled=True)

    def _disable_note_repeat(self):
        if not self.song().midi_recording_quantization and self._last_record_quantization:
            self._set_recording_quantization(self._last_record_quantization)
        self._update_note_repeat(enabled=False)

    def _set_recording_quantization(self, value):

        def doit():
            self.song().midi_recording_quantization = value

        self._tasks.parent_task.add(Task.run(doit))

    @subject_slot('selected_option')
    def _on_selected_option_changed(self, option):
        frequency = NOTE_REPEAT_FREQUENCIES[option]
        self._note_repeat.repeat_rate = 1.0 / frequency * 4.0

    def _update_note_repeat(self, enabled = False):
        self._on_selected_option_changed(self._options.selected_option)
        self._note_repeat.enabled = self.is_enabled()