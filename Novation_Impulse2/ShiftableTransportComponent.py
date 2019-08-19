#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Novation_Impulse/ShiftableTransportComponent.py
import Live
NavDirection = Live.Application.Application.View.NavDirection
from _Framework.ButtonElement import ButtonElement
from _Framework.TransportComponent import TransportComponent
from _Framework.ToggleComponent import ToggleComponent

class ShiftableTransportComponent(TransportComponent):
    """ Special transport class handling the seek buttons differently based on a shift button"""

    def __init__(self, c_instance, session, parent, ffwd_button, rwd_button):
        TransportComponent.__init__(self)
        self.c_instance = c_instance
        self._mixer9_button = None
        self._play_button = None
        self._record_button = None
        self._session = session
        self._parent = parent
        self._ffwd_button = ffwd_button
        self._rwd_button = rwd_button
        song = self.song()
#        self._automation_toggle= self.register_component(ToggleComponent('session_automation_record', song))
        self._automation_toggle, self._re_enable_automation_toggle, self._delete_automation = self.register_components(ToggleComponent('session_automation_record', song), ToggleComponent('re_enable_automation_enabled', song, read_only=True), ToggleComponent('has_envelopes', None, read_only=True))



    def disconnect(self):
        if self._play_button != None:
            self._play_button.remove_value_listener(self._play_pressed)
            self._play_button = None

        TransportComponent.disconnect(self)

    def set_stop_buttonOnInit(self, button):
        self.log("set_stop_buttonOnInit 1")
        self._stop_button = button
        self.set_stop_button(self._stop_button)
        self.log("set_stopbuttonOnInit 2")


    def set_record_buttonOnInit(self, button):
        self.log("set_record_buttonOnInit 1")
        self._record_button = button
        self.set_record_button(self._record_button)
        self.log("set_record_buttonOnInit 2")

    def set_mixer9_button(self, button):
        self.log("set_mixer9_button 1")
        self._mixer9_button = button
        self.set_overdub_button(self._mixer9_button)
        #self._automation_toggle.set_toggle_button(self._mixer9_button)
        self.log("set_mixer9_button 2")


    def set_play_button(self, button):
        self._play_button = button
        self._play_button.add_value_listener(self._play_pressed)
        self._play_toggle.set_toggle_button(button)

    def _play_pressed(self, value):
        self.log("_play_pressed " + str(value))
        if not value in range(128):
            raise AssertionError
        if self._parent.shift_pressed:
            if value != 0:
                if self.song().can_undo:
                    #todo: add message
                    self.song().undo()
                    self.log("undoing")
                    self._parent._set_string_to_display('undoing')

                else:
                    #todo: add message
                    self._parent._set_string_to_display('cannot undo')


    def _shift_button_handler(self, value):
        self.log("shift handler transport component : " + str(value))
        if not value in range(128):
            raise AssertionError
        self.log("shift handler transport component 2")
        if self._parent.shift_pressed:
            self._play_toggle.set_toggle_button(None)
            self._session.set_stop_all_clips_button(self._stop_button)
            self.set_stop_button(None)
            self.set_overdub_button(None)
            self._automation_toggle.set_toggle_button(self._mixer9_button)
            self.set_metronome_button(self._record_button)
            self.set_record_button(None)

        else:
            self._play_toggle.set_toggle_button(self._play_button)
            self._session.set_stop_all_clips_button(None)
            self.set_stop_button(self._stop_button)
            self.set_overdub_button(self._mixer9_button)
            self._automation_toggle.set_toggle_button(None)
            self.set_metronome_button(None)
            self.set_record_button(self._record_button)

        self.log("shift handler transport component 3")


    def _ffwd_value(self, value):
        self.log("ffwd handler main" + str(value))
        if not self._ffwd_button != None:
            raise AssertionError
        if not value in range(128):
            raise AssertionError
        else:
            if self._parent.shift_pressed:
                self.log("ffwd shifted handler")
#                    self.song().current_song_time = self.song().last_event_time
                if value == 1:
                    self._scroll_device_chain(NavDirection.right)
            else:
                self.log("ffwd normal handler")
                TransportComponent._ffwd_value(self, value)

    def _rwd_value(self, value):
        self.log("rwd handler main" + str(value))
        if not self._rwd_button != None:
            raise AssertionError
        if not value in range(128):
            raise AssertionError
        else:
            if self._parent.shift_pressed:
                self.log("rwd shifted handler")
#                    self.song().current_song_time = 0.0
                if value == 1:
                    self._scroll_device_chain(NavDirection.left)
            else:
                self.log("rwd normal handler")
                TransportComponent._rwd_value(self, value)


    def _scroll_device_chain(self, direction):
        self.log("_scroll_device_chain 1")
        view = self._parent.application().view
        self.log("_scroll_device_chain 2")
        if not view.is_view_visible('Detail') or not view.is_view_visible('Detail/DeviceChain'):
            view.show_view('Detail')
            view.show_view('Detail/DeviceChain')
        else:
            view.scroll_view(direction, 'Detail/DeviceChain', False)

    def log(self, message):
        pass
#       self.c_instance.log_message(message)

