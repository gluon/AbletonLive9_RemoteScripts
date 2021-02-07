# uncompyle6 version 2.9.10
# Python bytecode 2.7 (62211)
# Decompiled from: Python 2.7.13 (default, Dec 17 2016, 23:03:43) 
# [GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)]
# Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/pushbase/selection.py
# Compiled at: 2016-05-20 03:43:52
"""
Object that encapsulates selection in the Push controller.
"""
from __future__ import absolute_import, print_function
import Live

class Selection(object):
    """
    Object that encapsulates selection.
    
    [jbo] The intent of this object is to grow its interface until no
    'view.selected_*' access are done in any part of the script.  This
    way, it should be easy to change our selection model such that
    multiple-Push controllers can play together properly.  Also, feel
    free to make these properties listenables when neccesary.
    """

    @property
    def selected_device(self):
        """
        Device with the blue hand.
        """
        raise NotImplementedError

    @property
    def selected_object(self):
        """
        Current object that is selected.
        """
        raise NotImplementedError

    @property
    def selected_track(self):
        """
        Current track that is selected.
        """
        raise NotImplementedError

    @property
    def selected_scene(self):
        """
        Current scene that is selected.
        """
        raise NotImplementedError

    @property
    def hotswap_target(self):
        """
        Current object that is selected.
        """
        raise NotImplementedError


class PushSelection(Selection):
    """
    Push selection object.  So far it is read-only and just accesses
    the appropiate components.  Ideally we should refactor a bit and
    make all components set and query the selection via this object
    and not otherwise.
    """

    def __init__(self, application=None, device_component=None, navigation_component=None, *a, **k):
        super(PushSelection, self).__init__(*a, **k)
        self._device_component = device_component
        self._navigation_component = navigation_component
        self._application = application
        self._browser = application.browser

    @property
    def selected_device(self):
        return self._device_component.device()

    def _get_selected_object(self):
        return self._navigation_component.selected_object

    def _set_selected_object(self, lom_object):
        if isinstance(lom_object, Live.DrumPad.DrumPad):
            lom_object.canonical_parent.view.selected_drum_pad = lom_object
        if isinstance(lom_object, Live.Chain.Chain):
            lom_object.canonical_parent.view.selected_chain = lom_object
        else:
            self._application.get_document().view.select_device(lom_object, False)

    selected_object = property(_get_selected_object, _set_selected_object)

    @property
    def selected_track(self):
        return self._application.get_document().view.selected_track

    @property
    def hotswap_target(self):
        """
        Current object that is selected.
        """
        return self._browser.hotswap_target