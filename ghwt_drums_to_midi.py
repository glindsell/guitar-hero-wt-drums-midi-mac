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


def find_iac_output():
    outputs = mido.get_output_names()

    print("MIDI outputs:")
    for name in outputs:
        print(f"  {name}")

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


def handle_event(event, midi_out):
    if event.type == pygame.JOYBUTTONDOWN:
        note = BUTTON_TO_NOTE.get(event.button)

        if note is not None:
            send_note_on(midi_out, note)
            print(f"button {event.button} → note_on {note}")

    elif event.type == pygame.JOYBUTTONUP:
        note = BUTTON_TO_NOTE.get(event.button)

        if note is not None:
            send_note_off(midi_out, note)


def main():
    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        raise RuntimeError("No controller detected.")

    joy = pygame.joystick.Joystick(0)
    joy.init()

    print(f"Using controller: {joy.get_name()}")
    print(
        f"Buttons: {joy.get_numbuttons()}, "
        f"axes: {joy.get_numaxes()}, "
        f"hats: {joy.get_numhats()}"
    )

    # Clear startup noise like JoyDeviceAdded / AudioDeviceAdded.
    pygame.event.clear()

    output_name = find_iac_output()
    midi_out = mido.open_output(output_name)

    print(f"Sending MIDI to: {output_name}")
    print("Select a GarageBand Software Instrument drum kit track, then hit the pads.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            # Event-driven: wait until pygame receives an event.
            # The timeout prevents macOS/SDL from trapping Ctrl+C forever.
            event = pygame.event.wait(100)

            if event.type != pygame.NOEVENT:
                handle_event(event, midi_out)

            # Drain any extra queued events, e.g. very quick button down/up pairs.
            for queued_event in pygame.event.get():
                handle_event(queued_event, midi_out)

    except KeyboardInterrupt:
        print("\nStopping MIDI bridge.")

    finally:
        # Avoid stuck notes in GarageBand.
        for note in set(BUTTON_TO_NOTE.values()):
            send_note_off(midi_out, note)

        midi_out.close()
        pygame.quit()


if __name__ == "__main__":
    main()
