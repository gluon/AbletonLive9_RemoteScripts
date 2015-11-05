#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/midi-remote-scripts/Push2/user_component.py
from ableton.v2.control_surface.control import ToggleButtonControl
from pushbase.user_component import UserComponentBase

class UserComponent(UserComponentBase):
    user_mode_toggle_button = ToggleButtonControl()

    @user_mode_toggle_button.toggled
    def user_mode_toggle_button(self, toggled, button):
        self.toggle_mode()