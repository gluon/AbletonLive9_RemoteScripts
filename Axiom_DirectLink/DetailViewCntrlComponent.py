#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Axiom_DirectLink/DetailViewCntrlComponent.py
import Live
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.ButtonElement import ButtonElement

class DetailViewCntrlComponent(ControlSurfaceComponent):
    """ Component that can navigate the selection of devices """

    def __init__(self):
        ControlSurfaceComponent.__init__(self)
        self._left_button = None
        self._right_button = None

    def disconnect(self):
        if self._left_button != None:
            self._left_button.remove_value_listener(self._nav_value)
            self._left_button = None
        if self._right_button != None:
            self._right_button.remove_value_listener(self._nav_value)
            self._right_button = None

    def set_device_nav_buttons(self, left_button, right_button):
        if not (left_button == None or isinstance(left_button, ButtonElement)):
            raise AssertionError
            if not (right_button == None or isinstance(right_button, ButtonElement)):
                raise AssertionError
                identify_sender = True
                if self._left_button != None:
                    self._left_button.remove_value_listener(self._nav_value)
                self._left_button = left_button
                if self._left_button != None:
                    self._left_button.add_value_listener(self._nav_value, identify_sender)
                self._right_button != None and self._right_button.remove_value_listener(self._nav_value)
            self._right_button = right_button
            self._right_button != None and self._right_button.add_value_listener(self._nav_value, identify_sender)
        self.update()

    def on_enabled_changed(self):
        self.update()

    def update(self):
        super(DetailViewCntrlComponent, self).update()
        if self.is_enabled():
            if self._left_button != None:
                self._left_button.turn_off()
            if self._right_button != None:
                self._right_button.turn_off()

    def _nav_value(self, value, sender):
        raise sender != None and sender in (self._left_button, self._right_button) or AssertionError
        if self.is_enabled():
            if not sender.is_momentary() or value != 0:
                modifier_pressed = True
                if not self.application().view.is_view_visible('Detail') or not self.application().view.is_view_visible('Detail/DeviceChain'):
                    self.application().view.show_view('Detail')
                    self.application().view.show_view('Detail/DeviceChain')
                else:
                    direction = Live.Application.Application.View.NavDirection.left
                    if sender == self._right_button:
                        direction = Live.Application.Application.View.NavDirection.right
                    self.application().view.scroll_view(direction, 'Detail/DeviceChain', not modifier_pressed)