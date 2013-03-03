#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/AccentComponent.py
from _Framework.ModesComponent import ModesComponent

class AccentComponent(ModesComponent):

    def __init__(self, full_velocity, *a, **k):
        super(AccentComponent, self).__init__(*a, **k)
        self._full_velocity = full_velocity
        self.add_mode('disabled', None)
        self.add_mode('enabled', (self._on_accent_on, self._on_accent_off), 'DefaultButton.On')
        self.selected_mode = 'disabled'

    @property
    def activated(self):
        return self._full_velocity.enabled

    def _on_accent_off(self):
        self._full_velocity.enabled = False

    def _on_accent_on(self):
        self._full_velocity.enabled = True