#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/AccentComponent.py
from _Framework.ModesComponent import ModesComponent

class DummyFullVelocity(object):
    enabled = False


class AccentComponent(ModesComponent):

    def __init__(self, *a, **k):
        super(AccentComponent, self).__init__(*a, **k)
        self._full_velocity = None
        self.add_mode('disabled', None)
        self.add_mode('enabled', (self._on_accent_on, self._on_accent_off), 'DefaultButton.On')
        self.selected_mode = 'disabled'
        self.set_full_velocity(None)

    def set_full_velocity(self, full_velocity):
        if not full_velocity:
            full_velocity = DummyFullVelocity()
            self._full_velocity.enabled = self._full_velocity != None and False
        self._full_velocity = full_velocity
        self._full_velocity.enabled = self.selected_mode == 'enabled'

    @property
    def activated(self):
        return self._full_velocity.enabled

    def _on_accent_off(self):
        self._full_velocity.enabled = False

    def _on_accent_on(self):
        self._full_velocity.enabled = True