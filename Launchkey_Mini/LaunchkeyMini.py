#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchkey_Mini/LaunchkeyMini.py
from Launchkey.Launchkey import Launchkey, LaunchkeyControlFactory, make_button

class LaunchkeyMiniControlFactory(LaunchkeyControlFactory):

    def create_next_track_button(self):
        return make_button(107, 'Next_Track_Button')

    def create_prev_track_button(self):
        return make_button(106, 'Prev_Track_Button')


class LaunchkeyMini(Launchkey):
    """ Script for Novation's Launchkey Mini keyboard """

    def __init__(self, c_instance):
        super(LaunchkeyMini, self).__init__(c_instance, control_factory=LaunchkeyMiniControlFactory(), identity_response=(240, 126, 127, 6, 2, 0, 32, 41, 53, 0, 0))
        self._suggested_input_port = 'LK Mini InControl'
        self._suggested_output_port = 'LK Mini InControl'

    def _setup_navigation(self):
        super(LaunchkeyMini, self)._setup_navigation()
        self._next_scene_button = make_button(105, 'Next_Scene_Button')
        self._prev_scene_button = make_button(104, 'Prev_Scene_Button')
        self._session_navigation.set_next_scene_button(self._next_scene_button)
        self._session_navigation.set_prev_scene_button(self._prev_scene_button)

    def _setup_transport(self):
        pass