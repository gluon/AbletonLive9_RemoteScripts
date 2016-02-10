#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/components/session_navigation.py
from __future__ import absolute_import, print_function
from ...base import listens
from ..compound_component import CompoundComponent
from .scroll import ScrollComponent

class SessionNavigationComponent(CompoundComponent):
    """
    Allows moving the session ring using navigation controls.
    """

    def __init__(self, session_ring = None, *a, **k):
        super(SessionNavigationComponent, self).__init__(*a, **k)
        raise session_ring is not None or AssertionError
        self._session_ring = session_ring
        self.__on_offset_changed.subject = self._session_ring
        self.__on_tracks_changed.subject = self._session_ring
        self.__on_scene_list_changed.subject = self.song
        self._vertical_banking, self._horizontal_banking, self._vertical_paginator, self._horizontal_paginator = self.register_components(ScrollComponent(), ScrollComponent(), ScrollComponent(), ScrollComponent())
        self._vertical_banking.can_scroll_up = self._can_bank_up
        self._vertical_banking.can_scroll_down = self._can_bank_down
        self._vertical_banking.scroll_up = self._bank_up
        self._vertical_banking.scroll_down = self._bank_down
        self._horizontal_banking.can_scroll_up = self._can_bank_left
        self._horizontal_banking.can_scroll_down = self._can_bank_right
        self._horizontal_banking.scroll_up = self._bank_left
        self._horizontal_banking.scroll_down = self._bank_right
        self._vertical_paginator.can_scroll_up = self._can_scroll_page_up
        self._vertical_paginator.can_scroll_down = self._can_scroll_page_down
        self._vertical_paginator.scroll_up = self._scroll_page_up
        self._vertical_paginator.scroll_down = self._scroll_page_down
        self._horizontal_paginator.can_scroll_up = self._can_scroll_page_left
        self._horizontal_paginator.can_scroll_down = self._can_scroll_page_right
        self._horizontal_paginator.scroll_up = self._scroll_page_left
        self._horizontal_paginator.scroll_down = self._scroll_page_right

    @listens('offset')
    def __on_offset_changed(self, track_offset, _):
        self._update_vertical()
        self._update_horizontal()

    @listens('tracks')
    def __on_tracks_changed(self):
        self._update_horizontal()

    @listens('scenes')
    def __on_scene_list_changed(self):
        self._update_vertical()

    def _update_vertical(self):
        if self.is_enabled():
            self._vertical_banking.update()
            self._vertical_paginator.update()

    def _update_horizontal(self):
        if self.is_enabled():
            self._horizontal_banking.update()
            self._horizontal_paginator.update()

    def _can_scroll_page_up(self):
        return self._session_ring.scene_offset > 0

    def _can_scroll_page_down(self):
        return self._session_ring.scene_offset < len(self.song.scenes) - self._session_ring.num_scenes

    def _scroll_page_up(self):
        height = self._session_ring.num_scenes
        track_offset = self._session_ring.track_offset
        scene_offset = self._session_ring.scene_offset
        if scene_offset > 0:
            new_scene_offset = scene_offset
            if scene_offset % height > 0:
                new_scene_offset -= scene_offset % height
            else:
                new_scene_offset = max(0, scene_offset - height)
            self._session_ring.set_offsets(track_offset, new_scene_offset)

    def _scroll_page_down(self):
        height = self._session_ring.num_scenes
        track_offset = self._session_ring.track_offset
        scene_offset = self._session_ring.scene_offset
        new_scene_offset = scene_offset + height - scene_offset % height
        self._session_ring.set_offsets(track_offset, new_scene_offset)

    def _can_scroll_page_left(self):
        return self._session_ring.track_offset > 0

    def _can_scroll_page_right(self):
        return self._session_ring.track_offset < len(self._session_ring.tracks_to_use()) - self._session_ring.num_tracks

    def _scroll_page_left(self):
        width = self._session_ring.num_tracks
        track_offset = self._session_ring.track_offset
        scene_offset = self._session_ring.scene_offset
        if track_offset > 0:
            new_track_offset = track_offset
            if track_offset % width > 0:
                new_track_offset -= track_offset % width
            else:
                new_track_offset = max(0, track_offset - width)
            self._session_ring.set_offsets(new_track_offset, scene_offset)

    def _scroll_page_right(self):
        width = self._session_ring.num_tracks
        track_offset = self._session_ring.track_offset
        scene_offset = self._session_ring.scene_offset
        new_track_offset = track_offset + width - track_offset % width
        self._session_ring.set_offsets(new_track_offset, scene_offset)

    def _can_bank_down(self):
        return len(self.song.scenes) > self._session_ring.scene_offset + 1

    def _can_bank_up(self):
        return self._session_ring.scene_offset > 0

    def _can_bank_right(self):
        return len(self._session_ring.tracks_to_use()) > self._session_ring.track_offset + 1

    def _can_bank_left(self):
        return self._session_ring.track_offset > 0

    def _bank_up(self):
        return self._session_ring.move(0, -1)

    def _bank_down(self):
        return self._session_ring.move(0, 1)

    def _bank_right(self):
        return self._session_ring.move(1, 0)

    def _bank_left(self):
        return self._session_ring.move(-1, 0)

    def set_up_button(self, button):
        self._vertical_banking.set_scroll_up_button(button)

    def set_down_button(self, button):
        self._vertical_banking.set_scroll_down_button(button)

    def set_left_button(self, button):
        self._horizontal_banking.set_scroll_up_button(button)
        self._horizontal_banking.update()

    def set_right_button(self, button):
        self._horizontal_banking.set_scroll_down_button(button)

    def set_page_up_button(self, page_up_button):
        self._vertical_paginator.set_scroll_up_button(page_up_button)

    def set_page_down_button(self, page_down_button):
        self._vertical_paginator.set_scroll_down_button(page_down_button)

    def set_page_left_button(self, page_left_button):
        self._horizontal_paginator.set_scroll_up_button(page_left_button)

    def set_page_right_button(self, page_right_button):
        self._horizontal_paginator.set_scroll_down_button(page_right_button)