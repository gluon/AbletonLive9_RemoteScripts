"""
# Copyright (C) 2007 Nathan Ramella (nar@remix.net)
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# For questions regarding this module contact
# Nathan Ramella <nar@remix.net> or visit http://www.remix.net

This script is based off the Ableton Live supplied MIDI Remote Scripts, customised
for OSC request delivery and response. This script can be run without any extra
Python libraries out of the box. 

This is the second file that is loaded, by way of being instantiated through
__init__.py

"""

import Live
import LiveOSCCallbacks
import RemixNet
import OSC
import LiveUtils
import sys
from Logger import log
from _Framework.InputControlElement import *
from _Framework.TransportComponent import TransportComponent
from _Framework.ButtonElement import ButtonElement 
from _Framework.ControlSurface import ControlSurface 

class LiveOSC:
    __module__ = __name__
    __doc__ = "Main class that establishes the LiveOSC Component"
    #struct per emmagatzemar les referencies als callbacks per poder gestionarlos
    prlisten = {}
    plisten = {}
    dlisten = {}
    clisten = {}
    slisten = {}
    pplisten = {}
    cnlisten = {}
    cclisten = {}
    wlisten = {}
    llisten = {}
    #struct per emmagatzemar els listeners de noms
    dnlisten = {}
    sclisten = {}
    snlisten = {}
    
    _send_pos = {}
    
    mlisten = { "solo": {}, "mute": {}, "arm": {}, "panning": {}, "volume": {}, "sends": {}, "name": {}, "oml": {}, "omr": {}, "devices": {}, "color": {} }
    rlisten = { "solo": {}, "mute": {}, "panning": {}, "volume": {}, "sends": {}, "name": {}, "color": {} }
    masterlisten = { "panning": {}, "volume": {}, "crossfader": {} }
    scenelisten = {}
    
    scene = 0
    track = 0

    def __init__(self, c_instance):
        self._LiveOSC__c_instance = c_instance
      
        self.basicAPI = 0       
        self.oscEndpoint = RemixNet.OSCEndpoint()
        self.oscEndpoint.send('/remix/oscserver/startup', 1)
        """transport = TransportComponent()
        transport.set_play_button(ButtonElement(True, 0, 1, 28))"""
        log("LiveOSC initialized")
        # log("log "+str(LiveUtils.getSong().tracks[0].devices[0].name));
        # Visible tracks listener
        if self.song().tracks_has_listener(self.refresh_state) != 1:
            self.song().add_tracks_listener(self.refresh_state)
        
######################################################################
# Standard Ableton Methods

    def connect_script_instances(self, instanciated_scripts):
        """
        Called by the Application as soon as all scripts are initialized.
        You can connect yourself to other running scripts here, as we do it
        connect the extension modules
        """
        return

    def is_extension(self):
        return False

    def request_rebuild_midi_map(self):
        """
        To be called from any components, as soon as their internal state changed in a 
        way, that we do need to remap the mappings that are processed directly by the 
        Live engine.
        Dont assume that the request will immediately result in a call to
        your build_midi_map function. For performance reasons this is only
        called once per GUI frame.
        """
        return
    
    def update_display(self):
        """
        This function is run every 100ms, so we use it to initiate our Song.current_song_time
        listener to allow us to process incoming OSC commands as quickly as possible under
        the current listener scheme.
        """
        ######################################################
        # START OSC LISTENER SETUP
              
        if self.basicAPI == 0:
            # By default we have set basicAPI to 0 so that we can assign it after
            # initialization. We try to get the current song and if we can we'll
            # connect our basicAPI callbacks to the listener allowing us to 
            # respond to incoming OSC every 60ms.
            #
            # Since this method is called every 100ms regardless of the song time
            # changing, we use both methods for processing incoming UDP requests
            # so that from a resting state you can initiate play/clip triggering.

            try:
                doc = self.song()
            except:
                log('could not get song handle')
                return
            try:
                self.basicAPI = LiveOSCCallbacks.LiveOSCCallbacks(self._LiveOSC__c_instance, self.oscEndpoint)
                # Commented for stability
               
            except:
                self.oscEndpoint.send('/remix/echo', 'setting up basicAPI failed')
                log('setting up basicAPI failed');
                return
            
            # If our OSC server is listening, try processing incoming requests.
            # Any 'play' initiation will trigger the current_song_time listener
            # and bump updates from 100ms to 60ms.
            
        if self.oscEndpoint:
            try:
                self.oscEndpoint.processIncomingUDP()
            except:
                log('error processing incoming UDP packets:', sys.exc_info());
            
        if self.oscEndpoint:
            self.positions()
            #self.songtime_change()
            
        # END OSC LISTENER SETUP
        ######################################################

    """def current_song_time_changed(self):
        time = self.song().current_song_time
        if int(time) != self.time:
            self.time = int(time)
            self.oscEndpoint.send("/live/beat", self.time)"""

    def send_midi(self, midi_event_bytes):
        """
        Use this function to send MIDI events through Live to the _real_ MIDI devices 
        that this script is assigned to.
        """
        pass

    def receive_midi(self, midi_bytes):
        log("recived midi")
        return

    def can_lock_to_devices(self):
        return False

    def suggest_input_port(self):
        return ''

    def suggest_output_port(self):
        return ''
    
    def suggest_map_mode(self, cc_no, channel):
        return Live.MidiMap.MapMode.absolute

    def __handle_display_switch_ids(self, switch_id, value):
	pass
    
    
