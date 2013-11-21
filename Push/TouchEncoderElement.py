#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/TouchEncoderElement.py
from _Framework.EncoderElement import EncoderElement
from _Framework.SubjectSlot import subject_slot, SlotManager

class TouchEncoderObserver(object):
    """ Interface for observing the state of one or more TouchEncoderElements """

    def on_encoder_touch(self, encoder):
        pass

    def on_encoder_parameter(self, encoder):
        pass


class TouchEncoderElement(EncoderElement, SlotManager):
    """ Class representing an encoder that is touch sensitive """
    __subject_events__ = ('touch_value',)

    def __init__(self, msg_type, channel, identifier, map_mode, undo_step_handler = None, delete_handler = None, touch_button = None, *a, **k):
        super(TouchEncoderElement, self).__init__(msg_type, channel, identifier, map_mode, *a, **k)
        raise touch_button is not None or AssertionError
        self.touch_button = touch_button
        self._trigger_undo_step = False
        self._undo_step_open = False
        self._undo_step_handler = undo_step_handler
        self._delete_handler = delete_handler
        self.set_touch_button(touch_button)
        self.set_observer(None)

    def is_pressed(self):
        return self.touch_button and self.touch_button.is_pressed()

    def set_touch_button(self, touch_button):
        self.touch_button = touch_button
        self._on_touch_button.subject = touch_button

    def set_observer(self, observer):
        if observer is None:
            observer = TouchEncoderObserver()
        self._observer = observer

    def _delete_clip_automation(self):
        mapped_parameter = self.mapped_parameter()
        if mapped_parameter:
            selected_track = self._undo_step_handler.view.selected_track
            playing_slot_index = selected_track.playing_slot_index
            if playing_slot_index >= 0:
                playing_clip = selected_track.clip_slots[playing_slot_index].clip
                if playing_clip:
                    playing_clip.clear_envelope(mapped_parameter)

    @subject_slot('value')
    def _on_touch_button(self, value):
        self._trigger_undo_step = value
        if value:
            param = self.mapped_parameter()
            if self._delete_handler and self._delete_handler.is_deleting and param:
                self._delete_handler.delete_clip_envelope(param)
            else:
                self.begin_gesture()
                self._observer.on_encoder_touch(self)
                self.notify_touch_value(value)
        else:
            if self._undo_step_handler and self._undo_step_open:
                self._undo_step_handler.end_undo_step()
            self._observer.on_encoder_touch(self)
            self.notify_touch_value(value)
            self.end_gesture()

    def connect_to(self, parameter):
        if parameter != self.mapped_parameter():
            self.last_mapped_parameter = parameter
            super(TouchEncoderElement, self).connect_to(parameter)
            self._observer.on_encoder_parameter(self)

    def release_parameter(self):
        if self.mapped_parameter() != None:
            super(TouchEncoderElement, self).release_parameter()
            self._observer.on_encoder_parameter(self)

    def receive_value(self, value):
        if self._undo_step_handler and self._trigger_undo_step:
            self._undo_step_handler.begin_undo_step()
            self._trigger_undo_step = False
            self._undo_step_open = True
        super(TouchEncoderElement, self).receive_value(value)