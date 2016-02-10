#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/Skin.py
from __future__ import absolute_import
from itertools import chain

class SkinColorMissingError(Exception):
    pass


class Skin(object):

    def __init__(self, colors = None, *a, **k):
        super(Skin, self).__init__(*a, **k)
        self._colors = {}
        if colors is not None:
            self._fill_colors(colors)

    def _fill_colors(self, colors, pathname = ''):
        try:
            self._fill_colors(super(colors))
        except TypeError:
            map(self._fill_colors, colors.__bases__)

        for k, v in colors.__dict__.iteritems():
            if k[:1] != '_':
                if callable(v):
                    self._fill_colors(v, pathname + k + '.')
                else:
                    self._colors[pathname + k] = v

    def __getitem__(self, key):
        try:
            return self._colors[key]
        except KeyError:
            raise SkinColorMissingError, 'Skin color missing: %s' % str(key)

    def iteritems(self):
        return self._colors.iteritems()


def merge_skins(*skins):
    skin = Skin()
    skin._colors = dict(chain(*map(lambda s: s._colors.items(), skins)))
    return skin