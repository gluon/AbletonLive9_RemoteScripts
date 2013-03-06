#Embedded file name: /Applications/Ableton Live 8.app/Contents/App-Resources/MIDI Remote Scripts/QuNeo/SequencerMetronome.py
import Live
import time
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from ConfigurableButtonElement import ConfigurableButtonElement
from _Framework.InputControlElement import *
from MIDI_Map import *

class SequencerMetronome(ControlSurfaceComponent):

    def __init__(self, parent):
        ControlSurfaceComponent.__init__(self)
        self.parent = parent
        self.last_beat = None
        self.led_pad = []
        self.led_metro_buttons()
        self.last_time = None
        self.count = -1

    def update_time(self):
        if self.song().is_playing != False:
            self.new_time = self.song().get_current_beats_song_time().beats
            if self.new_time != self.last_time:
                self.count += 1
                if self.count > 3:
                    self.count = 0
            self.parent.log_message('Its been %f seconds' + str(self.new_time))
            self.led_pad[self.new_time - 1].send_value(127, True)
            self.led_pad[self.new_time - 2].send_value(0, True)
            self.led_pad[self.new_time + 2].send_value(0, True)
            self.last_time = self.new_time

    def disconnect(self):
        if self.led_pad != None:
            for row in range(4):
                self.led_pad[row].turn_off()

        self.led_pad = None

    def led_metro_buttons(self):
        for index in range(4):
            self.led_pad.append(ConfigurableButtonElement(True, MIDI_NOTE_TYPE, METRO_CHANNEL, LED_METRO_2[index], RED_HI))

    def update(self):
        pass