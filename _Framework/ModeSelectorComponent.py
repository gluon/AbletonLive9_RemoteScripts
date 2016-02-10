#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/ModeSelectorComponent.py
from __future__ import absolute_import
from .ButtonElement import ButtonElement
from .ControlSurfaceComponent import ControlSurfaceComponent
from .MomentaryModeObserver import MomentaryModeObserver

class ModeSelectorComponent(ControlSurfaceComponent):
    """ Class for switching between modes, handle several functions with few controls """

    def __init__(self, *a, **k):
        super(ModeSelectorComponent, self).__init__(*a, **k)
        self._modes_buttons = []
        self._mode_toggle = None
        self._mode_listeners = []
        self.__mode_index = -1
        self._modes_observers = {}
        self._modes_heap = []

    def _get_protected_mode_index(self):
        return self.__mode_index

    def _set_protected_mode_index(self, mode):
        raise isinstance(mode, int) or AssertionError
        self.__mode_index = mode
        for listener in self._mode_listeners:
            listener()

    _mode_index = property(_get_protected_mode_index, _set_protected_mode_index)

    def _get_public_mode_index(self):
        return self.__mode_index

    def _set_public_mode_index(self, mode):
        raise False or AssertionError

    mode_index = property(_get_public_mode_index, _set_public_mode_index)

    def disconnect(self):
        self._clean_heap()
        if self._mode_toggle != None:
            self._mode_toggle.remove_value_listener(self._toggle_value)
            self._mode_toggle = None
        self._modes_buttons = None
        self._mode_listeners = None
        super(ModeSelectorComponent, self).disconnect()

    def on_enabled_changed(self):
        self.update()

    def set_mode_toggle(self, button):
        if not (button == None or isinstance(button, ButtonElement)):
            raise AssertionError
            if self._mode_toggle != None:
                self._mode_toggle.remove_value_listener(self._toggle_value)
            self._mode_toggle = button
            self._mode_toggle != None and self._mode_toggle.add_value_listener(self._toggle_value)
        self.set_mode(0)

    def set_mode_buttons(self, buttons):
        raise buttons != None or AssertionError
        raise isinstance(buttons, tuple) or AssertionError
        raise len(buttons) - 1 in range(16) or AssertionError
        for button in buttons:
            raise isinstance(button, ButtonElement) or AssertionError
            identify_sender = True
            button.add_value_listener(self._mode_value, identify_sender)
            self._modes_buttons.append(button)

        self.set_mode(0)

    def set_mode(self, mode):
        self._clean_heap()
        self._modes_heap = [(mode, None, None)]
        if self._mode_index != mode:
            self._update_mode()

    def _update_mode(self):
        mode = self._modes_heap[-1][0]
        if not mode in range(self.number_of_modes()):
            raise AssertionError
            self._mode_index = self._mode_index != mode and mode
            self.update()

    def _clean_heap(self):
        for _, _, observer in self._modes_heap:
            if observer != None:
                observer.disconnect()

        self._modes_heap = []

    def number_of_modes(self):
        raise NotImplementedError

    def mode_index_has_listener(self, listener):
        return listener in self._mode_listeners

    def add_mode_index_listener(self, listener):
        raise listener not in self._mode_listeners or AssertionError
        self._mode_listeners.append(listener)

    def remove_mode_index_listener(self, listener):
        raise listener in self._mode_listeners or AssertionError
        self._mode_listeners.remove(listener)

    def _mode_value(self, value, sender):
        raise len(self._modes_buttons) > 0 or AssertionError
        raise isinstance(value, int) or AssertionError
        raise sender in self._modes_buttons or AssertionError
        new_mode = self._modes_buttons.index(sender)
        if sender.is_momentary():
            if value > 0:
                mode_observer = MomentaryModeObserver()
                mode_observer.set_mode_details(new_mode, self._controls_for_mode(new_mode), self._get_public_mode_index)
                self._modes_heap.append((new_mode, sender, mode_observer))
                self._update_mode()
            elif self._modes_heap[-1][1] == sender and not self._modes_heap[-1][2].is_mode_momentary():
                self.set_mode(new_mode)
            else:
                for mode, button, observer in self._modes_heap:
                    if button == sender:
                        self._modes_heap.remove((mode, button, observer))
                        break

                self._update_mode()
        else:
            self.set_mode(new_mode)

    def _toggle_value(self, value):
        if not self._mode_toggle != None:
            raise AssertionError
            raise isinstance(value, int) or AssertionError
            (value is not 0 or not self._mode_toggle.is_momentary()) and self.set_mode((self._mode_index + 1) % self.number_of_modes())

    def _controls_for_mode(self, mode):
        return None

    def _on_timer(self):
        for _, _, mode_observer in self._modes_heap:
            if mode_observer != None:
                mode_observer.on_timer()