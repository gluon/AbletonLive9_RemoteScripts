#Embedded file name: C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\Maschine_Mk1\ModSceneComponent.py
import Live
from _Framework.SceneComponent import SceneComponent
from _Framework.Util import in_range, nop
from ModClipSlotComponent import ModClipSlotComponent

class ModSceneComponent(SceneComponent):
    """
    Special Scene Component for Maschine
    """
    clip_slot_component_type = ModClipSlotComponent

    def __init__(self, num_slots = 0, tracks_to_use_callback = nop, *a, **k):
        super(ModSceneComponent, self).__init__(num_slots, tracks_to_use_callback, *a, **k)