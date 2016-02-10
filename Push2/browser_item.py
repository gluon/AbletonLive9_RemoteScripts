#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/browser_item.py
from __future__ import absolute_import, print_function
from ableton.v2.base import Proxy

class BrowserItem(object):

    def __init__(self, name = '', icon = '', children = None, is_loadable = False, is_selected = False, contained_item = None, enable_wrapping = True, *a, **k):
        super(BrowserItem, self).__init__(*a, **k)
        self._name = name
        self._icon = icon
        self._children = [] if children is None else children
        self._is_loadable = is_loadable
        self._is_selected = is_selected
        self._contained_item = contained_item
        self._enable_wrapping = enable_wrapping

    @property
    def name(self):
        return self._name

    @property
    def icon(self):
        return self._icon

    @property
    def children(self):
        return self._children

    @property
    def iter_children(self):
        return self.children

    @property
    def is_loadable(self):
        return self._is_loadable

    @property
    def is_selected(self):
        return self._is_selected

    @property
    def contained_item(self):
        return self._contained_item

    @property
    def is_device(self):
        return False

    @property
    def enable_wrapping(self):
        return self._enable_wrapping

    @property
    def uri(self):
        if self._contained_item is not None:
            return self._contained_item.uri
        return self._name


class ProxyBrowserItem(Proxy):

    def __init__(self, enable_wrapping = True, icon = '', *a, **k):
        super(ProxyBrowserItem, self).__init__(*a, **k)
        self._enable_wrapping = enable_wrapping
        self._icon = icon

    @property
    def icon(self):
        return self._icon

    @property
    def enable_wrapping(self):
        return self._enable_wrapping

    @property
    def contained_item(self):
        return self.proxied_object