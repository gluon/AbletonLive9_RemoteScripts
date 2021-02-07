# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/session_recording.py
# Compiled at: 2016-09-29 19:13:24
from __future__ import absolute_import, print_function
from ableton.v2.base import nop
from pushbase.session_recording_component import FixedLengthSessionRecordingComponent

class SessionRecordingComponent(FixedLengthSessionRecordingComponent):

    def __init__(self, *a, **k):
        super(SessionRecordingComponent, self).__init__(*a, **k)
        self._on_record_button_pressed = nop
        self._on_arrangement_record_button_pressed = nop
        self.set_trigger_recording_on_release(not any((
         self._record_button.is_pressed,
         self.arrangement_record_button.is_pressed)))

    def set_trigger_recording_on_release(self, trigger_recording):
        self._should_trigger_recording = trigger_recording

    def _on_record_button_released(self):
        self._trigger_recording_action(self._trigger_recording)

    def _on_arrangement_record_button_released(self):
        self._trigger_recording_action(self._toggle_arrangement_recording)

    def _trigger_recording_action(self, recording_action):
        if self._should_trigger_recording:
            recording_action()
        self._should_trigger_recording = True