######################################################################
# Useful Methods

    def application(self):
        """returns a reference to the application that we are running in"""
        return Live.Application.get_application()

    def song(self):
        """returns a reference to the Live Song that we do interact with"""
        return self._LiveOSC__c_instance.song()

    def handle(self):
        """returns a handle to the c_interface that is needed when forwarding MIDI events via the MIDI map"""
        return self._LiveOSC__c_instance.handle()
            
    def getslots(self):
        tracks = self.song().tracks

        clipSlots = []
        for track in tracks:
            clipSlots.append(track.clip_slots)
        return clipSlots
    
    def positions(self):
        tracks = self.song().tracks
        pos = 0
        ps = 0
        if self.song().is_playing != 4: 
            for i in range(len(tracks)):
                track = tracks[i]
                if track.is_foldable != 1:
                    if track.playing_slot_index != -2:
                        if track.playing_slot_index != -1:
                            ps = track.playing_slot_index
                            clip = track.clip_slots[ps].clip
                            if clip.looping == 1:
                                if clip.playing_position < clip.loop_start:
                                    clip.looping = 0
                                    start = clip.loop_start
                                    end = clip.loop_end
                                    clip.looping = 1
                                    pos = round((clip.playing_position - start) / (end - start), 3)
                                    #pos = round((clip.loop_start - clip.playing_position) / (clip.loop_start - start), 3)
                                else:
                                    pos = round((clip.playing_position - clip.loop_start) / (clip.loop_end - clip.loop_start), 3)

                            else:
                                pos = round((clip.playing_position-clip.loop_start) / (clip.length), 3)
                            
                            self.oscEndpoint.send('/clip/playing_position',(i, ps, pos))
                        else:
                            pass
                    else:
                        pass

                else:
                    pass
        else:
            pass

    def trBlock(self, trackOffset, blocksize):
        block = []
        tracks = self.song().tracks
        
        for track in range(0, blocksize):
            block.extend([str(tracks[trackOffset+track].name)])                            
        self.oscEndpoint.send("/live/name/trackblock", block)
        self.oscEndpoint.send("/live/trackblock/refresh", block)

    def sendDeviceIds(self):
        block=[]
        block=LiveUtils.getTrackDevicesWithId()
        log("abans d'enviar osc deviceChange")
        self.oscEndpoint.send('/track/deviceChange', block)
        
    def sendTrackIds(self):
        log("entro a sendTrackIds")
        block=[]
        block=LiveUtils.getTrackWithId()
        log("abans d'enviar osc trackChange")
        self.oscEndpoint.send('/track/trackChange', block)
        

######################################################################
# Used Ableton Methods

    def disconnect(self):
        self.rem_clip_listeners()
        self.rem_mixer_listeners()
        self.rem_scene_listeners()
        self.rem_tempo_listener()
        self.rem_overdub_listener()
        self.rem_tracks_listener()
        self.rem_device_listeners()
        self.rem_transport_listener()
        self.rem_scenes_listeners()
        
        self.song().remove_tracks_listener(self.refresh_state)
        
        self.oscEndpoint.send('/remix/oscserver/shutdown', 1)
        self.oscEndpoint.shutdown()
            
    def build_midi_map(self, midi_map_handle):
        #self.refresh_state()
        """parameter=InputControlElement(MIDI_CC_TYPE,1,8)"""
        """self.parameter=self.song().tracks[0].devices[0].parameters[5].value
        channel=0
        cc=8
        Live.MidiMap.map_midi_cc(midi_map_handle, parameter, channel, cc, Live.MidiMap.MapMode.absolute, True)
        Live.MidiMap.forward_midi_cc(self._LiveOSC__c_instance.handle(), midi_map_handle, channel, cc)"""
        log("entro a build midi map")
        self.add_device_listeners()
            
    def refresh_state(self):
        log("entro a refresh state")
        self.add_clip_listeners()
        self.add_mixer_listeners()
        self.add_scene_listeners()
        self.add_scenes_listeners()
        self.add_tempo_listener()
        self.add_loop_listener()
        self.add_metronome_listener()
        self.add_overdub_listener()
        self.add_tracks_listener()
        self.add_device_listeners()
        self.add_transport_listener()
        self.add_device_id()
        self.request_rebuild_midi_map()

