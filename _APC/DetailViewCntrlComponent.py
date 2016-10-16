#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_APC/DetailViewCntrlComponent.py
import Live
NavDirection = Live.Application.Application.View.NavDirection
from _Framework.Control import ButtonControl, ToggleButtonControl
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.SubjectSlot import subject_slot
from _Framework import Task
SHOW_PLAYING_CLIP_DELAY = 0.5

class DetailViewCntrlComponent(ControlSurfaceComponent):
    """
    Component that can toggle the device chain- and clip view
    of the selected track
    """
    device_clip_toggle_button = ButtonControl(color='DefaultButton.Off')
    device_nav_left_button = ButtonControl(color='DefaultButton.Off')
    device_nav_right_button = ButtonControl(color='DefaultButton.Off')
    detail_toggle_button = ToggleButtonControl()

    def __init__(self, *a, **k):
        super(DetailViewCntrlComponent, self).__init__(*a, **k)
        self._detail_view_visibility_changed.subject = self.application().view
        self._detail_view_visibility_changed()
        self._go_to_playing_clip_task = self._tasks.add(Task.sequence(Task.wait(SHOW_PLAYING_CLIP_DELAY), Task.run(self._go_to_playing_clip)))
        self._go_to_playing_clip_task.kill()
        self.set_device_clip_toggle_button = self.device_clip_toggle_button.set_control_element
        self.set_detail_toggle_button = self.detail_toggle_button.set_control_element

    def set_device_nav_buttons(self, left_button, right_button):
        self.set_device_nav_left_button(left_button)
        self.set_device_nav_right_button(right_button)

    @device_clip_toggle_button.pressed
    def device_clip_toggle_button(self, button):
        if not self.application().view.is_view_visible('Detail'):
            self.application().view.show_view('Detail')
        if not self.application().view.is_view_visible('Detail/DeviceChain'):
            self.application().view.show_view('Detail/DeviceChain')
        else:
            self.application().view.show_view('Detail/Clip')
        self._go_to_playing_clip_task.restart()

    @device_clip_toggle_button.released
    def device_clip_toggle_button(self, button):
        self._go_to_playing_clip_task.kill()

    @device_nav_left_button.pressed
    def device_nav_left_button(self, value):
        self._scroll_device_chain(NavDirection.left)

    @device_nav_right_button.pressed
    def device_nav_right_button(self, value):
        self._scroll_device_chain(NavDirection.right)

    def _scroll_device_chain(self, direction):
        view = self.application().view
        if not view.is_view_visible('Detail') or not view.is_view_visible('Detail/DeviceChain'):
            view.show_view('Detail')
            view.show_view('Detail/DeviceChain')
        else:
            view.scroll_view(direction, 'Detail/DeviceChain', False)

    def _go_to_playing_clip(self):
        song = self.song()
        playing_slot_index = song.view.selected_track.playing_slot_index
        if playing_slot_index > -1:
            song.view.selected_scene = song.scenes[playing_slot_index]
            if song.view.highlighted_clip_slot.has_clip:
                self.application().view.show_view('Detail/Clip')

    @detail_toggle_button.toggled
    def detail_toggle_button(self, is_toggled, button):
        if is_toggled:
            self.application().view.show_view('Detail')
        else:
            self.application().view.hide_view('Detail')

    @subject_slot('is_view_visible', 'Detail')
    def _detail_view_visibility_changed(self):
        self.detail_toggle_button.is_toggled = self.application().view.is_view_visible('Detail')

    def show_view(self, view):
        app_view = self.application().view
        try:
            if view == 'Detail/DeviceChain' or 'Detail/Clip':
                if not app_view.is_view_visible('Detail'):
                    app_view.show_view('Detail')
            if not app_view.is_view_visible(view):
                app_view.show_view(view)
        except RuntimeError:
            pass