#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/pad_velocity_curve.py
from __future__ import absolute_import, print_function
import math
from ableton.v2.base import SerializableListenableProperties, chunks, clamp, listenable_property, task
from ableton.v2.control_surface import Component
NUM_VELOCITY_CURVE_ENTRIES = 128
LAST_INDEX_FOR_DISPLAY = 58

class LookupTable:
    MAXW = [1700.0,
     1660.0,
     1590.0,
     1510.0,
     1420.0,
     1300.0,
     1170.0,
     1030.0,
     860.0,
     640.0,
     400.0]
    CPMIN = [1650.0,
     1580.0,
     1500.0,
     1410.0,
     1320.0,
     1220.0,
     1110.0,
     1000.0,
     900.0,
     800.0,
     700.0]
    CPMAX = [2050.0,
     1950.0,
     1850.0,
     1750.0,
     1650.0,
     1570.0,
     1490.0,
     1400.0,
     1320.0,
     1240.0,
     1180.0]
    GAMMA = [0.7,
     0.64,
     0.58,
     0.54,
     0.5,
     0.46,
     0.43,
     0.4,
     0.36,
     0.32,
     0.25]
    MINV = [1.0,
     1,
     1.0,
     1.0,
     1.0,
     1.0,
     3.0,
     6.0,
     12.0,
     24.0,
     36.0]
    MAXV = [96.0,
     102.0,
     116.0,
     121.0,
     124.0,
     127.0,
     127.0,
     127.0,
     127.0,
     127.0,
     127.0]
    ALPHA = [90.0,
     70.0,
     54.0,
     40.0,
     28.0,
     20.0,
     10.0,
     -5.0,
     -25.0,
     -55.0,
     -90.0]


def gamma_func(x, gamma):
    return math.pow(x, math.exp(-4.0 + 8.0 * gamma))


def calculate_points(alpha):
    a1 = (225.0 - alpha) * math.pi / 180.0
    a2 = (45.0 - alpha) * math.pi / 180.0
    r = 0.4
    p1x = 0.5 + r * math.cos(a1)
    p1y = 0.5 + r * math.sin(a1)
    p2x = 0.5 + r * math.cos(a2)
    p2y = 0.5 + r * math.sin(a2)
    return (p1x,
     p1y,
     p2x,
     p2y)


def bezier(x, t, p1x, p1y, p2x, p2y):
    p0x = 0.0
    p0y = 0.0
    p3x = 1.0
    p3y = 1.0
    while t <= 1.0:
        s = 1 - t
        t2 = t * t
        t3 = t2 * t
        s2 = s * s
        s3 = s2 * s
        xt = s3 * p0x + 3 * t * s2 * p1x + 3 * t2 * s * p2x + t3 * p3x
        if xt >= x:
            return (s3 * p0y + 3 * t * s2 * p1y + 3 * t2 * s * p2y + t3 * p3y, t)
        t += 0.0001

    return (1.0, t)


def generate_velocity_curve(sensitivity, gain, dynamics):
    minw = 160
    maxw = LookupTable.MAXW[sensitivity]
    gamma = LookupTable.GAMMA[gain]
    minv = LookupTable.MINV[gain]
    maxv = LookupTable.MAXV[gain]
    alpha = LookupTable.ALPHA[dynamics]
    p1x, p1y, p2x, p2y = calculate_points(alpha)
    curve = []
    minw_index = int(minw) / 32
    maxw_index = int(maxw) / 32
    t = 0.0
    for index in xrange(NUM_VELOCITY_CURVE_ENTRIES):
        w = index * 32.0
        if w <= minw:
            velocity = 1.0 + (minv - 1.0) * float(index) / float(minw_index)
        elif w >= maxw:
            velocity = maxv + (127.0 - maxv) * float(index - maxw_index) / float(128 - maxw_index)
        else:
            wnorm = (w - minw) / (maxw - minw)
            b, t = bezier(wnorm, t, p1x, p1y, p2x, p2y)
            velonorm = gamma_func(b, gamma)
            velocity = minv + velonorm * (maxv - minv)
        curve.append(clamp(int(round(velocity)), 1, 127))

    return curve


def generate_thresholds(sensitivity, gain, dynamics):
    cpmin = LookupTable.CPMIN[sensitivity]
    cpmax = LookupTable.CPMAX[sensitivity]
    threshold0 = 33
    threshold1 = 31
    return (threshold0,
     threshold1,
     int(cpmin),
     int(cpmax))


class PadVelocityCurveSettings(SerializableListenableProperties):
    sensitivity = listenable_property.managed(5)
    min_sensitivity = 0
    max_sensitivity = 10
    gain = listenable_property.managed(5)
    min_gain = 0
    max_gain = 10
    dynamics = listenable_property.managed(5)
    min_dynamics = 0
    max_dynamics = 10


class PadVelocityCurveSender(Component):
    SEND_RATE = 0.5
    curve_points = listenable_property.managed([])

    def __init__(self, curve_sysex_element = None, threshold_sysex_element = None, settings = None, chunk_size = None, *a, **k):
        raise curve_sysex_element is not None or AssertionError
        raise threshold_sysex_element is not None or AssertionError
        raise settings is not None or AssertionError
        raise chunk_size is not None or AssertionError
        super(PadVelocityCurveSender, self).__init__(*a, **k)
        self._curve_sysex_element = curve_sysex_element
        self._threshold_sysex_element = threshold_sysex_element
        self._settings = settings
        self._chunk_size = chunk_size
        self._send_task = self._tasks.add(task.sequence(task.wait(self.SEND_RATE), task.run(self._on_send_task_finished))).kill()
        self._settings_changed = False
        self.register_slot(settings, self._on_setting_changed, 'sensitivity')
        self.register_slot(settings, self._on_setting_changed, 'gain')
        self.register_slot(settings, self._on_setting_changed, 'dynamics')
        self._update_curve_model()

    def send(self):
        self._send_velocity_curve()
        self._send_thresholds()
        self._settings_changed = False

    def _send_velocity_curve(self):
        velocities = self._generate_curve()
        velocity_chunks = chunks(velocities, self._chunk_size)
        for index, velocities in enumerate(velocity_chunks):
            self._curve_sysex_element.send_value(index * self._chunk_size, velocities)

    def _send_thresholds(self):
        threshold_values = generate_thresholds(self._settings.sensitivity, self._settings.gain, self._settings.dynamics)
        self._threshold_sysex_element.send_value(*threshold_values)

    def _generate_curve(self):
        return generate_velocity_curve(self._settings.sensitivity, self._settings.gain, self._settings.dynamics)

    def _on_setting_changed(self, _):
        if not self._send_task.is_running:
            self.send()
            self._send_task.restart()
        else:
            self._settings_changed = True
        self._update_curve_model()

    def _update_curve_model(self):
        self.curve_points = self._generate_curve()[:LAST_INDEX_FOR_DISPLAY]

    def _on_send_task_finished(self):
        if self._settings_changed:
            self.send()