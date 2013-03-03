#Embedded file name: /Users/versonator/Hudson/live/Projects/AppLive/Resources/MIDI Remote Scripts/_Framework/Resource.py
from _Framework.Util import index_if, first

class Resource(object):

    def grab(self, client, *a, **k):
        raise NotImplemented

    def release(self, client):
        raise NotImplemented

    def get_owner(self):
        raise NotImplementedError

    owner = property(lambda self: self.get_owner())


class CompoundResource(Resource):

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

    def __init__(self, on_grab_callback = None, on_release_callback = None, *a, **k):
        super(ExclusiveResource, self).__init__(*a, **k)
        self._owner = None
        if on_grab_callback:
            self.on_grab = on_grab_callback
        if on_release_callback:
            self.on_release = on_release_callback

    def grab(self, client, *a, **k):
        if not client is not None:
            raise AssertionError, 'Someone has to adquire resource'
            self._owner == None and self.on_grab(client, *a, **k)
            self._owner = client
        return self._owner == client

    def release(self, client):
        if not client:
            raise AssertionError
            self._owner = client == self._owner and None
            self.on_release(client)
            return True
        return False

    def get_owner(self):
        return self._owner

    def on_grab(self, client, *a, **k):
        raise NotImplemented, 'Override or pass callback'

    def on_release(self, client):
        raise NotImplemented, 'Override or pass callback'


class SharedResource(Resource):
    """
    A resource that has no owner and will always be grabbed.
    """

    def __init__(self, on_grab_callback = None, on_release_callback = None, *a, **k):
        super(SharedResource, self).__init__(*a, **k)
        if on_grab_callback:
            self.on_grab = on_grab_callback
        if on_release_callback:
            self.on_release = on_release_callback
        self._clients = set()

    def grab(self, client, *a, **k):
        raise client is not None or AssertionError, 'Someone has to adquire resource'
        self.on_grab(client, *a, **k)
        self._clients.add(client)
        return True

    def release(self, client):
        if not client:
            raise AssertionError
            client in self._clients and self.on_release(client)
            self._clients.remove(client)
            for client in self._clients:
                self.on_grab(client)

            return True
        return False

    def get_owner(self):
        raise False or AssertionError, 'Shared resource has no owner'

    def on_grab(self, client, *a, **k):
        raise NotImplemented, 'Override or pass callback'

    def on_release(self, client):
        raise NotImplemented, 'Override or pass callback'


class PrioritizedResource(Resource):
    """
    A prioritized resource shares the resource among all the clients
    with the same priority.
    """
    default_priority = 0

    def __init__(self, on_grab_callback = None, on_release_callback = None, *a, **k):
        super(PrioritizedResource, self).__init__(*a, **k)
        self._clients = []
        self._owners = set()
        if on_grab_callback:
            self.on_grab = on_grab_callback
        if on_release_callback:
            self.on_release = on_release_callback

    def grab(self, client, priority = None):
        if not client is not None:
            raise AssertionError
            if priority is None:
                priority = self.default_priority
            old_owners = self._owners
            self._remove_client(client)
            self._add_client(client, priority)
            new_owners = self._actual_owners()
            self._owners = new_owners != old_owners and new_owners
            self._on_release_set(old_owners - new_owners)
            self._on_grab_set(new_owners)
        return client in new_owners

    def _on_release_set(self, clients):
        for client in clients:
            self.on_release(client)

    def _on_grab_set(self, clients):
        for client in clients:
            self.on_grab(client)

    def release(self, client):
        if not client is not None:
            raise AssertionError
            old_owners = self._owners
            self._remove_client(client)
            new_owners = self._actual_owners()
            self._owners = new_owners != old_owners and new_owners
            self._on_release_set(old_owners - new_owners)
            self._on_grab_set(new_owners)
        return client in old_owners

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

    def _actual_owners(self):
        max_priority = self.max_priority
        return set([ client for client, priority in self._clients if priority == max_priority ])

    @property
    def max_priority(self):
        return self._clients[-1][1] if self._clients else self.default_priority

    @property
    def stack_size(self):
        return len(self._clients)

    def get_owner(self):
        raise False or AssertionError, 'Shared resource has no owner'

    @property
    def owners(self):
        return self._actual_owners()

    def on_grab(self, client):
        raise NotImplemented, 'Override or pass callback'

    def on_release(self, client):
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
    default_priority = 0

    def __init__(self, on_grab_callback = None, on_release_callback = None, *a, **k):
        super(StackingResource, self).__init__(*a, **k)
        self._clients = []
        self._owner = None
        if on_grab_callback:
            self.on_grab = on_grab_callback
        if on_release_callback:
            self.on_release = on_release_callback

    def grab(self, client, priority = None):
        if not client is not None:
            raise AssertionError
            if priority is None:
                priority = self.default_priority
            old_owner = self._owner
            self._remove_client(client)
            self._add_client(client, priority)
            new_owner = self._actual_owner()
            if new_owner != old_owner:
                old_owner is not None and self.on_release(old_owner)
            self.on_grab(new_owner)
            self._owner = new_owner
        return new_owner == client

    def release(self, client):
        if not client is not None:
            raise AssertionError
            old_owner = self._owner
            self._remove_client(client)
            new_owner = self._actual_owner()
            if new_owner != old_owner:
                self._owner = new_owner
                self.on_release(old_owner)
                new_owner is not None and self.on_grab(new_owner)
        return old_owner == client

    def release_stacked(self):
        """
        Releases all objects that are stacked but do not own the
        resource.
        """
        self.release_if(lambda client: client != self.owner)

    def release_if(self, predicate):
        """
        Releases all objects that satisfy a predicate.
        """
        for client, _ in list(self._clients):
            if predicate(client):
                self.release(client)

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

    def _actual_owner(self):
        return self._clients[-1][0] if self._clients else None

    @property
    def stack_clients(self):
        return map(first, self._clients)

    @property
    def max_priority(self):
        return self._clients[-1][1] if self._clients else self.default_priority

    @property
    def stack_size(self):
        return len(self._clients)

    def get_owner(self):
        return self._owner

    def on_grab(self, client):
        raise NotImplemented, 'Override or pass callback'

    def on_release(self, client):
        raise NotImplemented, 'Override or pass callback'