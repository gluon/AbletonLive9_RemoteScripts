#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/note_editor_paginator.py
from __future__ import absolute_import, print_function
from ableton.v2.base import forward_property, SlotManager, listens, listens_group
from .loop_selector_component import Paginator

class NoteEditorPaginator(Paginator, SlotManager):

    def __init__(self, note_editors = None, *a, **k):
        super(NoteEditorPaginator, self).__init__(*a, **k)
        self._note_editors = note_editors
        self._last_page_index = -1
        self._on_page_length_changed.subject = self._reference_editor
        self._on_active_steps_changed.replace_subjects(note_editors)

    @property
    def _reference_editor(self):
        return self._note_editors[0]

    @forward_property('_reference_editor')
    def page_index():
        pass

    @forward_property('_reference_editor')
    def page_length():
        pass

    def _update_from_page_index(self):
        needed_update = self._last_page_index != self.page_index
        if needed_update:
            self._last_page_index = self.page_index
            self.notify_page_index()
        return needed_update

    @listens_group('active_steps')
    def _on_active_steps_changed(self, editor):
        self.notify_page()

    @listens('page_length')
    def _on_page_length_changed(self):
        self.notify_page()
        self.notify_page_length()
        self._update_from_page_index()

    @property
    def can_change_page(self):
        return all([ e.can_change_page for e in self._note_editors ])

    def select_page_in_point(self, value):
        can_change_page = self.can_change_page
        if can_change_page:
            map(lambda e: e.set_selected_page_point(value), self._note_editors)
            if self._update_from_page_index():
                self.notify_page()
        return can_change_page