#Embedded file name: /Users/versonator/Jenkins/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/Layer.py
"""
Module implementing a way to resource-based access to controls in an
unified interface dynamic.
"""
from Util import nop
from itertools import repeat, izip
from Resource import ExclusiveResource, CompoundResource

class LayerError(Exception):
    pass


class UnhandledControlError(LayerError):
    pass


class ControlClient(object):
    """
    Client of the indivial controls that delivers the controls to the
    layer owner.
    """

    def __init__(self, layer = None, layer_client = None, *a, **k):
        super(ControlClient, self).__init__(*a, **k)
        raise layer_client or AssertionError
        raise layer or AssertionError
        self.layer_client = layer_client
        self.layer = layer

    def __eq__(self, other):
        return self.layer == getattr(other, 'layer', None) and self.layer_client == getattr(other, 'layer_client', None)

    def set_control_element(self, control_element, grabbed):
        layer = self.layer
        owner = self.layer_client
        raise owner or AssertionError
        if not control_element in layer._control_to_names:
            raise AssertionError, 'Control not in layer: %s' % (control_element,)
            names = layer._control_to_names[control_element]
            control_element = grabbed or None
        for name in names:
            try:
                handler = getattr(owner, 'set_' + name)
            except AttributeError:
                try:
                    control = getattr(owner, name)
                    handler = control.set_control_element
                except AttributeError:
                    if name[0] != '_':
                        raise UnhandledControlError, 'Component %s has no handler for control_element %s' % (str(owner), name)
                    else:
                        handler = nop

            handler(control_element or None)
            layer._name_to_controls[name] = control_element


class CompoundLayer(CompoundResource):
    """
    A compound resource takes two layers and makes them look like one,
    grabbing both of them.  Both can have different priorities
    thought.
    """

    def _get_priority(self):
        raise self.first.priority == self.second.priority or AssertionError
        return self.first.priority

    def _set_priority(self, priority):
        self.first.priority = priority
        self.second.priority = priority

    priority = property(_get_priority, _set_priority)

    def __getattr__(self, key):
        try:
            return getattr(self.first, key)
        except AttributeError:
            return getattr(self.second, key)


class Layer(ExclusiveResource):
    """
    A layer provides a convenient interface to control resources. In a
    layer, you can group several controls by name.  The layer itself
    is an exclusive resource.  When grabbing the layer, it will try to
    grab all controls and will forward them to its own owner when he
    receives them, and will take them from him when they are
    release. The layer with give and take away the controls from its
    client using methods of the form::
    
        client.set[control-name](control)
    
    Where [control-name] is the name the control was given in this
    layer.  This way, layers are a convenient way to provide controls
    to components indirectly, with automatic handling of competition
    for them.
    
    Note that [control-name] can not be any of the following reserved
    names: priority, grab, release, on_grab, on_release, owner,
    get_owner
    
    If [control-name] starts with an underscore (_) it is considered
    private.  It is grabbed but it is not delivered to the client.
    """

    def __init__(self, priority = None, **controls):
        super(Layer, self).__init__()
        self._priority = priority
        self._name_to_controls = dict(izip(controls.iterkeys(), repeat(None)))
        self._control_to_names = dict()
        for name, control in controls.iteritems():
            self._control_to_names.setdefault(control, []).append(name)

    def __add__(self, other):
        return CompoundLayer(self, other)

    def _get_priority(self):
        return self._priority

    def _set_priority(self, priority):
        if priority != self._priority:
            self._priority = priority
            if self.owner:
                self.grab(self.owner)

    priority = property(_get_priority, _set_priority)

    def __getattr__(self, name):
        """ Provides access to controls """
        try:
            return self._name_to_controls[name]
        except KeyError:
            raise AttributeError

    def grab(self, client, *a, **k):
        if client == self.owner:
            self.on_grab(client, *a, **k)
            return True
        return super(Layer, self).grab(client, *a, **k)

    def on_grab(self, client, *a, **k):
        """ Override from ExclusiveResource """
        for control in self._control_to_names.iterkeys():
            k.setdefault('priority', self._priority)
            control.resource.grab(ControlClient(layer_client=client, layer=self), *a, **k)

    def on_release(self, client):
        """ Override from ExclusiveResource """
        for control in self._control_to_names.iterkeys():
            control.resource.release(ControlClient(layer_client=client, layer=self))