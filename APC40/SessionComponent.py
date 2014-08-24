#Embedded file name: /Users/versonator/Jenkins/live/Binary/Core_Release_64_static/midi-remote-scripts/APC40/SessionComponent.py
from _Framework.Control import ButtonControl
from _APC.SessionComponent import SessionComponent as SessionComponentBase

class SessionComponent(SessionComponentBase):
    """ Special SessionComponent with a button (pedal) to fire the selected clip slot """
    slot_launch_button = ButtonControl()
    selected_scene_launch_button = ButtonControl()

    def set_slot_launch_button(self, button):
        self.slot_launch_button.set_control_element(button)

    @slot_launch_button.pressed
    def slot_launch_button(self, button):
        clip_slot = self.song().view.highlighted_clip_slot
        if clip_slot:
            clip_slot.fire()

    def set_selected_scene_launch_button(self, button):
        self.selected_scene_launch_button.set_control_element(button)

    @selected_scene_launch_button.pressed
    def selected_scene_launch_button(self, button):
        scene = self.song().view.selected_scene
        if scene:
            scene.fire()