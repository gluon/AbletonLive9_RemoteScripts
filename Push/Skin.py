#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/Push/Skin.py
import SkinDefault

class SkinColorMissingError(Exception):
    pass


class Skin(object):

    def __init__(self, colors = None, *a, **k):
        super(Skin, self).__init__(*a, **k)
        self._colors = {}
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


def make_default_skin():
    skin = Skin(SkinDefault.Colors)
    return skin