import argparse
import sys

import pygame
import mido


BUTTON_TO_NOTE = {
    4: 36,  # kick pedal
    2: 38,  # red pad / snare
    3: 42,  # yellow cymbal / closed hi-hat
    0: 47,  # blue pad / mid tom
    5: 49,  # orange cymbal / crash
    1: 43,  # green pad / floor tom
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Bridge Guitar Hero World Tour drums to MIDI via IAC."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print controller, MIDI, and pad-hit debug output.",
    )
    return parser.parse_args()


def log(debug, message):
    if debug:
        print(message)


def find_iac_output(debug):
    outputs = mido.get_output_names()

    log(debug, "MIDI outputs:")
    for name in outputs:
        log(debug, f"  {name}")

    for name in outputs:
        if "iac" in name.lower():
            return name

    raise RuntimeError(
        "Could not find IAC MIDI output. "
        "Enable IAC Driver in Audio MIDI Setup."
    )


def send_note_on(midi_out, note):
    midi_out.send(
        mido.Message(
            "note_on",
            note=note,
            velocity=120,
            channel=9,  # MIDI channel 10, zero-indexed in mido
        )
    )


def send_note_off(midi_out, note):
    midi_out.send(
        mido.Message(
            "note_off",
            note=note,
            velocity=0,
            channel=9,
        )
    )


def handle_event(event, midi_out, debug):
    if event.type == pygame.JOYBUTTONDOWN:
        note = BUTTON_TO_NOTE.get(event.button)

        if note is not None:
            send_note_on(midi_out, note)
            log(debug, f"button {event.button} → note_on {note}")

    elif event.type == pygame.JOYBUTTONUP:
        note = BUTTON_TO_NOTE.get(event.button)

        if note is not None:
            send_note_off(midi_out, note)
            log(debug, f"button {event.button} → note_off {note}")


def main():
    args = parse_args()

    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        raise RuntimeError("No controller detected.")

    joy = pygame.joystick.Joystick(0)
    joy.init()

    log(args.debug, f"Using controller: {joy.get_name()}")
    log(
        args.debug,
        (
            f"Buttons: {joy.get_numbuttons()}, "
            f"axes: {joy.get_numaxes()}, "
            f"hats: {joy.get_numhats()}"
        ),
    )

    # Clear startup noise like JoyDeviceAdded / AudioDeviceAdded.
    pygame.event.clear()

    output_name = find_iac_output(args.debug)
    midi_out = mido.open_output(output_name)

    log(args.debug, f"Sending MIDI to: {output_name}")
    log(args.debug, "Select a GarageBand Software Instrument drum kit track, then hit the pads.")
    log(args.debug, "Press Ctrl+C to stop.\n")

    try:
        while True:
            # Event-driven wait with timeout so Ctrl+C remains reliable.
            event = pygame.event.wait(100)

            if event.type != pygame.NOEVENT:
                handle_event(event, midi_out, args.debug)

            # Drain any extra queued events, e.g. quick button down/up pairs.
            for queued_event in pygame.event.get():
                handle_event(queued_event, midi_out, args.debug)

    except KeyboardInterrupt:
        log(args.debug, "\nStopping MIDI bridge.")

    finally:
        # Avoid stuck notes in GarageBand.
        for note in set(BUTTON_TO_NOTE.values()):
            send_note_off(midi_out, note)

        midi_out.close()
        pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
