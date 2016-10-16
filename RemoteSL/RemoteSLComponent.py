from consts import *

class RemoteSLComponent:
    """Baseclass for a subcomponent of the RemoteSL.
    Just defines some handy shortcuts to the main scripts functions...
    for more details about the methods, see the RemoteSLs doc strings
    """


    def __init__(self, remote_sl_parent):
        self.__parent = remote_sl_parent
        self.__support_mkII = False



    def application(self):
        return self.__parent.application()



    def song(self):
        return self.__parent.song()



    def send_midi(self, midi_event_bytes):
        self.__parent.send_midi(midi_event_bytes)



    def request_rebuild_midi_map(self):
        self.__parent.request_rebuild_midi_map()



    def disconnect(self):
        pass



    def build_midi_map(self, script_handle, midi_map_handle):
        pass



    def refresh_state(self):
        pass



    def update_display(self):
        pass



    def cc_status_byte(self):
        return CC_STATUS + SL_MIDI_CHANNEL



    def support_mkII(self):
        return self.__support_mkII



    def set_support_mkII(self, support_mkII):
        self.__support_mkII = support_mkII




