#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/AxiomPro/NotifyingMixerComponent.py
from _Framework.MixerComponent import MixerComponent
from _Framework.PhysicalDisplayElement import PhysicalDisplayElement

class NotifyingMixerComponent(MixerComponent):
    """ Special mixer class that notifies an observer when reassigning parameters """

    def __init__(self, num_tracks):
        self._update_callback = None
        MixerComponent.__init__(self, num_tracks)
        self._bank_display = None

    def disconnect(self):
        MixerComponent.disconnect(self)
        self._update_callback = None

    def set_update_callback(self, callback):
        raise callback == None or dir(callback).count('im_func') is 1 or AssertionError
        self._update_callback = callback

    def set_bank_display(self, display):
        raise isinstance(display, PhysicalDisplayElement) or AssertionError
        self._bank_display = display

    def on_selected_track_changed(self):
        MixerComponent.on_selected_track_changed(self)
        selected_track = self.song().view.selected_track
        num_strips = len(self._channel_strips)
        track_index = selected_track in self._tracks_to_use() and list(self._tracks_to_use()).index(selected_track)
        new_offset = track_index - track_index % num_strips
        if not new_offset / num_strips == int(new_offset / num_strips):
            raise AssertionError
            self.set_track_offset(new_offset)

    def update(self):
        super(NotifyingMixerComponent, self).update()
        if self._update_callback != None:
            self._update_callback()

    def _tracks_to_use(self):
        return tuple(self.song().visible_tracks) + tuple(self.song().return_tracks)

    def _reassign_tracks(self):
        MixerComponent._reassign_tracks(self)
        if self._update_callback != None:
            self._update_callback()

    def _bank_up_value(self, value):
        old_offset = int(self._track_offset)
        MixerComponent._bank_up_value(self, value)
        if self._bank_display != None:
            if value != 0 and old_offset != self._track_offset:
                min_track = self._track_offset + 1
                max_track = min(len(self._tracks_to_use()), min_track + len(self._channel_strips))
                self._bank_display.display_message('Tracks ' + str(min_track) + ' - ' + str(max_track))
            else:
                self._bank_display.update()

    def _bank_down_value(self, value):
        old_offset = int(self._track_offset)
        MixerComponent._bank_down_value(self, value)
        if self._bank_display != None:
            if value != 0 and old_offset != self._track_offset:
                min_track = self._track_offset + 1
                max_track = min(len(self._tracks_to_use()), min_track + len(self._channel_strips))
                self._bank_display.display_message('Tracks ' + str(min_track) + ' - ' + str(max_track))
            else:
                self._bank_display.update()