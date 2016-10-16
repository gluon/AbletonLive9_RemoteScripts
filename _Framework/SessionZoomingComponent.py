#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/SessionZoomingComponent.py
from __future__ import absolute_import
from .CompoundComponent import CompoundComponent
from .ScrollComponent import ScrollComponent
from .SubjectSlot import subject_slot, subject_slot_group
from .Util import in_range

class SessionZoomingComponent(CompoundComponent):
    """
    Class using a matrix of buttons to choose blocks of clips in the
    session, as if you had zoomed out from session.
    """

    def __init__(self, session = None, enable_skinning = False, *a, **k):
        super(SessionZoomingComponent, self).__init__(*a, **k)
        if not session:
            raise AssertionError
            self._buttons = None
            self._scene_bank_buttons = None
            self._scene_bank_button_slots = self.register_slot_manager()
            self._scene_bank_index = 0
            self._empty_value = 0
            self._stopped_value = 100
            self._playing_value = 127
            self._selected_value = 64
            self._session, self._vertical_scroll, self._horizontal_scroll = self.register_components(session, ScrollComponent(), ScrollComponent())
            self._vertical_scroll.can_scroll_up = self._can_scroll_up
            self._vertical_scroll.can_scroll_down = self._can_scroll_down
            self._vertical_scroll.scroll_up = self._scroll_up
            self._vertical_scroll.scroll_down = self._scroll_down
            self._horizontal_scroll.can_scroll_up = self._can_scroll_left
            self._horizontal_scroll.can_scroll_down = self._can_scroll_right
            self._horizontal_scroll.scroll_up = self._scroll_left
            self._horizontal_scroll.scroll_down = self._scroll_right
            self.register_slot(self._session, self._on_session_offset_changes, 'offset')
            enable_skinning and self._enable_skinning()

    def _enable_skinning(self):
        self.set_stopped_value('Zooming.Stopped')
        self.set_selected_value('Zooming.Selected')
        self.set_playing_value('Zooming.Playing')
        self.set_empty_value('Zooming.Empty')

    def on_scene_list_changed(self):
        self.update()

    def on_enabled_changed(self):
        super(SessionZoomingComponent, self).on_enabled_changed()
        self._session.set_show_highlight(self.is_enabled())

    def set_button_matrix(self, buttons):
        if buttons:
            buttons.reset()
        self._buttons = buttons
        self._on_matrix_value.subject = self._buttons
        self.update()
        self._on_session_offset_changes()

    def set_nav_buttons(self, up, down, left, right):
        self.set_nav_up_button(up)
        self.set_nav_down_button(down)
        self.set_nav_left_button(left)
        self.set_nav_right_button(right)
        self.update()

    def set_nav_up_button(self, button):
        self._vertical_scroll.set_scroll_up_button(button)

    def set_nav_down_button(self, button):
        self._vertical_scroll.set_scroll_down_button(button)

    def set_nav_left_button(self, button):
        self._horizontal_scroll.set_scroll_up_button(button)

    def set_nav_right_button(self, button):
        self._horizontal_scroll.set_scroll_down_button(button)

    def set_scene_bank_buttons(self, buttons):
        self._scene_bank_buttons = buttons
        self._on_scene_bank_value.replace_subjects(buttons or [])
        self.update()

    def set_empty_value(self, value):
        self._empty_value = value

    def set_playing_value(self, value):
        self._playing_value = value

    def set_stopped_value(self, value):
        self._stopped_value = value

    def set_selected_value(self, value):
        self._selected_value = value

    def update(self):
        super(SessionZoomingComponent, self).update()
        if self._allow_updates:
            if self.is_enabled():
                self._update_matrix_buttons()
                self._update_scene_bank_buttens()
        else:
            self._update_requests += 1

    def _update_matrix_buttons(self):
        if self._buttons != None:
            tracks = self._session.tracks_to_use()
            scenes = self.song().scenes
            slots_registry = [ None for index in xrange(len(scenes)) ]
            width = self._session.width()
            height = self._session.height()
            for x in xrange(self._buttons.width()):
                for y in xrange(self._buttons.height()):
                    value_to_send = self._empty_value
                    scene_bank_offset = self._scene_bank_index * self._buttons.height() * height
                    track_offset = x * width
                    scene_offset = y * height + scene_bank_offset
                    if track_offset in xrange(len(tracks)) and scene_offset in xrange(len(scenes)):
                        value_to_send = self._stopped_value
                        if self._session.track_offset() in xrange(width * (x - 1) + 1, width * (x + 1)) and self._session.scene_offset() - scene_bank_offset in xrange(height * (y - 1) + 1, height * (y + 1)):
                            value_to_send = self._selected_value
                        else:
                            playing = False
                            for track in xrange(track_offset, track_offset + width):
                                for scene in xrange(scene_offset, scene_offset + height):
                                    if track in xrange(len(tracks)) and scene in xrange(len(scenes)):
                                        if slots_registry[scene] == None:
                                            slots_registry[scene] = scenes[scene].clip_slots
                                        slot = slots_registry[scene][track] if len(slots_registry[scene]) > track else None
                                        if slot != None and slot.has_clip and slot.clip.is_playing:
                                            value_to_send = self._playing_value
                                            playing = True
                                            break

                                if playing:
                                    break

                    if in_range(value_to_send, 0, 128):
                        self._buttons.send_value(x, y, value_to_send)
                    else:
                        self._buttons.set_light(x, y, value_to_send)

    def _update_scene_bank_buttens(self):
        if self._scene_bank_buttons != None:
            for index, button in enumerate(self._scene_bank_buttons):
                if button:
                    button.set_light(index == self._scene_bank_index)

    def _on_session_offset_changes(self):
        if self._buttons:
            self._scene_bank_index = int(self._session.scene_offset() / self._session.height() / self._buttons.height())
        self.update()

    @subject_slot('value')
    def _on_matrix_value(self, value, x, y, is_momentary):
        if self.is_enabled():
            if value != 0 or not is_momentary:
                track_offset = x * self._session.width()
                scene_offset = (y + self._scene_bank_index * self._buttons.height()) * self._session.height()
                if track_offset in xrange(len(self._session.tracks_to_use())) and scene_offset in xrange(len(self.song().scenes)):
                    self._session.set_offsets(track_offset, scene_offset)

    @subject_slot_group('value')
    def _on_scene_bank_value(self, value, sender):
        if self.is_enabled() and self._buttons:
            if value != 0 or not sender.is_momentary():
                button_offset = list(self._scene_bank_buttons).index(sender)
                scene_offset = button_offset * self._buttons.height() * self._session.height()
                if scene_offset in xrange(len(self.song().scenes)):
                    self._scene_bank_index = button_offset
                    self.update()

    def _can_scroll_up(self):
        return self._session._can_bank_up()

    def _can_scroll_down(self):
        return self._session._can_bank_down()

    def _can_scroll_left(self):
        return self._session._can_bank_left()

    def _can_scroll_right(self):
        return self._session._can_bank_right()

    def _scroll_up(self):
        height = self._session.height()
        track_offset = self._session.track_offset()
        scene_offset = self._session.scene_offset()
        if scene_offset > 0:
            new_scene_offset = scene_offset
            if scene_offset % height > 0:
                new_scene_offset -= scene_offset % height
            else:
                new_scene_offset = max(0, scene_offset - height)
            self._session.set_offsets(track_offset, new_scene_offset)

    def _scroll_down(self):
        height = self._session.height()
        track_offset = self._session.track_offset()
        scene_offset = self._session.scene_offset()
        new_scene_offset = scene_offset + height - scene_offset % height
        self._session.set_offsets(track_offset, new_scene_offset)

    def _scroll_left(self):
        width = self._session.width()
        track_offset = self._session.track_offset()
        scene_offset = self._session.scene_offset()
        if track_offset > 0:
            new_track_offset = track_offset
            if track_offset % width > 0:
                new_track_offset -= track_offset % width
            else:
                new_track_offset = max(0, track_offset - width)
            self._session.set_offsets(new_track_offset, scene_offset)

    def _scroll_right(self):
        width = self._session.width()
        track_offset = self._session.track_offset()
        scene_offset = self._session.scene_offset()
        new_track_offset = track_offset + width - track_offset % width
        self._session.set_offsets(new_track_offset, scene_offset)


