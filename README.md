
## SyntaktPolytool -- polyphonic helper for Elektron Syntakt and other digis

### Features:

- Map incoming midi to separate midi channels for polyphonic playback
- Mirror track parameter changes to other tracks (changing synth/filter etc parameter on one track will change it for all tracks)

### Usage:

Add your midi input to list of inputs in the script.

    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
    python3 SyntaktPolytool.py

Play some notes, polyphony is mapped to tracks 1-8 by default.

For track parameter mirroring to work, on Syntakt, set:

`Settings -> Midi config -> Channels -> FX Control CH` to 13
`Settings -> Midi config -> Port config -> Encoder dest` to INT+EXT

Demo

... coming up, maybe
