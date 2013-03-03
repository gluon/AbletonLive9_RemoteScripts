#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/SceneComponent.py
from CompoundComponent import CompoundComponent
from ClipSlotComponent import ClipSlotComponent
from Util import in_range, nop

class SceneComponent(CompoundComponent):
    """
    Class representing a scene in Live
    """
    clip_slot_component_type = ClipSlotComponent

    def __init__(self, num_slots = 0, tracks_to_use_callback = nop, *a, **k):
        raise num_slots >= 0 or AssertionError
        raise callable(tracks_to_use_callback) or AssertionError
        super(SceneComponent, self).__init__(*a, **k)
        self._scene = None
        self._clip_slots = []
        self._tracks_to_use_callback = tracks_to_use_callback
        for _ in range(num_slots):
            new_slot = self._create_clip_slot()
            self._clip_slots.append(new_slot)
            self.register_components(new_slot)

        self._launch_button = None
        self._triggered_value = 127
        self._track_offset = 0
        self._select_button = None
        self._delete_button = None

    def disconnect(self):
        super(SceneComponent, self).disconnect()
        if self._scene != None:
            self._scene.remove_is_triggered_listener(self._on_is_triggered_changed)
        if self._launch_button != None:
            self._launch_button.remove_value_listener(self._launch_value)
            self._launch_button = None

    def on_track_list_changed(self):
        self.update()

    def set_scene(self, scene):
        if scene != self._scene:
            if self._scene != None:
                self._scene.remove_is_triggered_listener(self._on_is_triggered_changed)
            self._scene = scene
            if self._scene != None:
                self._scene.add_is_triggered_listener(self._on_is_triggered_changed)
            self.update()

    def set_launch_button(self, button):
        if button != self._launch_button:
            if self._launch_button != None:
                self._launch_button.remove_value_listener(self._launch_value)
            self._launch_button = button
            if self._launch_button != None:
                self._launch_button.add_value_listener(self._launch_value)
            self.update()

    def set_select_button(self, button):
        self._select_button = button

    def set_delete_button(self, button):
        self._delete_button = button

    def set_track_offset(self, offset):
        if not offset >= 0:
            raise AssertionError
            self._track_offset = offset != self._track_offset and offset
            self.update()

    def set_triggered_value(self, value):
        value = int(value)
        raise in_range(value, 0, 128) or AssertionError
        self._triggered_value = value

    def clip_slot(self, index):
        return self._clip_slots[index]

    def update(self):
        if self._allow_updates:
            if self._scene != None and self.is_enabled():
                clip_index = self._track_offset
                tracks = self.song().tracks
                clip_slots = self._scene.clip_slots
                if self._track_offset > 0:
                    real_offset = 0
                    visible_tracks = 0
                    while visible_tracks < self._track_offset and len(tracks) > real_offset:
                        if tracks[real_offset].is_visible:
                            visible_tracks += 1
                        real_offset += 1

                    clip_index = real_offset
                for slot in self._clip_slots:
                    while len(tracks) > clip_index and not tracks[clip_index].is_visible:
                        clip_index += 1

                    if len(clip_slots) > clip_index:
                        slot.set_clip_slot(clip_slots[clip_index])
                    else:
                        slot.set_clip_slot(None)
                    clip_index += 1

                self._on_is_triggered_changed()
            else:
                for slot in self._clip_slots:
                    slot.set_clip_slot(None)

                if self.is_enabled() and self._launch_button != None:
                    self._launch_button.turn_off()
        else:
            self._update_requests += 1

    def _launch_value(self, value):
        if self.is_enabled():
            if self._select_button and self._select_button.is_pressed() and value:
                self._do_select_scene(self._scene)
            if self._delete_button and self._delete_button.is_pressed() and value:
                self._do_delete_scene(self._scene)
            elif self._scene != None:
                launched = False
                if self._launch_button.is_momentary():
                    self._scene.set_fire_button_state(value != 0)
                    launched = value != 0
                elif value != 0:
                    self._scene.fire()
                    launched = True
                if launched and self.song().select_on_launch:
                    self.song().view.selected_scene = self._scene

    def _do_select_scene(self, scene):
        if self._scene != None:
            view = self.song().view
            if view.selected_scene != self._scene:
                view.selected_scene = self._scene

    def _do_delete_scene(self, scene):
        try:
            if self._scene:
                song = self.song()
                song.delete_scene(list(song.scenes).index(self._scene))
        except RuntimeError:
            pass

    def _on_is_triggered_changed(self):
        if not self._scene != None:
            raise AssertionError
            if self.is_enabled() and self._launch_button != None:
                self._scene.is_triggered and self._launch_button.send_value(self._triggered_value)
            else:
                self._launch_button.turn_off()

    def _create_clip_slot(self):
        return self.clip_slot_component_type()