class DeprecatedSessionZoomingComponent(SessionZoomingComponent):
    """
    Zooming component, that is controlling the sessions enabled state while holding the
    zoom button
    """

    def __init__(self, *a, **k):
        super(DeprecatedSessionZoomingComponent, self).__init__(*a, **k)
        self._zoom_button = None
        self._is_zoomed_out = False

    def set_button_matrix(self, buttons):
        """
        Overwrite to prevent resetting the buttons, as some old components
        don't like it.
        """
        self._buttons = buttons
        self._on_matrix_value.subject = self._buttons
        self.update()
        self._on_session_offset_changes()

    def set_zoom_button(self, button):
        if button != self._zoom_button:
            self._zoom_button = button
            self._on_zoom_value.subject = button
            self._is_zoomed_out = False
            self.update()

    def _session_set_enabled(self, is_enabled):
        self._session.set_enabled(is_enabled)

    @subject_slot('value')
    def _on_zoom_value(self, value):
        if self.is_enabled():
            if self._zoom_button.is_momentary():
                self._is_zoomed_out = value > 0
            else:
                self._is_zoomed_out = not self._is_zoomed_out
            if self._is_zoomed_out and self._buttons:
                self._scene_bank_index = int(self._session.scene_offset() / self._session.height() / self._buttons.height())
            else:
                self._scene_bank_index = 0
            self._session_set_enabled(not self._is_zoomed_out)
            self.update()

    def update(self):
        if self._allow_updates:
            self._session_set_enabled(not self._is_zoomed_out)
        super(DeprecatedSessionZoomingComponent, self).update()

    def _update_matrix_buttons(self):
        if self._is_zoomed_out:
            super(DeprecatedSessionZoomingComponent, self)._update_matrix_buttons()

    def _update_scene_bank_buttens(self):
        if self._is_zoomed_out:
            super(DeprecatedSessionZoomingComponent, self)._update_scene_bank_buttens()

    def _on_session_offset_changes(self):
        if self._is_zoomed_out:
            super(DeprecatedSessionZoomingComponent, self)._on_session_offset_changes()

    @subject_slot('value')
    def _on_matrix_value(self, *a, **k):
        if self._is_zoomed_out:
            super(DeprecatedSessionZoomingComponent, self)._on_matrix_value(*a, **k)

    @subject_slot_group('value')
    def _on_scene_bank_value(self, *a, **k):
        if self._is_zoomed_out:
            super(DeprecatedSessionZoomingComponent, self)._on_scene_bank_value(*a, **k)

    def _scroll_up(self):
        if self._is_zoomed_out:
            super(DeprecatedSessionZoomingComponent, self)._scroll_up()

    def _scroll_down(self):
        if self._is_zoomed_out:
            super(DeprecatedSessionZoomingComponent, self)._scroll_down()

    def _scroll_left(self):
        if self._is_zoomed_out:
            super(DeprecatedSessionZoomingComponent, self)._scroll_left()

    def _scroll_right(self):
        if self._is_zoomed_out:
            super(DeprecatedSessionZoomingComponent, self)._scroll_right()