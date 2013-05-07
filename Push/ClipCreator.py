#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/ClipCreator.py
import Live
_Q = Live.Song.Quantization

class ClipCreator(object):
    """ Manages clip creation over all components """

    def __init__(self, *a, **k):
        super(ClipCreator, self).__init__(*a, **k)
        self._grid_quantization = None
        self._grid_triplet = False

    def _get_grid_quantization(self):
        return self._grid_quantization

    def _set_grid_quantization(self, quantization):
        self._grid_quantization = quantization

    grid_quantization = property(_get_grid_quantization, _set_grid_quantization)

    def _get_grid_triplet(self):
        return self._grid_triplet

    def _set_grid_triplet(self, triplet):
        self._grid_triplet = triplet

    is_grid_triplet = property(_get_grid_triplet, _set_grid_triplet)

    def create(self, slot, length):
        if not slot.clip == None:
            raise AssertionError
            slot.create_clip(length)
            slot.clip.view.grid_quantization = self.grid_quantization != None and self.grid_quantization
            slot.clip.view.grid_is_triplet = self.is_grid_triplet
        slot.fire(force_legato=True, launch_quantization=_Q.q_no_q)