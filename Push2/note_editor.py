# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/note_editor.py
# Compiled at: 2016-11-16 18:13:20
from __future__ import absolute_import, print_function
from pushbase.note_editor_component import NoteEditorComponent

class Push2NoteEditorComponent(NoteEditorComponent):
    __events__ = ('mute_solo_stop_cancel_action_performed', )

    def _on_pad_pressed(self, coordinate):
        super(Push2NoteEditorComponent, self)._on_pad_pressed(coordinate)
        self.notify_mute_solo_stop_cancel_action_performed()