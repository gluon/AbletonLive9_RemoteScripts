#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Novation_Impulse/TransportViewModeSelector.py
import Live
from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.TransportComponent import TransportComponent
from _Framework.SessionComponent import SessionComponent

class TransportViewModeSelector(ModeSelectorComponent):
    """ Class that reassigns specific buttons based on the views visible in Live """

    def __init__(self, parent, c_instance, transport, session, ffwd_button, rwd_button, loop_button):
        if not isinstance(transport, TransportComponent):
            raise AssertionError
        if not isinstance(session, SessionComponent):
            raise AssertionError
        if not isinstance(ffwd_button, ButtonElement):
            raise AssertionError
        if not isinstance(rwd_button, ButtonElement):
            raise AssertionError
        if not isinstance(loop_button, ButtonElement):
            raise AssertionError
        ModeSelectorComponent.__init__(self)
        self._parent = parent
        self.c_instance = c_instance
        self._transport = transport
        self._session = session
        self._ffwd_button = ffwd_button
        self._rwd_button = rwd_button
        self._loop_button = loop_button
        self._shift_pressed = False
        self.application().view.add_is_view_visible_listener('Session', self._on_view_changed)
        self._loop_button.add_value_listener(self._loop_pressed)
        self.update()

    def disconnect(self):
        ModeSelectorComponent.disconnect(self)
        self._transport = None
        self._session = None
        self._ffwd_button = None
        self._rwd_button = None
        self._loop_button.remove_value_listener(self._loop_pressed)
        self._loop_button = None
        self.application().view.remove_is_view_visible_listener('Session', self._on_view_changed)

    def update(self):
        if self.is_enabled():
            self.log("transportviewselctor_update ")
            if self._shift_pressed:
                #shift plus loop will make an alternative control mode for everything
                self._session.selected_scene().set_launch_button(None)
                self._transport.set_loop_button(None)
            else:
                if self._mode_index == 0:
                    self._transport.set_loop_button(self._loop_button)
                    self._session.selected_scene().set_launch_button(None)
                else:
                    self._transport.set_loop_button(None)
                    self._session.selected_scene().set_launch_button(self._loop_button)
            # hack as we have nadler for fwd that changes devices
            if self._mode_index == 0 or self._shift_pressed:
                self._transport.set_seek_buttons(self._ffwd_button, self._rwd_button)
                self._session.set_select_buttons(None, None)
            else:
                self._transport.set_seek_buttons(None, None)
                self._session.set_select_buttons(self._ffwd_button, self._rwd_button)

    def _on_view_changed(self):
        if self.application().view.is_view_visible('Session'):
            self._mode_index = 1
        else:
            self._mode_index = 0
        self.update()


    def _shift_button_handler(self, value):
        self.log("shift handler transport component " + str(value))
        if not value in range(128):
            raise AssertionError
        self.log("shift handler 2")
        self._shift_pressed = self.is_enabled() and self._parent.shift_pressed
        self.update()
        self.log("shift handler 3")

    def _loop_pressed(self, value):
        self.log("loop handler transport component " + str(value))
        
        if (value == 1) and (self._shift_pressed):
            self._parent.flipAlternativeButtonMode()


    def log(self, message):
        pass
#        self.c_instance.log_message(message)

