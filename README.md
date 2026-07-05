# Guitar Hero World Tour Drums to MIDI

A small Python bridge for using a **Guitar Hero World Tour PS3 drum kit** as a MIDI controller on macOS.

The drum kit does not show up directly as a MIDI device in GarageBand. It appears as a game controller, so this script listens for the drum pad button events and sends MIDI notes to macOS via the built-in **IAC Driver**.

Tested with:

- Guitar Hero World Tour drum kit
- PS3 USB dongle
- macOS
- GarageBand

## Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv ghdrums
source ghdrums/bin/activate
pip install -r requirements.txt
```

Enable the macOS virtual MIDI bus:

1. Open **Audio MIDI Setup**
2. Go to **Window → Show MIDI Studio**
3. Double-click **IAC Driver**
4. Tick **Device is online**

## Usage

Start the bridge:

```bash
source ghdrums/bin/activate
python ghwt_drums_to_midi.py
```

Then open GarageBand and create a:

**Software Instrument → Drum Kit**

Keep the script running while playing.

For debug output:

```bash
python ghwt_drums_to_midi.py --debug
```

## Current pad mapping

```text
kick pedal    → kick
red pad       → snare
yellow cymbal → closed hi-hat
blue pad      → mid tom
orange cymbal → crash
green pad     → floor tom
```

## Detecting buttons

If your kit reports different button numbers, run:

```bash
python detect_drums.py
```

Hit each pad and update the `BUTTON_TO_NOTE` mapping in `ghwt_drums_to_midi.py`.

## Notes

This is a small personal project, not a polished driver. It exists because I wanted to use an old Guitar Hero drum kit as a basic GarageBand MIDI controller.

The `ghdrums/` virtual environment should not be committed. Recreate it from `requirements.txt` instead.