######################################################################
# Add / Remove Listeners   
    def add_scene_listeners(self):
        self.rem_scene_listeners()

        if self.song().scenes_has_listener(self.scenes_change) != 1:
            self.song().add_scenes_listener(self.scenes_change)

        if self.song().view.selected_scene_has_listener(self.scene_change) != 1:
            self.song().view.add_selected_scene_listener(self.scene_change)

        if self.song().view.selected_track_has_listener(self.track_change) != 1:
            self.song().view.add_selected_track_listener(self.track_change)


    def rem_scene_listeners(self):
        if self.song().view.selected_scene_has_listener(self.scene_change) == 1:
            self.song().view.remove_selected_scene_listener(self.scene_change)
            
        if self.song().view.selected_track_has_listener(self.track_change) == 1:
            self.song().view.remove_selected_track_listener(self.track_change)

    def scenes_change(self):
        log("envio event de track ids")
        self.sendTrackIds()
        self.oscEndpoint.send("/client/refresh", (1))

    def track_change(self):
        selected_track = self.song().view.selected_track
        tracks = self.song().tracks
        index = 0
        selected_index = 0
        for track in tracks:
            index = index + 1        
            if track == selected_track:
                selected_index = index
                
        if selected_index != self.track:
            self.track = selected_index
            self.oscEndpoint.send("/live/track", (selected_index))

    def scene_change(self):
        selected_scene = self.song().view.selected_scene
        scenes = self.song().scenes
        index = 0
        selected_index = 0
        for scene in scenes:
            index = index + 1        
            if scene == selected_scene:
                selected_index = index
                
        if selected_index != self.scene:
            self.scene = selected_index
            self.oscEndpoint.send("/live/scene", (selected_index))

    def add_loop_listener(self):
        self.rem_loop_listener()

        print "add loop listener"
        if self.song().loop_has_listener(self.loop_change) != 1:
            self.song().add_loop_listener(self.loop_change)

    def rem_loop_listener(self):
        if self.song().loop_has_listener(self.loop_change) == 1:
            self.song().remove_loop_listener(self.loop_change)

    def loop_change(self):
        loop = LiveUtils.getSong().loop
        self.oscEndpoint.send("/live/loop", int(loop))

    def add_metronome_listener(self):
        self.rem_metronome_listener()

        print "add metronome listener"
        if self.song().metronome_has_listener(self.metronome_change) != 1:
            self.song().add_metronome_listener(self.metronome_change)

    def rem_metronome_listener(self):
        if self.song().metronome_has_listener(self.metronome_change) == 1:
            self.song().remove_metronome_listener(self.metronome_change)

    def metronome_change(self):
        metronome = LiveUtils.getSong().metronome
        self.oscEndpoint.send("/live/metronome", int(metronome))

    def signature_change(self):
        numerator = LiveUtils.getSong().signature_numerator
        denominator = LiveUtils.getSong().signature_denominator
        self.oscEndpoint.send("/live/signature", (int(numerator), int(denominator)))


    def add_tempo_listener(self):
        self.rem_tempo_listener()

        print "add tempo/signature listener"
        if self.song().tempo_has_listener(self.tempo_change) != 1:
            self.song().add_tempo_listener(self.tempo_change)
        if self.song().signature_numerator_has_listener(self.signature_change) != 1:
            self.song().add_signature_numerator_listener(self.signature_change)
        if self.song().signature_denominator_has_listener(self.signature_change) != 1:
            self.song().add_signature_denominator_listener(self.signature_change)

    def rem_tempo_listener(self):
        if self.song().tempo_has_listener(self.tempo_change) == 1:
            self.song().remove_tempo_listener(self.tempo_change)
        if self.song().signature_numerator_has_listener(self.signature_change) == 1:
            self.song().remove_signature_numerator_listener(self.signature_change)
        if self.song().signature_denominator_has_listener(self.signature_change) == 1:
            self.song().remove_signature_denominator_listener(self.signature_change)

    def tempo_change(self):
        tempo = LiveUtils.getTempo()
        self.oscEndpoint.send("/live/tempo", (tempo))
	
    def add_transport_listener(self):
        if self.song().is_playing_has_listener(self.transport_change) != 1:
            self.song().add_is_playing_listener(self.transport_change)
            
    def rem_transport_listener(self):
        if self.song().is_playing_has_listener(self.transport_change) == 1:
            self.song().remove_is_playing_listener(self.transport_change)    
    
    def transport_change(self):
        self.oscEndpoint.send("/live/play", int(self.song().is_playing))
        
    def songtime_change(self):
        self.oscEndpoint.send("/set/playing_position", (self.song().current_song_time))
    
    def add_overdub_listener(self):
        self.rem_overdub_listener()
    
        if self.song().overdub_has_listener(self.overdub_change) != 1:
            self.song().add_overdub_listener(self.overdub_change)
	    
    def rem_overdub_listener(self):
        if self.song().overdub_has_listener(self.overdub_change) == 1:
            self.song().remove_overdub_listener(self.overdub_change)
	    
    def overdub_change(self):
        overdub = LiveUtils.getSong().overdub
        self.oscEndpoint.send("/live/overdub", int(overdub))
	
    def add_tracks_listener(self):
        self.rem_tracks_listener()
    
        if self.song().tracks_has_listener(self.tracks_change) != 1:
            self.song().add_tracks_listener(self.tracks_change)
    
    def rem_tracks_listener(self):
        if self.song().tracks_has_listener(self.tempo_change) == 1:
            self.song().remove_tracks_listener(self.tracks_change)
    
    def tracks_change(self):
        log("entro a tracks change")
        self.sendTrackIds()
        self.sendDeviceIds()
        self.oscEndpoint.send("/client/refresh", (1))

    def rem_clip_listeners(self):
        for slot in self.slisten:
            if slot != None:
                if slot.has_clip_has_listener(self.slisten[slot]) == 1:
                    slot.remove_has_clip_listener(self.slisten[slot])
    
        self.slisten = {}
        
        for clip in self.clisten:
            if clip != None:
                if clip.playing_status_has_listener(self.clisten[clip]) == 1:
                    clip.remove_playing_status_listener(self.clisten[clip])
                
        self.clisten = {}

        for clip in self.pplisten:
            if clip != None:
                if clip.playing_position_has_listener(self.pplisten[clip]) == 1:
                    clip.remove_playing_position_listener(self.pplisten[clip])
                
        self.pplisten = {}

        for clip in self.cnlisten:
            if clip != None:
                if clip.name_has_listener(self.cnlisten[clip]) == 1:
                    clip.remove_name_listener(self.cnlisten[clip])
                
        self.cnlisten = {}

        for clip in self.cclisten:
            if clip != None:
                if clip.color_has_listener(self.cclisten[clip]) == 1:
                    clip.remove_color_listener(self.cclisten[clip])
                
        self.cclisten = {}


        for clip in self.wlisten:
            if clip != None:
                if clip.is_audio_clip:
                    if clip.warping_has_listener(self.wlisten[clip]) == 1:
                        clip.remove_warping_listener(self.wlisten[clip])
                
        self.wlisten = {}
        
        for clip in self.llisten:
            if clip != None:
                if clip.looping_has_listener(self.llisten[clip]) == 1:
                    clip.remove_looping_listener(self.llisten[clip])
                
        self.llisten = {}        


        
    def add_clip_listeners(self):
        self.rem_clip_listeners()
    
        tracks = self.getslots()
        for track in range(len(tracks)):
            for clip in range(len(tracks[track])):
                c = tracks[track][clip]
                if c.clip != None:
                    self.add_cliplistener(c.clip, track, clip)
                    log("ClipLauncher: added clip listener tr: " + str(track) + " clip: " + str(clip));
                
                self.add_slotlistener(c, track, clip)
        
    def add_cliplistener(self, clip, tid, cid):
        cb = lambda :self.clip_changestate(clip, tid, cid)
        
        if self.clisten.has_key(clip) != 1:
            clip.add_playing_status_listener(cb)
            self.clisten[clip] = cb
            
        cb2 = lambda :self.clip_position(clip, tid, cid)
        if self.pplisten.has_key(clip) != 1:
            clip.add_playing_position_listener(cb2)
            self.pplisten[clip] = cb2
            
        cb3 = lambda :self.clip_name(clip, tid, cid)
        if self.cnlisten.has_key(clip) != 1:
            clip.add_name_listener(cb3)
            self.cnlisten[clip] = cb3

        if self.cclisten.has_key(clip) != 1:
            clip.add_color_listener(cb3)
            self.cclisten[clip] = cb3
        
        if clip.is_audio_clip:
            cb4 = lambda: self.clip_warping(clip, tid, cid)
            if self.wlisten.has_key(clip) != 1:
                clip.add_warping_listener(cb4)
                self.wlisten[clip] = cb4
            
        cb5 = lambda: self.clip_looping(clip, tid, cid)
        if self.llisten.has_key(clip) != 1:
            clip.add_looping_listener(cb5)
            self.llisten[clip] = cb5   
        
    def add_slotlistener(self, slot, tid, cid):
        cb = lambda :self.slot_changestate(slot, tid, cid)
        
        if self.slisten.has_key(slot) != 1:
            slot.add_has_clip_listener(cb)
            self.slisten[slot] = cb   
            
