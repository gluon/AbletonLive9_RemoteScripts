#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/_Framework/Resource.py
from __future__ import absolute_import
from functools import partial
from .Proxy import Proxy
from .Util import index_if, nop, first, NamedTuple
DEFAULT_PRIORITY = 0

class Resource(object):

    def grab(self, client, *a, **k):
        raise NotImplemented

    def release(self, client):
        raise NotImplemented

    def get_owner(self):
        raise NotImplementedError

    owner = property(lambda self: self.get_owner())


class CompoundResource(Resource):
    """
    A resource that composes two resources, making sure that both
    grabs have to be successfull for the compound to be adquired.
    """

    def __init__(self, first_resource = None, second_resource = None, *a, **k):
        super(CompoundResource, self).__init__(*a, **k)
        self._first_resource = first_resource
        self._second_resource = second_resource

    def grab(self, client, *a, **k):
        if self._first_resource.grab(client, *a, **k):
            if self._second_resource.grab(client, *a, **k):
                pass
            else:
                self._first_resource.release(client)
        return self.owner == client

    def release(self, client):
        if not client:
            raise AssertionError
            client == self.owner and self._second_resource.release(client)
            self._first_resource.release(client)
            return True
        return False

    def get_owner(self):
        return self._first_resource.owner or self._second_resource.owner

    @property
    def first(self):
        return self._first_resource

    @property
    def second(self):
        return self._second_resource


def compose_resources(*resources):
    return reduce(CompoundResource, resources)


class ExclusiveResource(Resource):
    """
    A resource that can not be grabbed any client if it is owned by
    someone else already.
    """

    def __init__(self, on_received_callback = None, on_lost_callback = None, *a, **k):
        super(ExclusiveResource, self).__init__(*a, **k)
        self._owner = None
        if on_received_callback:
            self.on_received = on_received_callback
        if on_lost_callback:
            self.on_lost = on_lost_callback

    def grab(self, client, *a, **k):
        if not client is not None:
            raise AssertionError('Someone has to adquire resource')
            self._owner == None and self.on_received(client, *a, **k)
            self._owner = client
        return self._owner == client

    def release(self, client):
        if not client:
            raise AssertionError
            self._owner = client == self._owner and None
            self.on_lost(client)
            return True
        return False

    def get_owner(self):
        return self._owner

    def on_received(self, client, *a, **k):
        raise NotImplemented, 'Override or pass callback'

    def on_lost(self, client):
        raise NotImplemented, 'Override or pass callback'


class SharedResource(Resource):
    """
    A resource that has no owner and will always be grabbed.
    """

    def __init__(self, on_received_callback = None, on_lost_callback = None, *a, **k):
        super(SharedResource, self).__init__(*a, **k)
        if on_received_callback:
            self.on_received = on_received_callback
        if on_lost_callback:
            self.on_lost = on_lost_callback
        self._clients = set()

    def grab(self, client, *a, **k):
        raise client is not None or AssertionError('Someone has to adquire resource')
        self.on_received(client, *a, **k)
        self._clients.add(client)
        return True

    def release(self, client):
        if not client is not None:
            raise AssertionError
            client in self._clients and self.on_lost(client)
            self._clients.remove(client)
            for client in self._clients:
                self.on_received(client)

            return True
        return False

    def get_owner(self):
        raise False or AssertionError('Shared resource has no owner')

    def on_received(self, client, *a, **k):
        raise NotImplemented, 'Override or pass callback'

    def on_lost(self, client):
        raise NotImplemented, 'Override or pass callback'


