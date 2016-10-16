#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/session_recording.py
from __future__ import absolute_import, print_function
from pushbase.session_recording_component import FixedLengthSessionRecordingComponent

class SessionRecordingComponent(FixedLengthSessionRecordingComponent):

    def __init__(self, *a, **k):
        super(SessionRecordingComponent, self).__init__(*a, **k)
        self.set_trigger_recording_on_release(not self._record_button.is_pressed)

    def set_trigger_recording_on_release(self, trigger_recording):
        self._should_trigger_recording = trigger_recording

    def _on_record_button_pressed(self):
        pass

    def _on_record_button_released(self):
        if self._should_trigger_recording:
            self._trigger_recording()
        self._should_trigger_recording = True