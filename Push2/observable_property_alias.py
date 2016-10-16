#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Push2/observable_property_alias.py
from __future__ import absolute_import, print_function
from ableton.v2.base import SlotManager, Slot

class ObservablePropertyAlias(SlotManager):

    def __init__(self, alias_host, property_host = None, property_name = '', alias_name = None, getter = None, *a, **k):
        super(ObservablePropertyAlias, self).__init__(*a, **k)
        self._alias_host = alias_host
        self._alias_name = alias_name or property_name
        self._property_host = property_host
        self._property_name = property_name
        self._property_slot = None
        self._setup_alias(getter)

    def _get_property_host(self):
        return self._property_host

    def _set_property_host(self, host):
        self._property_host = host
        self._property_slot.subject = host

    property_host = property(_get_property_host, _set_property_host)

    def _setup_alias(self, getter):
        aliased_prop = property(getter or self._get_property)
        setattr(self._alias_host.__class__, self._alias_name, aliased_prop)
        notifier = getattr(self._alias_host, 'notify_' + self._alias_name)
        self._property_slot = self.register_slot(Slot(self.property_host, notifier, self._property_name))

    def _get_property(self, _):
        return getattr(self.property_host, self._property_name, None)