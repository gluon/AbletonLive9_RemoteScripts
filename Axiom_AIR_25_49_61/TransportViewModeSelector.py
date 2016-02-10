#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Axiom_AIR_25_49_61/TransportViewModeSelector.py
from _Framework.ModeSelectorComponent import ModeSelectorComponent

class TransportViewModeSelector(ModeSelectorComponent):
    """ Class that reassigns specific buttons based on the views visible in Live """

    def __init__(self, transport, session, ffwd_button, rwd_button, loop_button):
        ModeSelectorComponent.__init__(self)
        self._transport = transport
        self._session = session
        self._ffwd_button = ffwd_button
        self._rwd_button = rwd_button
        self._loop_button = loop_button
        self.application().view.add_is_view_visible_listener('Session', self._on_view_changed)
        self._on_view_changed()

    def disconnect(self):
        ModeSelectorComponent.disconnect(self)
        self._transport = None
        self._session = None
        self._ffwd_button = None
        self._rwd_button = None
        self._loop_button = None
        self.application().view.remove_is_view_visible_listener('Session', self._on_view_changed)

    def update(self):
        super(TransportViewModeSelector, self).update()
        if self.is_enabled():
            if self._mode_index == 0:
                self._transport.set_seek_buttons(self._ffwd_button, self._rwd_button)
                self._transport.set_loop_button(self._loop_button)
                self._session.set_select_buttons(None, None)
                self._session.selected_scene().set_launch_button(None)
            else:
                self._transport.set_seek_buttons(None, None)
                self._transport.set_loop_button(None)
                self._session.set_select_buttons(self._ffwd_button, self._rwd_button)
                self._session.selected_scene().set_launch_button(self._loop_button)

    def _on_view_changed(self):
        if self.application().view.is_view_visible('Session'):
            self._mode_index = 1
        else:
            self._mode_index = 0
        self.update()