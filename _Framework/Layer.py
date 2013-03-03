#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/Layer.py
"""
Module implementing a way to resource-based access to controls in an
unified interface dynamic.
"""
from Util import nop
from itertools import repeat, izip
from Resource import ExclusiveResource

class LayerError(Exception):
    pass


class UnhandledControlError(LayerError):
    pass


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
    """

    def __init__(self, *a, **controls):
        super(Layer, self).__init__(*a)
        self._layer_owner = None
        self._priority = None
        self._name_to_controls = dict(izip(controls.iterkeys(), repeat(None)))
        self._control_to_names = dict()
        for name, control in controls.iteritems():
            self._control_to_names.setdefault(control, []).append(name)

    def _get_priority(self):
        return self._priority

    def _set_priority(self, priority):
        if priority != self._priority:
            self._priority = priority
            if self._layer_owner:
                self.grab(self._layer_owner)

    priority = property(_get_priority, _set_priority)

    def __getattr__(self, name):
        """ Provides access to controls """
        try:
            return self._name_to_controls[name]
        except KeyError:
            raise AttributeError

    def set_control_element(self, control, grabbed):
        """
        Client interface of the ControlElement resource. Please do not
        call this method directly, nor use a layer to grab controls
        directly -- do it implicitly by grabing the layer.
        """
        if not self._layer_owner:
            raise AssertionError
            raise control in self._control_to_names or AssertionError, 'Control not in layer.'
            owner = self._layer_owner
            names = self._control_to_names[control]
            control = grabbed or None
        for name in names:
            try:
                handler = getattr(owner, 'set_' + name)
            except AttributeError:
                if name[0] != '_':
                    raise UnhandledControlError, 'Component %s has no handler for control %s' % (str(owner), name)
                else:
                    handler = nop

            handler(control)
            self._name_to_controls[name] = control

    def grab(self, client, *a, **k):
        if client == self.owner:
            self.on_grab(client, *a, **k)
            return True
        return super(Layer, self).grab(client, *a, **k)

    def on_grab(self, client, *a, **k):
        """ Override from ExclusiveResource """
        self._layer_owner = client
        for control in self._control_to_names.iterkeys():
            k.setdefault('priority', self._priority)
            control.resource.grab(self, *a, **k)

    def on_release(self, client):
        """ Override from ExclusiveResource """
        for control in self._control_to_names.iterkeys():
            control.resource.release(self)

        self._layer_owner = None