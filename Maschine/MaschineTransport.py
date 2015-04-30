#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\MaschineTransport.py
import Live
from _Framework.CompoundComponent import CompoundComponent
from _Framework.ToggleComponent import ToggleComponent
from MIDI_Map import *

class MaschineTransport(CompoundComponent):
    """
    Class encapsulating all functions in Live's transport section.
    """

    def __init__(self, *a, **k):
        super(MaschineTransport, self).__init__(*a, **k)
        song = self.song()
        self._automation_toggle, self._re_enable_automation_toggle, self._delete_automation, self._arrangement_overdub_toggle, self._back_to_arrange_toggle = self.register_components(ToggleComponent('session_automation_record', song), ToggleComponent('re_enable_automation_enabled', song, read_only=True), ToggleComponent('has_envelopes', None, read_only=True), ToggleComponent('arrangement_overdub', song), ToggleComponent('back_to_arranger', song))

    def set_back_arrange_button(self, button):
        self._back_to_arrange_toggle.set_toggle_button(button)

    def set_session_auto_button(self, button):
        self._automation_toggle.set_toggle_button(button)

    def set_arrangement_overdub_button(self, button):
        self._arrangement_overdub_toggle.set_toggle_button(button)

    def update(self):
        pass