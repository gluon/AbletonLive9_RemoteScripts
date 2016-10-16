#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/components/clip_slot.py
from __future__ import absolute_import, print_function
import Live
from ...base import in_range, listens, liveobj_valid
from ..component import Component

def find_nearest_color(rgb_table, src_hex_color):

    def hex_to_channels(color_in_hex):
        return ((color_in_hex & 16711680) >> 16, (color_in_hex & 65280) >> 8, color_in_hex & 255)

    def squared_distance(color):
        return sum([ (a - b) ** 2 for a, b in zip(hex_to_channels(src_hex_color), hex_to_channels(color[1])) ])

    return min(rgb_table, key=squared_distance)[0]


class ClipSlotComponent(Component):
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
        self._delete_button = None
        self._select_button = None
        self._duplicate_button = None

    def on_enabled_changed(self):
        self.update()

    def set_clip_slot(self, clip_slot):
        self._clip_slot = clip_slot
        self._update_clip_property_slots()
        self.__on_slot_triggered_changed.subject = clip_slot
        self.__on_slot_playing_state_changed.subject = clip_slot
        self.__on_clip_state_changed.subject = clip_slot
        self.__on_controls_other_clips_changed.subject = clip_slot
        self.__on_has_stop_button_changed.subject = clip_slot
        self.__on_clip_slot_color_changed.subject = clip_slot
        track = clip_slot.canonical_parent if clip_slot else None
        if track and track.can_be_armed:
            self.__on_arm_value_changed.subject = track
            self.__on_implicit_arm_value_changed.subject = track
        self.update()

    def set_launch_button(self, button):
        self.__launch_button_value.subject = button
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
        self._stopped_value = value
        self._clip_palette = []

    def set_record_button_value(self, value):
        self._record_button_value = value

    def set_clip_palette(self, palette):
        raise palette != None or AssertionError
        self._stopped_value = None
        self._clip_palette = palette

    def set_clip_rgb_table(self, rgb_table):
        """ A list of velocity, hex-rgb color pairs that is used, if the color could not
        be matched to the clip palette """
        self._clip_rgb_table = rgb_table

    def has_clip(self):
        raise liveobj_valid(self._clip_slot) or AssertionError
        return self._clip_slot.has_clip

    def update(self):
        super(ClipSlotComponent, self).update()
        self._has_fired_slot = False
        button = self.__launch_button_value.subject
        if self._allow_updates:
            if self.is_enabled() and button != None:
                value_to_send = self._feedback_value()
                if value_to_send in (None, -1):
                    button.turn_off()
                elif in_range(value_to_send, 0, 128):
                    button.send_value(value_to_send)
                else:
                    button.set_light(value_to_send)
        else:
            self._update_requests += 1

    def _color_value(self, slot_or_clip):
        color = slot_or_clip.color
        try:
            return self._clip_palette[color]
        except (KeyError, IndexError):
            if self._clip_rgb_table != None:
                return find_nearest_color(self._clip_rgb_table, color)
            else:
                return self._stopped_value

    def _track_is_armed(self, track):
        return liveobj_valid(track) and track.can_be_armed and any([track.arm, track.implicit_arm])

    def _feedback_value(self):
        if liveobj_valid(self._clip_slot):
            track = self._clip_slot.canonical_parent
            slot_or_clip = self._clip_slot.clip if self.has_clip() else self._clip_slot
            if slot_or_clip.is_triggered:
                if slot_or_clip.will_record_on_start:
                    return self._triggered_to_record_value
                return self._triggered_to_play_value
            if slot_or_clip.is_playing:
                if slot_or_clip.is_recording:
                    return self._recording_value
                return self._started_value
            if slot_or_clip.color != None:
                return self._color_value(slot_or_clip)
            if getattr(slot_or_clip, 'controls_other_clips', True) and self._stopped_value != None:
                return self._stopped_value
            if self._track_is_armed(track) and self._clip_slot.has_stop_button and self._record_button_value != None:
                return self._record_button_value

    def _update_clip_property_slots(self):
        clip = self._clip_slot.clip if self._clip_slot else None
        self.__on_clip_playing_state_changed.subject = clip
        self.__on_recording_state_changed.subject = clip
        self.__on_clip_color_changed.subject = clip

    @listens('has_clip')
    def __on_clip_state_changed(self):
        self._update_clip_property_slots()
        self.update()

    @listens('controls_other_clips')
    def __on_controls_other_clips_changed(self):
        self._update_clip_property_slots()
        self.update()

    @listens('color')
    def __on_clip_color_changed(self):
        self.update()

    @listens('color')
    def __on_clip_slot_color_changed(self):
        self.update()

    @listens('playing_status')
    def __on_slot_playing_state_changed(self):
        self.update()

    @listens('playing_status')
    def __on_clip_playing_state_changed(self):
        self.update()

    @listens('is_recording')
    def __on_recording_state_changed(self):
        self.update()

    @listens('arm')
    def __on_arm_value_changed(self):
        self.update()

    @listens('implicit_arm')
    def __on_implicit_arm_value_changed(self):
        self.update()

    @listens('has_stop_button')
    def __on_has_stop_button_changed(self):
        self.update()

    @listens('is_triggered')
    def __on_slot_triggered_changed(self):
        if not self.has_clip():
            song = self.song
            view = song.view
            if song.select_on_launch and self._clip_slot.is_triggered and self._has_fired_slot and self._clip_slot.will_record_on_start and self._clip_slot != view.highlighted_clip_slot:
                view.highlighted_clip_slot = self._clip_slot
            self.update()

    @listens('value')
    def __launch_button_value(self, value):
        if self.is_enabled():
            if self._select_button and self._select_button.is_pressed() and value:
                self._do_select_clip(self._clip_slot)
            elif liveobj_valid(self._clip_slot):
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
        if liveobj_valid(self._clip_slot):
            if self.song.view.highlighted_clip_slot != self._clip_slot:
                self.song.view.highlighted_clip_slot = self._clip_slot

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
        button = self.__launch_button_value.subject
        object_to_launch = self._clip_slot
        launch_pressed = value or not button.is_momentary()
        if self.has_clip():
            object_to_launch = self._clip_slot.clip
        else:
            self._has_fired_slot = True
        if button.is_momentary():
            object_to_launch.set_fire_button_state(value != 0)
        elif launch_pressed:
            object_to_launch.fire()
        if launch_pressed and self.has_clip() and self.song.select_on_launch:
            self.song.view.highlighted_clip_slot = self._clip_slot