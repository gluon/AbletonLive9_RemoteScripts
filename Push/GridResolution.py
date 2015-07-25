#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/GridResolution.py
import Live
GridQuantization = Live.Clip.GridQuantization
from _Framework.SubjectSlot import subject_slot, SlotManager, Subject
from _Framework.Util import product
QUANTIZATION_FACTOR = 24
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
DEFAULT_INDEX = 3

class GridResolution(SlotManager, Subject):
    __subject_events__ = ('index',)

    def __init__(self, *a, **k):
        super(GridResolution, self).__init__(*a, **k)
        self._index = DEFAULT_INDEX
        self._quantization_buttons = []
        self._quantization_button_slots = self.register_slot_manager()

    def _get_index(self):
        return self._index

    def _set_index(self, index):
        self._index = index
        self.notify_index()

    index = property(_get_index, _set_index)

    @property
    def step_length(self):
        return QUANTIZATION_LIST[self._index] / QUANTIZATION_FACTOR

    @property
    def clip_grid(self):
        return CLIP_VIEW_GRID_LIST[self._index]

    @property
    def clip_length(self):
        return CLIP_LENGTH_LIST[self._index]

    def set_buttons(self, buttons):
        self._quantization_button_slots.disconnect()
        self._quantization_buttons = buttons or []
        for button in self._quantization_buttons:
            if button:
                button.set_on_off_values('NoteEditor.QuantizationSelected', 'NoteEditor.QuantizationUnselected')
            self._quantization_button_slots.register_slot(button, self._on_quantization_button_value, 'value', dict(identify_sender=True))

        self._update_quantization_buttons()

    @subject_slot('value')
    def _on_quantization_button_value(self, value, sender):
        if value or not sender.is_momentary():
            self.index = list(self._quantization_buttons).index(sender)
            self._update_quantization_buttons()

    def _update_quantization_buttons(self):
        for index, button in enumerate(self._quantization_buttons):
            if button != None:
                if index is self.index:
                    button.turn_on()
                else:
                    button.turn_off()

    def update(self):
        self._update_quantization_buttons()