#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/ableton/v2/control_surface/layer.py
"""
Module implementing a way to resource-based access to controls in an
unified interface dynamic.
"""
from __future__ import absolute_import, print_function
from itertools import repeat, izip
from .control_element import ControlElementClient, get_element
from .resource import ExclusiveResource, CompoundResource
from ..base import Disconnectable, nop

class LayerError(Exception):
    pass


class UnhandledElementError(LayerError):
    pass


class SimpleLayerOwner(Disconnectable):
    """
    Simple owner that grabs a given layer until it's disconnected
    """

    def __init__(self, layer = None):
        self._layer = layer
        self._layer.grab(self)

    def disconnect(self):
        self._layer.release(self)


class LayerClient(ControlElementClient):
    """
    Client of the indivial elements that delivers the elements to the
    layer owner.
    """

    def __init__(self, layer = None, layer_client = None, *a, **k):
        super(LayerClient, self).__init__(*a, **k)
        raise layer_client or AssertionError
        raise layer or AssertionError
        self.layer_client = layer_client
        self.layer = layer

    def set_control_element(self, control_element, grabbed):
        layer = self.layer
        owner = self.layer_client
        if not owner:
            raise AssertionError
            raise control_element in layer._element_to_names or AssertionError('Control not in layer: %s' % (control_element,))
            names = layer._element_to_names[control_element]
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
                        raise UnhandledElementError('Component %s has no handler for control_element %s' % (str(owner), name))
                    else:
                        handler = nop

            handler(control_element or None)
            layer._name_to_elements[name] = control_element


class CompoundLayer(CompoundResource):
    """
    A compound resource takes two layers and makes them look like one,
    grabbing both of them.  Both can have different priorities
    thought.
    """

    @property
    def priority(self):
        raise self.first.priority == self.second.priority or AssertionError
        return self.first.priority

    @priority.setter
    def priority(self, priority):
        self.first.priority = priority
        self.second.priority = priority

    def __getattr__(self, key):
        try:
            return getattr(self.first, key)
        except AttributeError:
            return getattr(self.second, key)


class LayerBase(ExclusiveResource):

    def __init__(self, priority = None, *a, **k):
        super(LayerBase, self).__init__(*a, **k)
        self._priority = priority

    def __add__(self, other):
        return CompoundLayer(self, other)

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, priority):
        if priority != self._priority:
            if self.owner:
                raise RuntimeError("Cannot change priority of a layer while it's owned")
            self._priority = priority

    def grab(self, client, *a, **k):
        if client == self.owner:
            self.on_received(client, *a, **k)
            return True
        return super(LayerBase, self).grab(client, *a, **k)


class Layer(LayerBase):
    """
    A layer provides a convenient interface to element resources. In a
    layer, you can group several elements by name.  The layer itself
    is an exclusive resource.  When grabbing the layer, it will try to
    grab all elements and will forward them to its own owner when he
    receives them, and will take them from him when they are
    release. The layer with give and take away the elements from its
    client using methods of the form::
    
        client.set[element-name](element)
    
    Where [element-name] is the name the element was given in this
    layer.  This way, layers are a convenient way to provide elements
    to components indirectly, with automatic handling of competition
    for them.
    
    Note that [element-name] can not be any of the following reserved
    names: priority, grab, release, on_received, on_lost, owner,
    get_owner
    
    If [element-name] starts with an underscore (_) it is considered
    private.  It is grabbed but it is not delivered to the client.
    """

    def __init__(self, priority = None, **elements):
        super(Layer, self).__init__()
        self._priority = priority
        self._name_to_elements = dict(izip(elements.iterkeys(), repeat(None)))
        self._element_to_names = dict()
        self._element_clients = dict()
        for name, element in elements.iteritems():
            self._element_to_names.setdefault(get_element(element), []).append(name)

    def __getattr__(self, name):
        """ Provides access to elements """
        try:
            return self._name_to_elements[name]
        except KeyError:
            raise AttributeError

    def on_received(self, client, *a, **k):
        """ Override from ExclusiveResource """
        for element in self._element_to_names.iterkeys():
            k.setdefault('priority', self._priority)
            element.resource.grab(self._get_control_client(client), *a, **k)

    def on_lost(self, client):
        """ Override from ExclusiveResource """
        for element in self._element_to_names.iterkeys():
            element.resource.release(self._get_control_client(client))

    def _get_control_client(self, client):
        try:
            element_client = self._element_clients[client]
        except KeyError:
            element_client = self._element_clients[client] = LayerClient(layer_client=client, layer=self)

        return element_client


class BackgroundLayer(LayerBase):
    """
    Special layer that will reset all elements that it grabs.
    """

    def __init__(self, *elements, **k):
        super(BackgroundLayer, self).__init__(**k)
        self._elements = [ get_element(element) for element in elements ]

    def on_received(self, client, *a, **k):
        """ Override from ExclusiveResource """
        for element in self._elements:
            k.setdefault('priority', self._priority)
            element.resource.grab(self, *a, **k)

    def on_lost(self, client):
        """ Override from ExclusiveResource """
        for element in self._elements:
            element.resource.release(self)

    def set_control_element(self, control_element, grabbed):
        if grabbed:
            control_element.reset()