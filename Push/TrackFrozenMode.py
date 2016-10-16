#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push/TrackFrozenMode.py
from _Framework.ModesComponent import ModesComponent
from _Framework.SubjectSlot import subject_slot

class TrackFrozenModesComponent(ModesComponent):

    def __init__(self, default_mode = None, frozen_mode = None, *a, **k):
        super(TrackFrozenModesComponent, self).__init__(*a, **k)
        raise default_mode is not None or AssertionError
        if not frozen_mode is not None:
            raise AssertionError
            self.add_mode('default', default_mode)
            self.add_mode('frozen', frozen_mode)
            self._on_selected_track_is_frozen_changed.subject = self.song().view
            self.is_enabled() and self._update_selected_mode()

    def _update_selected_mode(self):
        self.selected_mode = 'frozen' if self.song().view.selected_track.is_frozen else 'default'

    @subject_slot('selected_track.is_frozen')
    def _on_selected_track_is_frozen_changed(self):
        self._update_selected_mode()

    def update(self):
        super(TrackFrozenModesComponent, self).update()
        if self.is_enabled():
            self._update_selected_mode()