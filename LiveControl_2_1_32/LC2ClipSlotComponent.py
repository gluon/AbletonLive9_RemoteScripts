#Embedded file name: /Applications/Ableton Live 9 Suite.app/Contents/App-Resources/MIDI Remote Scripts/LiveControl_2_1_31/LC2ClipSlotComponent.py
import Live
from LC2Sysex import LC2Sysex
from _Framework.ClipSlotComponent import ClipSlotComponent
if LC2Sysex.l9():
    from _Framework.SubjectSlot import subject_slot

class LC2ClipSlotComponent(ClipSlotComponent):

    def set_get_offsets(func):
        LC2ClipSlotComponent._get_offset = func

    set_get_offsets = staticmethod(set_get_offsets)

    def release_attributes():
        LC2ClipSlotComponent._get_offset = None

    release_attributes = staticmethod(release_attributes)

    def __init__(self, tid, sid):
        ClipSlotComponent.__init__(self)
        self._tid = tid
        self._sid = sid

    if not LC2Sysex.l9():

        def _set_clip_slot(self, clip_slot):
            if clip_slot != self._clip_slot:
                if self._clip_slot is not None:
                    try:
                        self._clip_slot.remove_has_stop_button_listener(self._send_state)
                        if self.has_clip():
                            self._clip_slot.clip.remove_color_listener(self._on_color_changed)
                            self._clip_slot.clip.remove_name_listener(self._on_name_changed)
                    except:
                        pass

                ClipSlotComponent.set_clip_slot(self, clip_slot)
                if self._clip_slot is not None:
                    self._clip_slot.add_has_stop_button_listener(self._send_state)
                    if self.has_clip():
                        self._clip_slot.clip.add_color_listener(self._on_color_changed)
                        self._clip_slot.clip.add_name_listener(self._on_name_changed)

        def _on_clip_state_changed(self):
            ClipSlotComponent._on_clip_state_changed(self)
            if self.has_clip():
                if not self._clip_slot.clip.color_has_listener(self._on_color_changed):
                    self._clip_slot.clip.add_color_listener(self._on_color_changed)
                if not self._clip_slot.clip.name_has_listener(self._on_name_changed):
                    self._clip_slot.clip.add_name_listener(self._on_name_changed)
            self._send_state()

        def _on_color_changed(self):
            self._send_state()

        def _on_playing_state_changed(self):
            self._send_state()

    if LC2Sysex.l9():

        def _update_clip_property_slots(self):
            clip = self._clip_slot.clip if self._clip_slot else None
            self._on_name_changed.subject = clip
            ClipSlotComponent._update_clip_property_slots(self)

        @subject_slot('name')
        def _on_name_changed(self):
            self._send_state()

    def _send_state(self):
        if self._clip_slot is not None:
            if hasattr(self, '_get_offset'):
                if self._get_offset is not None:
                    offsets = self._get_offset()
                    if self._tid < offsets[2] and self._sid < offsets[3]:
                        sysex = LC2Sysex('CLIP')
                        sysex.byte(self._tid)
                        sysex.byte(self._sid)
                        sysex.trim(self.get_name(), 40)
                        sysex.rgb(self.color())
                        sysex.byte(self.state())
                        sysex.send()

    def get_name(self):
        if self._clip_slot is not None:
            if self._has_clip():
                name = unicode(self._clip_slot.clip.name)
            elif self._clip_slot.controls_other_clips:
                name = '>'
            elif self._clip_slot.has_stop_button:
                name = '[]'
            else:
                name = ''
        else:
            name = ''
        return name

    def state(self):
        playing = 0
        if self._has_clip():
            playing = 1
            if self._clip_slot.clip.is_playing:
                playing = 2
            elif self._clip_slot.clip.is_triggered:
                playing = 3
        elif self._clip_slot is not None:
            if self._clip_slot.is_playing:
                playing = 2
            elif self._clip_slot.is_triggered:
                playing = 3
        return playing

    def color(self):
        if self._clip_slot is not None:
            if self._has_clip():
                rgb = self._clip_slot.clip.color
            elif self._clip_slot.has_stop_button:
                rgb = 3289650
            else:
                rgb = 0
        else:
            rgb = 0
        return rgb

    def _has_clip(self):
        if self._clip_slot is not None:
            return self._clip_slot.has_clip
        else:
            return 0

    def launch(self):
        if self._clip_slot is not None:
            if self._has_clip():
                self._clip_slot.clip.fire()
                if self.song().select_on_launch:
                    self.select()
            else:
                self._clip_slot.fire()

    def select(self):
        if self._clip_slot is not None:
            if self._has_clip():
                self.song().view.selected_track = self._clip_slot.canonical_parent
                self.song().view.selected_scene = self.song().scenes[list(self._clip_slot.canonical_parent.clip_slots).index(self._clip_slot)]

    def update(self):
        if self._allow_updates:
            if self.is_enabled():
                self._send_state()