#remove mixer listeners
    def rem_mixer_listeners(self):
        # Master Track
        for type in ("volume", "panning", "crossfader"):
            for tr in self.masterlisten[type]:
                if tr != None:
                    cb = self.masterlisten[type][tr]
                
                    test = eval("tr.mixer_device." + type+ ".value_has_listener(cb)")
                
                    if test == 1:
                        eval("tr.mixer_device." + type + ".remove_value_listener(cb)")

        # Normal Tracks
        for type in ("arm", "solo", "mute"):
            for tr in self.mlisten[type]:
                if tr != None:
                    cb = self.mlisten[type][tr]
                    
                    if type == "arm":
                        if tr.can_be_armed == 1:
                            if tr.arm_has_listener(cb) == 1:
                                tr.remove_arm_listener(cb)
                                
                    else:
                        test = eval("tr." + type+ "_has_listener(cb)")
                
                        if test == 1:
                            eval("tr.remove_" + type + "_listener(cb)")
                
        for type in ("volume", "panning"):
            for tr in self.mlisten[type]:
                if tr != None:
                    cb = self.mlisten[type][tr]
                
                    test = eval("tr.mixer_device." + type+ ".value_has_listener(cb)")
                
                    if test == 1:
                        eval("tr.mixer_device." + type + ".remove_value_listener(cb)")
         
        for tr in self.mlisten["sends"]:
            if tr != None:
                for send in self.mlisten["sends"][tr]:
                    if send != None:
                        cb = self.mlisten["sends"][tr][send]

                        if send.value_has_listener(cb) == 1:
                            send.remove_value_listener(cb)
                        
                        
        for tr in self.mlisten["name"]:
            if tr != None:
                cb = self.mlisten["name"][tr]

                if tr.name_has_listener(cb) == 1:
                    tr.remove_name_listener(cb)
                    
        for tr in self.mlisten["color"]:
            if tr != None:
                cb = self.mlisten["color"][tr]

                try:
                    if tr.color_has_listener(cb) == 1:
                        tr.remove_color_listener(cb)
                except:
                    pass
    
        for tr in self.mlisten["devices"]:
            if tr != None:
                cb = self.mlisten["devices"][tr]
                log("Remove device listener in track: " + str(tr));
                
                if tr.devices_has_listener(cb) == 1:
                    tr.remove_devices_listener(cb)

        for tr in self.mlisten["oml"]:
            if tr != None:
                cb = self.mlisten["oml"][tr]

                if tr.output_meter_left_has_listener(cb) == 1:
                    tr.remove_output_meter_left_listener(cb)

        for tr in self.mlisten["omr"]:
            if tr != None:
                cb = self.mlisten["omr"][tr]

                if tr.output_meter_right_has_listener(cb) == 1:
                    tr.remove_output_meter_right_listener(cb)
                    
        # Return Tracks                
        for type in ("solo", "mute"):
            for tr in self.rlisten[type]:
                if tr != None:
                    cb = self.rlisten[type][tr]
                
                    test = eval("tr." + type+ "_has_listener(cb)")
                
                    if test == 1:
                        eval("tr.remove_" + type + "_listener(cb)")
                
        for type in ("volume", "panning"):
            for tr in self.rlisten[type]:
                if tr != None:
                    cb = self.rlisten[type][tr]
                
                    test = eval("tr.mixer_device." + type+ ".value_has_listener(cb)")
                
                    if test == 1:
                        eval("tr.mixer_device." + type + ".remove_value_listener(cb)")
         
        for tr in self.rlisten["sends"]:
            if tr != None:
                for send in self.rlisten["sends"][tr]:
                    if send != None:
                        cb = self.rlisten["sends"][tr][send]
                
                        if send.value_has_listener(cb) == 1:
                            send.remove_value_listener(cb)

        for tr in self.rlisten["name"]:
            if tr != None:
                cb = self.rlisten["name"][tr]

                if tr.name_has_listener(cb) == 1:
                    tr.remove_name_listener(cb)
                    
        for tr in self.rlisten["color"]:
            if tr != None:
                cb = self.rlisten["color"][tr]
                try:
                    if tr.color_has_listener(cb) == 1:
                        tr.remove_color_listener(cb)
                except:
                    pass
                    
        self.mlisten = { "solo": {}, "mute": {}, "arm": {}, "panning": {}, "volume": {}, "sends": {}, "name": {}, "oml": {}, "omr": {}, "devices": {}, "color": {} }
        self.rlisten = { "solo": {}, "mute": {}, "panning": {}, "volume": {}, "sends": {}, "name": {}, "color": {} }
        self.masterlisten = { "panning": {}, "volume": {}, "crossfader": {} }
    
    # afegim listeners als elements de mixer
    def add_mixer_listeners(self):
        self.rem_mixer_listeners()
        
        # Master Track
        tr = self.song().master_track
        for type in ("volume", "panning", "crossfader"):
            self.add_master_listener(0, type, tr)
        
        self.add_meter_listener(0, tr, 2)
        
        # Normal Tracks
        tracks = self.song().tracks
        for track in range(len(tracks)):
            tr = tracks[track]

            self.add_trname_listener(track, tr, 0)
            self.add_track_device_listeners(track,tr)
            
            if tr.has_audio_output:
                self.add_meter_listener(track, tr)
            
            for type in ("arm", "solo", "mute"):
                if type == "arm":
                    if tr.can_be_armed == 1:
                        self.add_mixert_listener(track, type, tr)
                else:
                    self.add_mixert_listener(track, type, tr)
                
            for type in ("volume", "panning"):
                self.add_mixerv_listener(track, type, tr)
                
            for sid in range(len(tr.mixer_device.sends)):
                self.add_send_listener(track, tr, sid, tr.mixer_device.sends[sid])
        
        # Return Tracks
        tracks = self.song().return_tracks
        for track in range(len(tracks)):
            tr = tracks[track]

            self.add_trname_listener(track, tr, 1)
            self.add_meter_listener(track, tr, 1)
            
            for type in ("solo", "mute"):
                self.add_retmixert_listener(track, type, tr)
                
            for type in ("volume", "panning"):
                self.add_retmixerv_listener(track, type, tr)
            
            for sid in range(len(tr.mixer_device.sends)):
                self.add_retsend_listener(track, tr, sid, tr.mixer_device.sends[sid])
        
    
    # Add track listeners
    def add_send_listener(self, tid, track, sid, send):
        if self.mlisten["sends"].has_key(track) != 1:
            self.mlisten["sends"][track] = {}
                    
        if self.mlisten["sends"][track].has_key(send) != 1:
            cb = lambda :self.send_changestate(tid, track, sid, send)
            
            self.mlisten["sends"][track][send] = cb
            send.add_value_listener(cb)
    
    def add_mixert_listener(self, tid, type, track):
        if self.mlisten[type].has_key(track) != 1:
            cb = lambda :self.mixert_changestate(type, tid, track)
            
            self.mlisten[type][track] = cb
            eval("track.add_" + type + "_listener(cb)")
            
    def add_mixerv_listener(self, tid, type, track):
        if self.mlisten[type].has_key(track) != 1:
            cb = lambda :self.mixerv_changestate(type, tid, track)
            
            self.mlisten[type][track] = cb
            eval("track.mixer_device." + type + ".add_value_listener(cb)")

    # Add master listeners
    def add_master_listener(self, tid, type, track):
        if self.masterlisten[type].has_key(track) != 1:
            cb = lambda :self.mixerv_changestate(type, tid, track, 2)
            
            self.masterlisten[type][track] = cb
            eval("track.mixer_device." + type + ".add_value_listener(cb)")
            
            
    # Add return listeners
    def add_retsend_listener(self, tid, track, sid, send):
        if self.rlisten["sends"].has_key(track) != 1:
            self.rlisten["sends"][track] = {}
                    
        if self.rlisten["sends"][track].has_key(send) != 1:
            cb = lambda :self.send_changestate(tid, track, sid, send, 1)
            
            self.rlisten["sends"][track][send] = cb
            send.add_value_listener(cb)
    
    def add_retmixert_listener(self, tid, type, track):
        if self.rlisten[type].has_key(track) != 1:
            cb = lambda :self.mixert_changestate(type, tid, track, 1)
            
            self.rlisten[type][track] = cb
            eval("track.add_" + type + "_listener(cb)")
            
    def add_retmixerv_listener(self, tid, type, track):
        if self.rlisten[type].has_key(track) != 1:
            cb = lambda :self.mixerv_changestate(type, tid, track, 1)
            
            self.rlisten[type][track] = cb
            eval("track.mixer_device." + type + ".add_value_listener(cb)")      

    # Track device Listener
    def add_track_device_listeners(self,tid,track):
        cbt = lambda :self.track_device_listener(tid,track)
        
        if self.mlisten["devices"].has_key(track) != 1:
            self.mlisten["devices"][track] = cbt
        
        track.add_devices_listener(cbt)
        log("Added device listener in track " + str(tid));

    # Track name listener
    def add_trname_listener(self, tid, track, ret = 0):
        cb = lambda :self.trname_changestate(tid, track, ret)

        if ret == 1:
            if self.rlisten["name"].has_key(track) != 1:
                self.rlisten["name"][track] = cb
            if self.rlisten["color"].has_key(track) != 1:
                self.rlisten["color"][track] = cb
        
        else:
            if self.mlisten["name"].has_key(track) != 1:
                self.mlisten["name"][track] = cb
            if self.mlisten["color"].has_key(track) != 1:
                self.mlisten["color"][track] = cb

        
        track.add_name_listener(cb)
        try:
            track.add_color_listener(cb)
        except:
            log("Failed adding color listener for %d" % tid)
            pass
        log("Added listeners for track %d" % tid)
    # Output Meter Listeners
    def add_meter_listener(self, tid, track, r = 0):
        cb = lambda :self.meter_changestate(tid, track, 0, r)

        if self.mlisten["oml"].has_key(track) != 1:
            self.mlisten["oml"][track] = cb

        track.add_output_meter_left_listener(cb)

        cb = lambda :self.meter_changestate(tid, track, 1, r)

        if self.mlisten["omr"].has_key(track) != 1:
            self.mlisten["omr"][track] = cb

        track.add_output_meter_right_listener(cb)

