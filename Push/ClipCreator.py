#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/ClipCreator.py
import Live
_Q = Live.Song.Quantization

class ClipCreator(object):
    """
    Manages clip creation over all components.
    """
    grid_quantization = None
    is_grid_triplet = False
    fixed_length = 8

    def create(self, slot, length = None):
        if not slot.clip == None:
            raise AssertionError
            if length is None:
                length = self.fixed_length
            slot.create_clip(length)
            slot.clip.view.grid_quantization = self.grid_quantization != None and self.grid_quantization
            slot.clip.view.grid_is_triplet = self.is_grid_triplet
        slot.fire(force_legato=True, launch_quantization=_Q.q_no_q)