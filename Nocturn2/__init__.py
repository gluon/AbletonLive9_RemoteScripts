#
# Copyright (C) 2009 Guillermo Ruiz Troyano
#
# This file is part of Nocturn Remote Script for Live (Nocturn RS4L).
#
#    Nocturn RS4L is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Nocturn RS4L is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Nocturn RS4L.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact info:
#    Guillermo Ruiz Troyano, ruiztroyano@gmail.com
#

import Live
from Nocturn import Nocturn
#import MidiRemoteScript
#from apihelper import print_api


def create_instance(c_instance):
	#print_api(Live, "Live", "/Users/Guillermo/Desarrollo/Control MIDI/LiveAPI/API/")
	#print_api(c_instance, "c_instance", "/Users/Guillermo/Desktop/")
	#print_api(MidiRemoteScript, "MidiRemoteScript", "/Users/Guillermo/Desktop/")
	return Nocturn(c_instance)
