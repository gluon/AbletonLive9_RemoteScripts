"""
# LiveUtils, a collection of simple utility functions for controlling Ableton Live
# Copyright (C) 2007 Rob King (rob@e-mu.org)
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
# Rob King <rob@e-mu.org> or visit http://www.e-mu.org
"""
import Live
import sys

from Logger import log

def getTrackWithId():
    trackIds =[]
    i=0
    tracks= getTracks()
    for track in tracks:
        trackName=track.name
        if(trackName.find('ConductrIdT') != -1):
            trackIds.append(str(track.name))
            trackIds.append(i)
                
        i=i+1
    
    return trackIds

def getTrackDevicesWithId():
    deviceIds =[]
    i=0
    j=0
    tracks= getTracks()
    for track in tracks:
        for device in track.devices:
            deviceName=device.name
            log(device.name)
            if(deviceName.find('ConductrId') != -1):
                deviceIds.append(str(device.name))
                deviceIds.append(i)
                deviceIds.append(j)
                
                
            j=j+1
        
        j=0
        i=i+1
    
    return deviceIds        
    
def getSong():
    """Gets a the current Song instance"""
    return Live.Application.get_application().get_document()

def continuePlaying():
    """Continues Playing"""
    getSong().continue_playing()

def playSelection():
    """Plays the current selection"""
    getSong().play_selection()

def jumpBy(time):
    """Jumps the playhead relative to it's current position by time.  Stops playback."""
    getSong().jump_by(time)
    
def scrubBy(time):
    """Jumps the playhead relative to it's current position by time.  Does not stop playback"""
    getSong().scrub_by(time)

def play():
    """Starts Ableton Playing"""
    print "playing"
    getSong().start_playing()

def stopClips():
    """Stops all currently playing clips"""
    getSong().stop_all_clips()

def stop():
    """Stops Ableton"""
    getSong().stop_playing()

def currentTime(time = None):
    """Sets/Returns the current song time"""
    song = getSong()
    if time is not None:
        song.current_song_time = time
    return getSong().current_song_time

def getScenes():
    """Returns a list of scenes"""
    return getSong().scenes

def getScene(num):
    """Returns scene number (num) (starting at 0)"""
    return getSong().scenes[num]

def launchScene(scene):
    """Launches scene number (scene)"""
    getScene(scene).fire()

def getTracks():
    """Returns a list of tracks"""
    return getSong().tracks

def getTrack(num):
    """Returns track number (num) (starting at 0)"""
    return getSong().tracks[num]

def stopTrack(trackNumber):
    """Stops all clips in track number (trackNumber)"""
    track = getTrack(trackNumber)
    for clipSlot in track.clip_slots:
        clipSlot.stop()
    
def getTempo():
    """Returns the current song tempo"""
    return getSong().tempo

def setTempo(tempo):
    getSong().tempo = tempo

def jumpToNextCue():
    getSong().jump_to_next_cue()    

def jumpToPrevCue():
    getSong().jump_to_prev_cue()
    
def armTrack(num):
    """Arms track number (num)"""
    getTrack(num).arm = 1

def disarmTrack(num):
    """Disarms track number (num)"""
    getTrack(num).arm = 0

def toggleArmTrack(num):
    """Toggles the armed state of track number (num)"""
    armed = getTrack(num).arm
    if armed:
        getTrack(num).arm = 0
    else:
        getTrack(num).arm = 1

def muteTrack(track, ty = 0):
    """Mutes track number (num)"""
    if ty == 1:
        getSong().return_tracks[track].mute = 1
    else:
        getTrack(track).mute = 1

def unmuteTrack(track, ty = 0):
    """Unmutes track number (num)"""
    if ty == 1:
        getSong().return_tracks[track].mute = 0
    else:    
        getTrack(track).mute = 0
    
def toggleMuteTrack(num):
    """Toggles the muted state of track number (num)"""
    muted = getTrack(num).mute
    if muted:
        getTrack(num).mute = 0
    else:
        getTrack(num).mute = 1

def soloTrack(track, ty = 0):
    """Solo's track number (num)"""
    if ty == 1:
        getSong().return_tracks[track].solo = 1
    else:
        getTrack(track).solo = 1    
    
def unsoloTrack(track, ty = 0):
    """Un-solos track number (num)"""
    if ty == 1:
        getSong().return_tracks[track].solo = 0
    else:
        getTrack(track).solo = 0
    
def toggleSoloTrack(num):
    """Toggles the soloed state of track number (num)"""
    soloed = getTrack(num).solo
    if soloed:
        getTrack(num).solo = 0
    else:
        getTrack(num).solo = 1

def trackVolume(track, volume = None):
    """Gets/Changes the volume of track (track)

    If (volume) is specified, changes the volume of track number
    (track) to (volume), a value between 0.0 and 1.0.
    """
    if volume != None:
        getTrack(track).mixer_device.volume.value = volume
    return getTrack(track).mixer_device.volume.value

def trackPan(track, pan = None):
    """Gets/Changes the panning of track number (track)

    If (pan) is specified, changes the panning to (pan).
    (pan) should be a value between -1.0 to 1.0
    """
    if pan != None:
        getTrack(track).mixer_device.panning.value = pan
    return getTrack(track).mixer_device.panning.value

def trackSend(track, send = None, level=None):
    """Gets/Changes the level of send number (send) on track (track).

    If (level) is specified, the level of the send is set to (level),
    a value between 0.0 and 1.0
    """
    if send == None:
        return getTrack(track).mixer_device.sends
    if level != None:
        getTrack(track).mixer_device.sends[send].value = level
    return getTrack(track).mixer_device.sends[send].value
    
def trackName(track, name = None):
    """Gets/Changes the name of track (track).

    If (name) is specified, the track name is changed
    """
    if name != None:
        getTrack(track).name = name
    return str(getTrack(track).name)

def getClipSlots():
    """Gets a 2D list of all the clip slots in the song"""
    tracks = getTracks()
    clipSlots = []
    for track in tracks:
        clipSlots.append(track.clip_slots)
    return clipSlots

def getClips():
    """Gets a 2D list of all the clip in the song.

    If there is no clip in a clip slot, None is returned

    """
    tracks = getTracks()
    clips = []
    for track in getClipSlots():
        trackClips = []
        for clipSlot in track:
            trackClips.append(clipSlot.clip)
        clips.append(trackClips)
    return clips

def launchClip(track, clip):
    """Launches clip number (clip) in track number (track)"""
    getClip(track, clip).fire()

def stopClip(track, clip):
    """Stops clip number (clip) in track (track)""" 
    getClip(track, clip).stop()

def getClip(track, clip):
    """Returns clip number (clip) in track (track)"""
    # painful code!
    #clips = getClips()
    #return clips[track][clip]
    return getSong().tracks[track].clip_slots[clip].clip

def clipName(track, clip, name = None):
    """Gets/changes the name of clip number (clip) in track (track)

    In (name) is specified, the name of the clip is changed

    """
    if name != None:
        getClip(track, clip).name = name
    return str(getClip(track, clip).name)

def clipPitch(track, clip, coarse = None, fine = None):
    """Gets/changes the coarse and fine pitch shift of clip (clip) in track (track).

    If (coarse) or (fine) are specified, changes the clip's pitch.
    """
    clip = getClip(track, clip)
    if coarse != None:
        clip.pitch_coarse = coarse
    if fine != None:
        clip.pitch_fine = fine
    return (clip.pitch_coarse, clip.pitch_fine)



