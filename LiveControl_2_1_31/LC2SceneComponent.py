#Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/LiveControl_2_1_31/LC2SceneComponent.py
from _Framework.SceneComponent import SceneComponent
from LC2ClipSlotComponent import LC2ClipSlotComponent
from LC2Sysex import LC2Sysex

class LC2SceneComponent(SceneComponent):

    def set_get_offsets(func):
        LC2SceneComponent._get_offset = func

    set_get_offsets = staticmethod(set_get_offsets)

    def release_attributes():
        LC2SceneComponent._get_offset = None

    release_attributes = staticmethod(release_attributes)

    def __init__(self, num_tracks, tracks_to_use, id):
        self._scene_id = id
        SceneComponent.__init__(self, num_tracks, tracks_to_use)

    def disconnect(self):
        if self._scene is not None:
            try:
                self._scene.remove_color_listener(self._on_color_changed)
                self._scene.remove_name_listener(self._on_name_changed)
            except:
                pass

        SceneComponent.disconnect(self)

    def _send_init(self):
        self._send_state()
        for clip in self._clip_slots:
            clip._send_state()

    def _create_clip_slot(self):
        return LC2ClipSlotComponent(len(self._clip_slots), self._scene_id)

    if not LC2Sysex.l9():

        def set_scene(self, scene):
            if scene is not None:
                id = list(self.song().scenes).index(scene)
            else:
                id = -1
            if self._scene is not None:
                try:
                    self._scene.remove_color_listener(self._on_color_changed)
                    self._scene.remove_name_listener(self._on_name_changed)
                except:
                    pass

            SceneComponent.set_scene(self, scene)
            if scene is not None:
                self._scene.add_color_listener(self._on_color_changed)
                self._scene.add_name_listener(self._on_name_changed)

        def _on_color_changed(self):
            self._send_state()

        def _on_name_changed(self):
            self._send_state()

        def _on_is_triggered_changed(self):
            self._send_state()

    else:

        def set_scene(self, scene):
            if scene != self._scene or type(self._scene) != type(scene):
                self._on_name_changed.subject = scene
            SceneComponent.set_scene(self, scene)

        from _Framework.SubjectSlot import subject_slot

        @subject_slot('name')
        def _on_name_changed(self):
            self._send_state()

        @subject_slot('is_triggered')
        def _on_is_triggered_changed(self):
            self._send_state()
            SceneComponent._on_is_triggered_changed(self)

        @subject_slot('color')
        def _on_scene_color_changed(self):
            self._send_state()
            SceneComponent._on_scene_color_changed()

    def _send_state(self):
        if hasattr(self, '_get_offset'):
            if self._get_offset is not None:
                offsets = self._get_offset()
                if self._scene_id < offsets[3]:
                    sysex = LC2Sysex('SCENE')
                    sysex.byte(self._scene_id)
                    sysex.ascii(self.get_name())
                    sysex.rgb(self.color())
                    sysex.byte(self.state())
                    sysex.send()

    def get_name(self):
        if self._scene is not None:
            return self._scene.name
        else:
            return ''

    def state(self):
        if self._scene is not None:
            return self._scene.is_triggered
        else:
            return 0

    def color(self):
        if self._scene is not None:
            return self._scene.color
        else:
            return 0

    def fire(self):
        if self._scene is not None:
            self._scene.fire()

    def update(self):
        SceneComponent.update(self)
        if self._allow_updates:
            if self.is_enabled():
                self._send_state()