######################################################################
# Listener Callbacks
        
    # Clip Callbacks
    def clip_warping(self, clip, tid, cid):
        self.oscEndpoint.send('/live/clip/warping', (tid, cid, int(clip.warping)))
        
    def clip_looping(self, clip, tid, cid):
        self.oscEndpoint.send('/live/clip/loopstate', (tid, cid, int(clip.looping)))
    
    def clip_name(self, clip, tid, cid):
        self.oscEndpoint.send('/live/name/clip', (tid, cid, str(clip.name), clip.color))
    
    def clip_position(self, clip, tid, cid):
        send = self._send_pos.has_key(tid) and self._send_pos[tid] or 0
    
        if self.check_md(1) or (self.check_md(5) and send):
            if clip.is_playing:
                if send > 0:
                    self._send_pos[tid] -= 1
                    
                self.oscEndpoint.send('/live/clip/position', (tid, cid, clip.playing_position, clip.length, clip.loop_start, clip.loop_end))
    
    def slot_changestate(self, slot, tid, cid):
        tmptrack = LiveUtils.getTrack(tid)
        armed = tmptrack.arm and 1 or 0
        
        # Added new clip
        if slot.clip != None:
            self.add_cliplistener(slot.clip, tid, cid)
            
            playing = 1
            if slot.clip.is_playing == 1:
                playing = 2
            
            if slot.clip.is_triggered == 1:
                playing = 3
            
            length =  slot.clip.loop_end - slot.clip.loop_start
            
            self.oscEndpoint.send('/live/track/info', (tid, armed, cid, playing, length))
            self.oscEndpoint.send('/live/name/clip', (tid, cid, str(slot.clip.name), slot.clip.color))
        else:
            if self.clisten.has_key(slot.clip) == 1:
                slot.clip.remove_playing_status_listener(self.clisten[slot.clip])
                
            if self.pplisten.has_key(slot.clip) == 1:
                slot.clip.remove_playing_position_listener(self.pplisten[slot.clip])

            if self.cnlisten.has_key(slot.clip) == 1:
                slot.clip.remove_name_listener(self.cnlisten[slot.clip])

            if self.cclisten.has_key(slot.clip) == 1:
                slot.clip.remove_color_listener(self.cclisten[slot.clip])
            
            self.oscEndpoint.send('/live/track/info', (tid, armed, cid, 0, 0.0))
            self.oscEndpoint.send('/live/clip/info', (tid, cid, 0))
                
        #log("Slot changed" + str(self.clips[tid][cid]))
    
    def clip_changestate(self, clip, x, y):
        log("Listener: x: " + str(x) + " y: " + str(y));

        playing = 1
        
        if clip.is_playing == 1:
            playing = 2
            
        if clip.is_triggered == 1:
            playing = 3
            
        self.oscEndpoint.send('/live/clip/info', (x, y, playing))
        self._send_pos[x] = 3
        
        #log("Clip changed x:" + str(x) + " y:" + str(y) + " status:" + str(playing)) 
        
        
    # Mixer Callbacks
    def mixerv_changestate(self, type, tid, track, r = 0):
        val = eval("track.mixer_device." + type + ".value")
        types = { "panning": "pan", "volume": "volume", "crossfader": "crossfader" }
        
        if r == 2:
            self.oscEndpoint.send('/live/master/' + types[type], (float(val)))
        elif r == 1:
            self.oscEndpoint.send('/live/return/' + types[type], (tid, float(val)))
        else:
            self.oscEndpoint.send('/live/' + types[type], (tid, float(val)))        
        
    def mixert_changestate(self, type, tid, track, r = 0):
        val = eval("track." + type)
        
        if r == 1:
            self.oscEndpoint.send('/live/return/' + type, (tid, int(val)))
        else:
            self.oscEndpoint.send('/live/' + type, (tid, int(val)))        
    
    def send_changestate(self, tid, track, sid, send, r = 0):
        val = send.value
        
        if r == 1:
            self.oscEndpoint.send('/live/return/send', (tid, sid, float(val)))   
        else:
            self.oscEndpoint.send('/live/send', (tid, sid, float(val)))   


    # Track name changestate
    def trname_changestate(self, tid, track, r = 0):
        if r == 1:
            col = 0
            try:
                col = track.color
            except:
                pass
            self.oscEndpoint.send('/live/name/return', (tid, str(track.name), col))
        else:
            col = 0
            try:
                col = track.color
            except:
                pass
            ndevices=len(track.devices)
            self.oscEndpoint.send('/live/name/track', (tid, str(track.name), col))
            self.trBlock(0, len(LiveUtils.getTracks()))
            
    # Meter Changestate
    def meter_changestate(self, tid, track, lr, r = 0):
        if r == 2:
            if self.check_md(2):
                if lr == 0:
                    self.oscEndpoint.send('/live/master/meter', (0, float(track.output_meter_left)))
                else:
                    self.oscEndpoint.send('/live/master/meter', (1, float(track.output_meter_right)))
        elif r == 1:
            if self.check_md(3):
                if lr == 0:
                    self.oscEndpoint.send('/live/return/meter', (tid, 0, float(track.output_meter_left)))
                else:
                    self.oscEndpoint.send('/live/return/meter', (tid, 1, float(track.output_meter_right)))        
        else:
            if self.check_md(4):
                if lr == 0:
                    self.oscEndpoint.send('/live/track/meter', (tid, 0, float(track.output_meter_left)))
                else:
                    self.oscEndpoint.send('/live/track/meter', (tid, 1, float(track.output_meter_right)))
    
    def check_md(self, param):
        devices = self.song().master_track.devices
        return 1
    
        if len(devices) > 0:
            if devices[0].parameters[param].value > 0:
                return 1
            else:
                return 0
        else:
            return 0
    
    # Device Listeners
    def add_device_id(self):
        for i in range(len(self.song().tracks)):
            for j in range(len(self.song().tracks[i].devices)):
                #log("device name" + str(Live.Application.encrypt_challenge));
                """print dir(self.song())"""

    def add_device_listeners(self):
        self.rem_device_listeners()

        self.do_add_device_listeners(self.song().tracks,0)
        self.do_add_device_listeners(self.song().return_tracks,1)
        self.do_add_device_listeners([self.song().master_track],2)
            
            
    def do_add_device_listeners(self, tracks, type):
        for i in range(len(tracks)):
            self.add_devicelistener(tracks[i], i, type)
        
            if len(tracks[i].devices) >= 1:
                for j in range(len(tracks[i].devices)):
                    self.add_name_device_listener(tracks[i].devices[j])
                    #self.add_devpmlistener(tracks[i].devices[j])
                    if len(tracks[i].devices[j].parameters) >= 1:
                        for k in range (len(tracks[i].devices[j].parameters)):
                            par = tracks[i].devices[j].parameters[k]
                            self.add_paramlistener(par, i, j, k, type)
                            
                            
    def add_name_device_listener(self,device):
        log("entro a add_name_device_listener")
        cb = lambda :self.dev_name_change(device)
        if device.name_has_listener(cb) != 1:
            device.add_name_listener(cb)
            self.dnlisten[device]=cb
                          
    def rem_device_listeners(self):
        for pr in self.prlisten:
            ocb = self.prlisten[pr]
            if pr != None:
                if pr.value_has_listener(ocb) == 1:
                    pr.remove_value_listener(ocb)
        
        self.prlisten = {}
        
        for tr in self.dlisten:
            ocb = self.dlisten[tr]
            if tr != None:
                if tr.view.selected_device_has_listener(ocb) == 1:
                    tr.view.remove_selected_device_listener(ocb)
                    
        self.dlisten = {}
        
        for de in self.plisten:
            ocb = self.plisten[de]
            if de != None:
                if de.parameters_has_listener(ocb) == 1:
                    de.remove_parameters_listener(ocb)
                    
        self.plisten = {}
        #here we delete de device name listeners
        for de in self.dnlisten:
            ocb = self.dnlisten[de]
            if de != None:
                if de.name_has_listener(ocb) == 1:
                    de.remove_name_listener(ocb)
                    
        self.dnlisten = {}


    def add_devpmlistener(self, device):
        cb = lambda :self.devpm_change()

        if self.plisten.has_key(device) != 1:
            device.add_parameters_listener(cb)
            self.plisten[device] = cb
    
    def devpm_change(self):
        #self.refresh_state()
            self.add_device_listeners()
            self.oscEndpoint.send('/updateDevices', (1))
            
    def dev_name_change(self,device):
        log("entro a envio de device name change dins de la funct dev_name_change")
        name= device.name
        self.oscEndpoint.send('/devicenamechanged', (str(name)))
    
    
        
    def add_paramlistener(self, param, tid, did, pid, type):
        cb = lambda :self.param_changestate(param, tid, did, pid, type)
        
        if self.prlisten.has_key(param) != 1:
            param.add_value_listener(cb)
            self.prlisten[param] = cb
            
    def param_changestate(self, param, tid, did, pid, type):
        if type == 2:
            self.oscEndpoint.send('/live/master/device/param', (did, pid, param.value, str(param.name)))
        elif type == 1:
            self.oscEndpoint.send('/live/return/device/param', (tid, did, pid, param.value, str(param.name)))
        else:
            self.oscEndpoint.send('/live/device/param', (tid, did, pid, param.value, str(param.name)))
        
    def add_devicelistener(self, track, tid, type):
        cb = lambda :self.device_changestate(track, tid, type)
        
        if self.dlisten.has_key(track) != 1:
            track.view.add_selected_device_listener(cb)
            self.dlisten[track] = cb
               

    def track_device_listener(self, tid, track):
        log("entro a track_device_listener")
        self.sendDeviceIds()
        
                
    def device_changestate(self, track, tid, type):
        
        did = self.tuple_idx(track.devices, track.view.selected_device)

        if type == 2:
            devices = LiveUtils.getSong().master_track.devices
            nm = str(devices[int(did)].name)
            params = LiveUtils.getSong().master_track.devices[did].parameters
            onoff = params[0].value
            num = len(devices)
            self.oscEndpoint.send('/master/selected_device', (1, did, nm, onoff, num))
        elif type == 1:
            devices = LiveUtils.getSong().return_tracks[tid].devices
            nm = str(devices[int(did)].name)
            params = LiveUtils.getSong().return_tracks[tid].devices[did].parameters
            onoff = params[0].value
            num = len(devices)
            self.oscEndpoint.send('/return/selected_device', (2, tid, did, nm, onoff, num))
        else:
            devices = LiveUtils.getSong().tracks[tid].devices
            nm = str(devices[int(did)].name)
            params = LiveUtils.getSong().tracks[tid].devices[did].parameters
            onoff = params[0].value
            num = len(devices)
            self.oscEndpoint.send('/track/selected_device', (0, tid, did, nm, onoff, num))       
        
    def tuple_idx(self, tuple, obj):
        for i in xrange(0,len(tuple)):
            if (tuple[i] == obj):
                return i

    def add_scenes_listeners(self):
        self.rem_scenes_listeners()
        scenes = self.song().scenes
        for sc in range (len(scenes)):
            scene = scenes[sc]
            self.add_scenelistener(scene, sc)

    def rem_scenes_listeners(self):
        for scene in self.sclisten:
            if scene != None:
                if scene.color_has_listener(self.sclisten[scene]) == 1:
                    scene.remove_color_listener(self.sclisten[scene])
            else:
                pass
        self.sclisten = {}

        for scene in self.snlisten:
            if scene != None:
                if scene.name_has_listener(self.snlisten[scene]) == 1:
                    scene.remove_name_listener(self.snlisten[scene])
            else:
                pass
        self.snlisten = {}

    def add_scenelistener(self, scene, sc):
        cb = lambda :self.scene_namecolor_changestate(scene, sc)
        if self.sclisten.has_key(scene) != 1:
            scene.add_color_listener(cb)
            self.sclisten[scene] = cb
        else:
            pass

        cb2 = lambda :self.scene_namecolor_changestate(scene, sc)
        if self.snlisten.has_key(scene) != 1:
            scene.add_name_listener(cb2)
            self.snlisten[scene] = cb2
        else:
            pass


    def scene_namecolor_changestate(self, scene, sc):
        nm = scene.name
        self.oscEndpoint.send("/live/name/scene", (sc, repr(nm), scene.color))


