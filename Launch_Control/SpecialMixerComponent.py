#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_static/midi-remote-scripts/Launch_Control/SpecialMixerComponent.py
from _Framework.MixerComponent import MixerComponent
from _Framework.ModesComponent import ModesComponent, LayerMode, LatchingBehaviour
from _Framework.SubjectSlot import subject_slot
from _Framework.Util import clamp

class SendSelectButtonBehaviour(LatchingBehaviour):

    def __init__(self, mixer = None, *a, **k):
        super(SendSelectButtonBehaviour, self).__init__(*a, **k)
        self._mixer = mixer

    def press_immediate(self, component, mode):
        if component.selected_mode == 'sends':
            self._mixer.selected_send_index += 2
        else:
            super(SendSelectButtonBehaviour, self).press_immediate(component, mode)


class SpecialMixerComponent(MixerComponent):
    __subject_events__ = ('selected_send_index', 'selected_mixer_mode')

    def __init__(self, num_tracks, mode_layer = None, pan_volume_layer = None, sends_layer = None, *a, **k):
        super(SpecialMixerComponent, self).__init__(num_tracks, *a, **k)
        self.set_enabled(False)
        self._send_controls = None
        self._selected_send_index = 0
        self._modes = self.register_component(ModesComponent())
        self._modes.add_mode('pan_volume', [LayerMode(self, pan_volume_layer)])
        self._modes.add_mode('sends', [LayerMode(self, sends_layer)], behaviour=SendSelectButtonBehaviour(self))
        self._modes.selected_mode = 'pan_volume'
        self._modes.layer = mode_layer
        self._on_visible_tracks.subject = self.song()
        self._on_selected_mixer_mode.subject = self._modes

    def _get_selected_send_index(self):
        return self._selected_send_index

    def _set_selected_send_index(self, value):
        self._selected_send_index = value
        self._cycle_send_index()
        self._update_send_controls()
        self.notify_selected_send_index(self._selected_send_index)

    selected_send_index = property(_get_selected_send_index, _set_selected_send_index)

    def set_pan_controls(self, controls):
        for control, channel_strip in map(None, controls or [], self._channel_strips):
            if channel_strip:
                channel_strip.set_pan_control(control)

    def set_volume_controls(self, controls):
        for control, channel_strip in map(None, controls or [], self._channel_strips):
            if channel_strip:
                channel_strip.set_volume_control(control)

    def set_sends_controls(self, controls):
        self._send_controls = controls
        self._update_send_controls()

    @property
    def num_sends(self):
        return len(self.song().tracks[0].mixer_device.sends)

    def _cycle_send_index(self):
        if self._selected_send_index >= self.num_sends:
            self._selected_send_index = 0

    def _clamp_send_index(self):
        self._selected_send_index = clamp(self._selected_send_index, 0, self.num_sends - 1)
        if self._selected_send_index % 2 > 0:
            self._selected_send_index -= 1

    def _update_send_controls(self):
        for index, channel_strip in enumerate(self._channel_strips):
            send_controls = [ self._send_controls.get_button(index, i) for i in (1, 0) ] if self._send_controls else [None]
            skipped_sends = [ None for _ in xrange(self._selected_send_index) ]
            channel_strip.set_send_controls(skipped_sends + send_controls)

    @subject_slot('visible_tracks')
    def _on_visible_tracks(self):
        self._clamp_send_index()
        self._update_send_controls()

    @subject_slot('selected_mode')
    def _on_selected_mixer_mode(self, mode):
        self.notify_selected_mixer_mode(mode)