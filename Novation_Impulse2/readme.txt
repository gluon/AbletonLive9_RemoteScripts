IMPORTANT!

since Ableton 9.1.2 some API has been changed

the new version is for Ableton 9.1.2 and higher

for old version please use version from a folder Novation_Impulse2_9_1

Features

Mixer  button 9 = OverDub
Shift + Mixer  button 9  = Automation record on/off
Shift + Rec  = Metronome on/off

Shift + PLay = Undo
Shift + Stop = Stop all clips

Shift + track mixer button = rec this track.. 

Shift + Clip buttons are now clip stop.

Shift + Ffwd/Back  - next/previous device 


Known issues that cannot be fixed 
1) After moving track with Shift+Track buttons are not returned to inital condition. 
    Also happens sometimes in other cases (like bank switching with Shift). 
   Workaround - press and release Shit again.
2) Pressin shift + (mutes/solos) flip button leds to unpredictable results.
   Workaround - do not do that, if you have done that, just press and release shift.

The reason for these problems is that when you use shift+track or shift+bank, the message "shift off" is not sent.
This is out of the scope of what I can do. The bug report is sent to Novation.

Known issues and todo:
FIXED: 1) impulse does not disconnect properly and does  not send disconnection message. 
FIXED  1.5) refactor shift - move it to main class.
FIXED: 2)when track goes down, the bank is not changed. 
3) on initialize mute/solo buttons do not light
  workaround - press shift button.
4) when arming a single track make the track selected 


Future things to implement. 

DONE 1) mixer9 - overdub
DONE 3) Shift + Stop - stop all clips.
   
   
FIXED:4) Shift+Mixer9 - Automation record on/off
4.5) Shift + Rec = metronome
5) Shift + Loop switch session/arrangement (as loop is the button that also changes in this case)
FIXED: 6) Shift + play Undo (as play is like backspace but turned opposite)

DONE: another parallel feature - Shift + drum pad in clip mode - stop the selected clip. 

think of re-mapping drum pads for another notes.

7) display messages, when
   metronome on/off
   undo
   switch session/arrangement
   overdub
   automation arm

2) Shift + Mixer 9 - automation arm (seems to be rather hard - not sure there is API for that)


