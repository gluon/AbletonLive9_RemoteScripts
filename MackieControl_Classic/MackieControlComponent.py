#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl_Classic/MackieControlComponent.py
from consts import *
import Live

class MackieControlComponent:
    """Baseclass for every 'sub component' of the Mackie Control. Just offers some """

    def __init__(self, main_script):
        self.__main_script = main_script

    def destroy(self):
        self.__main_script = None

    def main_script(self):
        return self.__main_script

    def shift_is_pressed(self):
        return self.__main_script.shift_is_pressed()

    def option_is_pressed(self):
        return self.__main_script.option_is_pressed()

    def control_is_pressed(self):
        return self.__main_script.control_is_pressed()

    def alt_is_pressed(self):
        return self.__main_script.alt_is_pressed()

    def song(self):
        return self.__main_script.song()

    def script_handle(self):
        return self.__main_script.handle()

    def application(self):
        return self.__main_script.application()

    def send_midi(self, bytes):
        self.__main_script.send_midi(bytes)

    def request_rebuild_midi_map(self):
        self.__main_script.request_rebuild_midi_map()