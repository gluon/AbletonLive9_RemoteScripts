# nanoKONTROLMyr

A midi remote script for use with Ableton Live 8 and the Korg nanoKontrol.

## Set-Up
1. Download and Unzip the file.

2. Move the nanoKONTROLMyr folder to the MidiRemoteScript folder within your Ableton Live application folder.

3. Open your Korg nano series editor and load the preset within the NanoKontrol Presets folder, over-writing your previous settings.

4. Select nanoKONTROLMyr as a control surface in the midi pane of the preferences window.

## Mappings

### Scenes
Scene 1 controls tracks 1 - 8
Scene 2 controls tracks 9 - 16
Scene 3 maps the encoders to the selected device and provides functions for moving tracks and devices.
Scene 4 is free for mapping to whatever you like, sending on midi channel 4.

### Global
The Ninth Slider is Always mapped to Master Volume, regardless of scene or midi channel.
The Ninth Encoder is Always mapped to Cue Volume, regardless of scene or midi channel.

### Transport
Transport functions only work when receiving midi cc numbers on channel 16.
Different functions are called when in session view and arranger view for some of the buttons. The Loop button acts as a Shift to allow more functions to be called with the other transport buttons.

Loop = Shift
Play = Play (Scene Launch when Shift held)
Stop = Stop (Stop All Clips when Shift held)
Record = Record (Overdub On/Off when Shift held)

Session Specific
Rewind = Scene Up (Scene Up by 5 when Shift held)
Forward = Scene Down (Scene Down by 5 when Shift held)

Arranger Specific
Rewind = Cue Position Left
Forward = Cue Position Right

### Encoders
The Encoders map to the Pans of the tracks. When sent on different midi channel numbers they map to different tracks. Channel 1 maps to tracks 1 - 8 and Channel 2 maps to 9 - 16 etc.
When sent on midi channel 16 they map to the selected device. This works in conjunction with the pads and buttons sending on channel 16 which provide functions for moving track and controlling devices.

### Sliders
The Sliders map to the Volumes of the tracks. The tracks they are mapped to changes with the midi channel they are sent on. Channel 1 maps to tracks 1 - 8 and Channel 2 maps to 9 - 16 etc.
There is as yet no function for when they are sent on channel 16, so they are free for mapping as you wish.

### Top Row of Buttons
The buttons on the top row turn Tracks On/Off. The Ninth Button on the row acts as a Shift and when this is held the other buttons Record Arm the tracks. They function the same as the sliders and encoders in that they map to tracks depending on the midi channel.
However, when sent on midi channel 16 the buttons select and view tracks 1 - 8 mapping the encoders above to the first device in that track.

### Bottom Row of Bottons/Pads
The buttons, or pads, on the bottom row Trigger Clips. The Ninth Button on the row acts as a Shift and when this is held the other buttons Stop the relevant clips. They function the same as the sliders, encoders and top row of buttons in that they map to tracks depending on the midi channel.
However, when sent on midi channel 16 the buttons provide various functions for controlling devices.

Button 10 = Track Left
Button 11 = Track Right
Button 12 = Device Left
Button 13 = Device Right
Button 14 = Bank 1 (When ninth button is held Bank 3)
Button 15 = Bank 2 (When ninth button is held Bank 4)
Button 16 = Device On/Off
Button 17 = Clip View/Device View

# Attributions

The contents of this repository is based on nanoKONTROLMyr by Myralfur - james@waterworth.org.uk
