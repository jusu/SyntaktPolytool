# SyntaktPolytool.py -- polyphonic helper for Elektron Syntakt and other digis

import mido
import time
import os

# Add your midi input device here
inputs = ['minilogue xd KBD/KNOB', 'LPK25']
output = 'Elektron Syntakt'
input_found = None

# Continue when midi input and output has been found
while True:
    input_names = mido.get_input_names()
    output_names = mido.get_output_names()

    for input in inputs:
        if input in input_names:
            input_found = input
            break

    if input_found and output in output_names:
        break

    time.sleep(3)
    print(f'Looking for {inputs} + Syntakt...')
    print(f'Inputs:  {mido.get_input_names()}')
    print(f'Outputs: {mido.get_output_names()}')

inport = mido.open_input(input)
outport = mido.open_output(output)
syninput = mido.open_input(output)

# Link Syntakt tracks
# For this feature, set Settings -> Midi config -> Channels -> FX Control CH to 13
def link_syntakt_tracks(msg):
    if msg.type == 'clock':
        return

    if msg.type == 'control_change' and msg.channel == 13:
        for ch in range(8):
            m = mido.Message('control_change', channel=ch, control=msg.control, value=msg.value)
            outport.send(m)

    if msg.type == 'control_change' and msg.channel <= 7:
        for ch in range(8):
            if ch != msg.channel:
                m = mido.Message('control_change', channel=ch, control=msg.control, value=msg.value)
                outport.send(m)

    print(f'Syntakt: {msg}')

syninput.callback = link_syntakt_tracks

#
# Polychannel routing
#

mode = 'polychannel'
autochannel_channel = 14

sustain = False
pressed = {}
d = {} # note -> [] of channels used by note

mapcc = True # map minilogue encoders to Syntakt

def channels_used():
    p = ['0','0','0','0','0','0','0','0']
    # To play analogue channels only, set this to:
    #p = ['1','1','1','1','1','1','1','1','0','0','0']
    for note, ch in d.items():
        for x in ch:
            p[x] = '1'
    return p

# Map some minilogue controls to Syntakt
ccmap = {
    43: 74, # Filter frequency
    44: 75, # Filter resonance
    16: 79, # Amp Attack
    17: 81, # Amp Decay
    18: 82, # Amp Sustain
    19: 83, # Amp Relese
}

for msg in inport:
    if msg.type == 'clock':
        continue

    if msg.type == 'control_change' and msg.control == 64:
        if mode == 'autochannel':
            msg.channel = autochannel_channel-1
            outport.send(msg)
        if mode == 'polychannel':
            for ch in range(8):
                msg.channel = ch
                outport.send(msg)

        sustain = msg.value == 127
        if mode == 'polychannel' and not sustain:
            d2 = {}
            for note, ch in d.items():
                for x in ch:
                    if note not in pressed or pressed[note] == False:
                        m = mido.Message('note_off', note=note, velocity=0, channel=x)
                        outport.send(m)
                    else:
                        if note not in d2:
                            d2[note] = []
                        d2[note].append(x)

            d = d2

    if msg.type == 'control_change' and msg.control != 64 and mapcc:
        if msg.control in ccmap:
            for ch in range(8):
                outport.send(mido.Message('control_change', channel=ch, control=ccmap[msg.control], value=msg.value))

    if mode == 'autochannel':
        if msg.type == 'note_on' or msg.type == 'note_off':
            msg.channel = autochannel_channel-1
            outport.send(msg)

    if mode == 'polychannel':
        if msg.type == 'note_on':
            pressed[msg.note] = True
            used = channels_used()
            if '0' in used:
                n = used.index('0')
                if n == -1:
                    print('No channels left')
                    continue
                if not msg.note in d:
                    d[msg.note] = []
                d[msg.note].append(n)
                msg.channel = n
                outport.send(msg)

        if msg.type == 'note_off':
            if msg.note in pressed:
                pressed.pop(msg.note)

        if msg.type == 'note_off' and sustain == False:
            if msg.note in d:
                ch = d[msg.note]
                d.pop(msg.note)
                for x in ch:
                    msg.channel = x
                    outport.send(msg)

    print(msg)
    print(channels_used())
    print(d)
    print(pressed)
