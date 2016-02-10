#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/simpler_zoom.py
from __future__ import absolute_import, print_function
from contextlib import contextmanager
from ableton.v2.base import clamp, linear, SlotManager, Subject, listens, liveobj_valid, liveobj_changed
from pushbase.device_chain_utils import is_simpler

def get_zoom_parameter(parameter_host):
    parameters = parameter_host.parameters if liveobj_valid(parameter_host) else []
    results = filter(lambda p: p.name == 'Zoom', parameters)
    if len(results) > 0:
        return results[0]


class ZoomHandling(SlotManager, Subject):
    __events__ = ('zoom',)
    SCREEN_WIDTH = 960
    ZOOM_EXP = 10.0
    DEFAULT_ZOOM_START_FUDGE = 0.2
    _parameter_host = None
    _zoom_parameter = None

    @property
    def zoom(self):
        if self._zoom_parameter:
            return self._zoom_parameter.value
        return 0.0

    @property
    def max_zoom(self):
        return NotImplementedError

    @property
    def zoom_factor(self):
        factor = 1.0
        if self.zoom > 0.0:
            minimum = 1.0
            factor = 1.0 / linear(minimum, self.max_zoom, self.zoom)
        return factor

    @listens('value')
    def _on_zoom_changed(self):
        self.notify_zoom()

    def _get_zoom_start_fudge(self):
        """ Return fudge for lowest zoom value, assuming ZOOM_EXP == 10.0.
        
        _internal_to_zoom and _zoom_to_internal adjust for some mysterious
        behaviour elsewhere with a fudge to map the lowest non-zero internal
        value to a higher zoom value, determined by the return value of this
        funtion.
        
        The sensible return value of this depends on the exponent of the curve
        used in those functions. To account for the fact that ZOOM_EXP is
        can be changed in subclasses or in the future, this function should return
        a value which assumes a ZOOM_EXP of 10.0.
        """
        return self.DEFAULT_ZOOM_START_FUDGE

    def _internal_to_zoom(self, value, _parent):
        fudge = self._get_zoom_start_fudge() ** 10 ** (1.0 / self.ZOOM_EXP)
        if value > 0.0:
            return (value * (1.0 - fudge) + fudge) ** self.ZOOM_EXP
        return 0.0

    def _zoom_to_internal(self, value, _parent):
        fudge = self._get_zoom_start_fudge() ** 10 ** (1.0 / self.ZOOM_EXP)
        linear_value = (value ** (1.0 / self.ZOOM_EXP) - fudge) / (1.0 - fudge)
        return clamp(linear_value, 0.0, 1.0)

    def request_zoom(self, factor):
        if self._zoom_parameter:
            self._zoom_parameter.value = factor

    def _set_zoom_parameter(self):
        return NotImplementedError

    def set_parameter_host(self):
        return NotImplementedError


class SimplerZoomHandling(ZoomHandling):

    def __init__(self):
        ZoomHandling.__init__(self)
        self.ZOOM_EXP = 20.0

    def set_parameter_host(self, parameter_host):
        new_parameter_host = parameter_host if is_simpler(parameter_host) else None
        if liveobj_changed(self._parameter_host, new_parameter_host):
            old_zoom = self.zoom
            self._parameter_host = new_parameter_host
            with self._updating_zoom_scaling():
                self._set_zoom_parameter()
            self._on_zoom_changed.subject = self._zoom_parameter
            self._on_sample_changed.subject = self._parameter_host
            if self.zoom != old_zoom:
                self.notify_zoom()

    def _set_zoom_parameter(self):
        self._zoom_parameter = get_zoom_parameter(self._parameter_host)

    @listens('sample')
    def _on_sample_changed(self):
        if self._zoom_parameter:
            self._zoom_parameter.value = self._zoom_parameter.default_value

    @contextmanager
    def _updating_zoom_scaling(self):
        if self._zoom_parameter:
            self._zoom_parameter.set_scaling_functions(None, None)
        yield
        if self._zoom_parameter:
            self._zoom_parameter.set_scaling_functions(self._zoom_to_internal, self._internal_to_zoom)

    @property
    def max_zoom(self):
        has_sample = liveobj_valid(self._parameter_host) and liveobj_valid(self._parameter_host.sample)
        length = float(self._parameter_host.sample.length if has_sample else self.SCREEN_WIDTH)
        return float(length / self.SCREEN_WIDTH)

    def _get_zoom_start_fudge(self):
        if liveobj_valid(self._parameter_host) and liveobj_valid(self._parameter_host.sample):
            sample_length = self._parameter_host.sample.length
            fudge_length_a = 200000
            fudge_factor_a = 0.4
            fudge_length_b = 2500000
            fudge_factor_b = 0.2
            if sample_length < fudge_length_a:
                return fudge_factor_a
            if sample_length > fudge_length_b:
                return fudge_factor_b
            return (sample_length - fudge_length_a) / (fudge_length_b - fudge_length_a) * (fudge_factor_b - fudge_factor_a) + fudge_factor_a
        else:
            return self.DEFAULT_ZOOM_START_FUDGE