#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/ClipSlotComponent.py
import Live
from ControlSurfaceComponent import ControlSurfaceComponent
from Util import in_range
from SubjectSlot import subject_slot
INVALID_COLOR = None

class ClipSlotComponent(ControlSurfaceComponent):
    """
    Component representing a ClipSlot within Live.
    """

    def __init__(self, *a, **k):
        super(ClipSlotComponent, self).__init__(*a, **k)
        self._clip_slot = None
        self._triggered_to_play_value = 126
        self._triggered_to_record_value = 121
        self._started_value = 127
        self._recording_value = 120
        self._stopped_value = 0
        self._clip_palette = []
        self._clip_rgb_table = None
        self._record_button_value = None
        self._has_fired_slot = False
        self._on_playing_state_changed_slot = self.register_slot(None, self._on_playing_state_changed, 'playing_status')
        self._on_recording_state_changed_slot = self.register_slot(None, self._on_recording_state_changed, 'is_recording')
        self._on_slot_triggered_changed_slot = self.register_slot(None, self._on_slot_triggered_changed, 'is_triggered')
        self._on_playing_state_changed_slot_slot = self.register_slot(None, self._on_playing_state_changed, 'playing_status')
        self._on_clip_state_changed_slot = self.register_slot(None, self._on_clip_state_changed, 'has_clip')
        self._on_controls_other_changed_slot = self.register_slot(None, self._on_clip_state_changed, 'controls_other_clips')
        self._on_has_stop_button_changed_slot = self.register_slot(None, self._on_has_stop_button_changed, 'has_stop_button')
        self._launch_button_value_slot = self.register_slot(None, self._launch_value, 'value')
        self._on_arm_value_changed_slot = self.register_slot(None, self._on_arm_value_changed, 'arm')
        self._on_implicit_arm_value_changed_slot = self.register_slot(None, self._on_implicit_arm_value_changed, 'implicit_arm')
        self._delete_button = None
        self._select_button = None
        self._duplicate_button = None

    def on_enabled_changed(self):
        self.update()

    def set_clip_slot(self, clip_slot):
        if not (clip_slot == None or isinstance(clip_slot, Live.ClipSlot.ClipSlot)):
            raise AssertionError
            clip = clip_slot.clip if clip_slot else None
            self._on_playing_state_changed_slot.subject = clip
            self._on_recording_state_changed_slot.subject = clip
            self._on_clip_color_changed.subject = clip
            self._on_slot_triggered_changed_slot.subject = clip_slot
            self._on_playing_state_changed_slot_slot.subject = clip_slot
            self._on_clip_state_changed_slot.subject = clip_slot
            self._on_controls_other_changed_slot.subject = clip_slot
            self._on_has_stop_button_changed_slot.subject = clip_slot
            track = clip_slot.canonical_parent if clip_slot else None
            self._on_arm_value_changed_slot.subject = track and track.can_be_armed and track
            self._on_implicit_arm_value_changed_slot.subject = track
        self._clip_slot = clip_slot
        self.update()

    def set_launch_button(self, button):
        if button != self._launch_button_value_slot.subject:
            self._launch_button_value_slot.subject = button
            self.update()

    def set_delete_button(self, button):
        self._delete_button = button

    def set_select_button(self, button):
        self._select_button = button

    def set_duplicate_button(self, button):
        self._duplicate_button = button

    def set_triggered_to_play_value(self, value):
        self._triggered_to_play_value = value

    def set_triggered_to_record_value(self, value):
        self._triggered_to_record_value = value

    def set_started_value(self, value):
        self._started_value = value

    def set_recording_value(self, value):
        self._recording_value = value

    def set_stopped_value(self, value):
        raise in_range(value, -1, 128) or AssertionError
        self._stopped_value = value
        self._clip_palette = []

    def set_record_button_value(self, value):
        self._record_button_value = value

    def set_clip_palette(self, palette):
        raise palette != None or AssertionError
        self._stopped_value = INVALID_COLOR
        self._clip_palette = palette

    def set_clip_rgb_table(self, rgb_table):
        """ A list of velocity, hex-rgb color pairs that is used, if the color could not
        be matched to the clip palette """
        self._clip_rgb_table = rgb_table

    def has_clip(self):
        raise self._clip_slot != None or AssertionError
        return self._clip_slot.has_clip

    def update(self):
        self._has_fired_slot = False
        button = self._launch_button_value_slot.subject
        if self._allow_updates:
            if self.is_enabled() and button != None:
                value_to_send = self._feedback_value()
                if isinstance(value_to_send, int):
                    if in_range(value_to_send, 0, 128):
                        button.send_value(value_to_send)
                    else:
                        button.turn_off()
                else:
                    button.set_light(value_to_send)
        else:
            self._update_requests += 1

    def _feedback_value(self):
        value_to_send = -1
        if self._clip_slot != None:
            slot_or_clip = self._clip_slot
            if self.has_clip():
                slot_or_clip = self._clip_slot.clip
                if self._stopped_value != INVALID_COLOR:
                    value_to_send = self._stopped_value
                else:
                    try:
                        value_to_send = self._clip_palette[self._clip_slot.clip.color]
                    except KeyError:
                        if self._clip_rgb_table != None:
                            value_to_send = self._find_nearest_color(self._clip_rgb_table, self._clip_slot.clip.color)
                        else:
                            value_to_send = 0

            else:
                track = self._clip_slot.canonical_parent
                if track and track.can_be_armed and (track.arm or track.implicit_arm) and self._clip_slot.has_stop_button and self._record_button_value:
                    value_to_send = self._record_button_value
            if slot_or_clip.is_triggered:
                value_to_send = self._triggered_to_record_value if slot_or_clip.will_record_on_start else self._triggered_to_play_value
            elif slot_or_clip.is_playing:
                value_to_send = self._recording_value if slot_or_clip.is_recording else self._started_value
            elif hasattr(slot_or_clip, 'controls_other_clips') and slot_or_clip.controls_other_clips:
                value_to_send = self._stopped_value
        return value_to_send

    def _find_nearest_color(self, rgb_table, src_hex_color):

        def hex_to_channels(color_in_hex):
            return ((color_in_hex & 16711680) >> 16, (color_in_hex & 65280) >> 8, color_in_hex & 255)

        def squared_distance(color):
            return sum([ (a - b) ** 2 for a, b in zip(hex_to_channels(src_hex_color), hex_to_channels(color[1])) ])

        return min(rgb_table, key=squared_distance)[0]

    def _on_clip_state_changed(self):
        if not self._clip_slot != None:
            raise AssertionError
            clip = self.has_clip() and self._clip_slot.clip
            self._on_playing_state_changed_slot.subject = clip
            self._on_recording_state_changed_slot.subject = clip
        self.update()

    @subject_slot('color')
    def _on_clip_color_changed(self):
        self.update()

    def _on_playing_state_changed(self):
        self.update()

    def _on_recording_state_changed(self):
        self.update()

    def _on_arm_value_changed(self):
        self.update()

    def _on_implicit_arm_value_changed(self):
        self.update()

    def _on_has_stop_button_changed(self):
        self.update()

    def _on_slot_triggered_changed(self):
        if not self.has_clip():
            song = self.song()
            view = song.view
            if song.select_on_launch and self._clip_slot.is_triggered and self._has_fired_slot and self._clip_slot.will_record_on_start and self._clip_slot != view.highlighted_clip_slot:
                view.highlighted_clip_slot = self._clip_slot
            self.update()

    def _launch_value(self, value):
        if self.is_enabled():
            if self._select_button and self._select_button.is_pressed() and value:
                self._do_select_clip(self._clip_slot)
            elif self._clip_slot != None:
                if self._duplicate_button and self._duplicate_button.is_pressed():
                    if value:
                        self._do_duplicate_clip()
                elif self._delete_button and self._delete_button.is_pressed():
                    if value:
                        self._do_delete_clip()
                else:
                    self._do_launch_clip(value)

    def _do_delete_clip(self):
        if self._clip_slot and self._clip_slot.has_clip:
            self._clip_slot.delete_clip()

    def _do_select_clip(self, clip_slot):
        if self._clip_slot != None:
            if self.song().view.highlighted_clip_slot != self._clip_slot:
                self.song().view.highlighted_clip_slot = self._clip_slot

    def _do_duplicate_clip(self):
        if self._clip_slot and self._clip_slot.has_clip:
            try:
                track = self._clip_slot.canonical_parent
                track.duplicate_clip_slot(list(track.clip_slots).index(self._clip_slot))
            except Live.Base.LimitationError:
                pass
            except RuntimeError:
                pass

    def _do_launch_clip(self, value):
        button = self._launch_button_value_slot.subject
        object_to_launch = self._clip_slot
        if not value != 0:
            launch_pressed = not button.is_momentary()
            if self.has_clip():
                object_to_launch = self._clip_slot.clip
            else:
                self._has_fired_slot = True
            if button.is_momentary():
                object_to_launch.set_fire_button_state(value != 0)
            elif value != 0:
                object_to_launch.fire()
            self.song().view.highlighted_clip_slot = launch_pressed and self.has_clip() and self.song().select_on_launch and self._clip_slot