class StackingResource(Resource):
    """
    A stacking resource is a special kind of resource that can preempt
    the current owner.  Resources are assigned to clients in order of
    arrival, this is, a new client attempting to grab will produce the
    former owner to be released.  However, when the current owner
    released ownership will be passed back to the last owner.
    
    This, clients are organised in a stack, where grabbing puts the
    client at the top, and releasing removes from wherever the client
    is in the stack.  Because ownership can change even a client does
    not release, a client should not use the resource based on the
    result of the grab() method but instead use whatever indirect API
    the concrete resource provides to assign ownership.
    
    Clients of a stacking resource can be prioritised to prevent
    preemption from a client with less priority. (For example, a modal
    dialog should not loose focus because of a normal window
    appearing.)
    """

    def __init__(self, on_received_callback = None, on_lost_callback = None, *a, **k):
        super(StackingResource, self).__init__(*a, **k)
        self._clients = []
        self._owners = set()
        if on_received_callback:
            self.on_received = on_received_callback
        if on_lost_callback:
            self.on_lost = on_lost_callback

    def grab(self, client, priority = None):
        if not client is not None:
            raise AssertionError
            if priority is None:
                priority = DEFAULT_PRIORITY
            old_owners = self._owners
            self._remove_client(client)
            self._add_client(client, priority)
            new_owners = self._actual_owners()
            new_owners != old_owners and self._on_lost_set(set(old_owners) - set(new_owners))
            self._on_received_set(new_owners)
            self._owners = new_owners
        return True

    def _on_lost_set(self, clients):
        for client in clients:
            self.on_lost(client)

    def _on_received_set(self, clients):
        for client in clients:
            self.on_received(client)

    def release(self, client):
        if not client is not None:
            raise AssertionError
            old_owners = self._owners
            result = self._remove_client(client)
            new_owners = self._actual_owners()
            self._owners = new_owners != old_owners and new_owners
            self._on_lost_set(set(old_owners) - set(new_owners))
            self._on_received_set(new_owners)
        return result

    def release_all(self):
        """
        Releases all stacked clients.
        """
        for client, _ in list(self._clients):
            self.release(client)

    def _add_client(self, client, priority):
        idx = index_if(lambda (_, p): p > priority, self._clients)
        self._clients.insert(idx, (client, priority))

    def _remove_client(self, client):
        idx = index_if(lambda (c, _): c == client, self._clients)
        if idx != len(self._clients):
            del self._clients[idx]
            return True

    def _actual_owners(self):
        if self._clients:
            return [self._clients[-1][0]]
        return []

    @property
    def max_priority(self):
        if self._clients:
            return self._clients[-1][1]
        return DEFAULT_PRIORITY

    @property
    def stack_size(self):
        return len(self._clients)

    def get_owner(self):
        raise not self._owners or len(self._owners) == 1 or AssertionError
        for owner in self._owners:
            return owner

    @property
    def clients(self):
        return map(first, self._clients)

    @property
    def owners(self):
        return self._owners

    def on_received(self, client):
        raise NotImplemented, 'Override or pass callback'

    def on_lost(self, client):
        raise NotImplemented, 'Override or pass callback'

    def release_stacked(self):
        clients = self.clients
        owners = self.owners
        for client in clients:
            if client not in owners:
                self.release(client)


class PrioritizedResource(StackingResource):
    """
    A prioritized resource shares the resource among all the clients
    with the same priority.
    """

    def _actual_owners(self):
        max_priority = self.max_priority
        return [ client for client, priority in self._clients if priority == max_priority ]


class ClientWrapper(NamedTuple):
    wrap = partial(nop)
    unwrap = partial(nop)


class ProxyResource(Proxy):
    """
    A resource that forwards to another resource.  One may specify a
    'proxy_client' function that can wrap the client to adapt it to
    the proxied resource requirements.
    """

    def __init__(self, proxied_resource = None, client_wrapper = ClientWrapper(), *a, **k):
        raise proxied_resource or AssertionError
        super(ProxyResource, self).__init__(proxied_object=proxied_resource, *a, **k)
        self._client_wrapper = client_wrapper

    def grab(self, client, *a, **k):
        self.__getattr__('grab')(self._client_wrapper.wrap(client), *a, **k)

    def release(self, client, *a, **k):
        self.__getattr__('release')(self._client_wrapper.wrap(client), *a, **k)

    @property
    def owner(self):
        return self._client_wrapper.unwrap(self.__getattr__('owner'))

    @property
    def owners(self):
        return map(self._client_wrapper.unwrap, self.__getattr__('owners'))