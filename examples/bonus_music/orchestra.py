"""BONUS - "orchestra" mode: play a melody AND a harmony at the same time.

    Standalone -- doesn't need play_melody.py. Just needs the buzzer(s).

THE ONE THING TO KNOW FIRST
  A single passive buzzer can only make ONE frequency at a time (PWM sets a
  single pitch). So a lone buzzer is *monophonic* -- it cannot truly play two
  notes at once. That's exactly why old Game Boy / NES music sounds the way it
  does. We get around it in two ways:

  PATH A - TWO BUZZERS (real harmony):
    Wire a second buzzer to another GPIO pin. The ESP32 has many independent
    PWM channels, so buzzer #1 plays the melody and buzzer #2 plays a harmony
    an octave lower -- both ringing together. Set TWO_BUZZERS = True below and
    connect the second buzzer's signal leg to GPIO 5 (other leg to GND).

  PATH B - ONE BUZZER (fake it, no extra parts):
    Flip between the two notes so fast (~120x a second) that your ear blends
    them into a shimmering chord. Not true harmony, but it sounds fuller. This
    is the default, so this file runs with a single buzzer out of the box.

TWO ESP32 BOARDS?  Yes, as a stretch -- each board plays one voice. The catch
  is starting them in sync (their clocks are independent): reset both at once,
  or wire a GPIO "start" line between them, or trigger both over WiFi. Fine for
  short tunes; they drift on long ones. One board + two buzzers is easier.

HOW TO USE
  1. Upload this file to the board and run it (F5).
  2. Default = one buzzer on GPIO 4, "fake chord" mode. You'll hear a melody
     with a bass an octave below.
  3. Got a second buzzer? Set TWO_BUZZERS = True, wire it to GPIO 5, re-run.
  4. If melodies_options.py is also on the board, set CHOICE (1..16) to pick
     any of the 16 tunes; otherwise it uses the built-ins below.

Ctrl-C to stop.
"""

import time
from machine import Pin, PWM

# ---------------- knobs campers can change ----------------
BUZZER_PIN_HI = 4        # melody buzzer
BUZZER_PIN_LO = 5        # harmony buzzer (only used if TWO_BUZZERS = True)
TWO_BUZZERS   = False    # False = fake chord on one buzzer; True = real 2-buzzer harmony
HARMONY_SHIFT = -1       # octaves for the 2nd voice: -1 = one octave lower (bass), +1 = higher
TEMPO_MS      = 400      # length of one beat (ms). Smaller = faster.
CHOICE        = 1        # which melodies_options tune (1..16); ignored if that file isn't uploaded
# ----------------------------------------------------------

# Notes and frequencies (Hz). Octave 3 is ADDED here so the harmony has room
# to drop an octave below the melody and still land on a real note.
NOTES = {
    "C3": 131, "CS3": 139, "D3": 147, "DS3": 156, "E3": 165, "F3": 175,
    "FS3": 185, "G3": 196, "GS3": 208, "A3": 220, "AS3": 233, "B3": 247,
    "C4": 262, "CS4": 277, "D4": 294, "DS4": 311, "E4": 330, "F4": 349,
    "FS4": 370, "G4": 392, "GS4": 415, "A4": 440, "AS4": 466, "B4": 494,
    "C5": 523, "CS5": 554, "D5": 587, "DS5": 622, "E5": 659, "F5": 698,
    "FS5": 740, "G5": 784, "GS5": 831, "A5": 880, "AS5": 932, "B5": 988,
    "C6": 1047,
    "REST": 0,
}

# Built-in tunes so this file runs on its own. If melodies_options.py is on the
# board, its 16 melodies are used instead (see pick_melody).
ODE_TO_JOY = [
    ("E4", 1), ("E4", 1), ("F4", 1), ("G4", 1), ("G4", 1), ("F4", 1), ("E4", 1), ("D4", 1),
    ("C4", 1), ("C4", 1), ("D4", 1), ("E4", 1), ("E4", 1.5), ("D4", 0.5), ("D4", 2),
]
TWINKLE = [
    ("C4", 1), ("C4", 1), ("G4", 1), ("G4", 1), ("A4", 1), ("A4", 1), ("G4", 2),
    ("F4", 1), ("F4", 1), ("E4", 1), ("E4", 1), ("D4", 1), ("D4", 1), ("C4", 2),
]
BUILTINS = [("Ode to Joy", ODE_TO_JOY), ("Twinkle Twinkle", TWINKLE)]

try:
    from melodies_options import MELODIES     # the 16-tune menu, if uploaded
except ImportError:
    MELODIES = []


def octave_shift(melody, delta):
    """Return a copy of a melody moved by `delta` octaves.

    Keeps a note unchanged if the shifted version isn't in NOTES (so it can
    never crash), and leaves RESTs alone.
    """
    out = []
    for note, beats in melody:
        if note == "REST":
            out.append((note, beats))
            continue
        base, octave = note[:-1], int(note[-1])
        shifted = base + str(octave + delta)
        out.append(((shifted if shifted in NOTES else note), beats))
    return out


def set_voice(buzzer, note, duty=400):
    """Point one buzzer at one note (or silence for REST)."""
    freq = NOTES[note]
    if freq == 0:
        buzzer.duty(0)
    else:
        buzzer.freq(freq)
        buzzer.duty(duty)


# ---- PATH A: two buzzers, real harmony ----
def play_duet(hi, lo, melody_hi, melody_lo):
    """Play two voices at once, one per buzzer. Both parts share the rhythm."""
    for (n1, b1), (n2, _b2) in zip(melody_hi, melody_lo):
        set_voice(hi, n1)
        set_voice(lo, n2)
        time.sleep_ms(int(b1 * TEMPO_MS))
        hi.duty(0)
        lo.duty(0)
        time.sleep_ms(20)             # tiny gap so repeated notes don't blur


# ---- PATH B: one buzzer, fake chord by fast alternation ----
def play_chord(buzzer, notes, beats):
    """Flicker between several notes fast enough that they blend into a chord."""
    end = time.ticks_add(time.ticks_ms(), int(beats * TEMPO_MS))
    while time.ticks_diff(end, time.ticks_ms()) > 0:
        for n in notes:
            freq = NOTES[n]
            if freq == 0:
                buzzer.duty(0)
            else:
                buzzer.freq(freq)
                buzzer.duty(512)
            time.sleep_ms(8)          # ~120 flips/sec -> the ear fuses them
    buzzer.duty(0)
    time.sleep_ms(20)


def play_duet_one_buzzer(buzzer, melody_hi, melody_lo):
    """Play a two-note 'chord' each beat on a single buzzer."""
    for (n1, b1), (n2, _b2) in zip(melody_hi, melody_lo):
        play_chord(buzzer, [n1, n2], b1)


def list_melodies():
    print("Melodies (set CHOICE at the top):")
    for i, (title, _) in enumerate(MELODIES, 1):
        print("  {:2d}. {}".format(i, title))


def pick_melody():
    """Choose the melody: from melodies_options if present, else a built-in."""
    catalog = MELODIES if MELODIES else BUILTINS
    idx = CHOICE
    if MELODIES and CHOICE is None:
        list_melodies()
        try:
            idx = int(input("Melody number: "))
        except (ValueError, EOFError):
            idx = 1
    if not (1 <= idx <= len(catalog)):
        idx = 1
    title, melody = catalog[idx - 1]
    print("Melody:", title)
    return melody


def main():
    hi = PWM(Pin(BUZZER_PIN_HI))
    hi.duty(0)
    lo = None
    if TWO_BUZZERS:
        lo = PWM(Pin(BUZZER_PIN_LO))
        lo.duty(0)

    melody = pick_melody()
    harmony = octave_shift(melody, HARMONY_SHIFT)

    try:
        if TWO_BUZZERS:
            print("Two-buzzer duet -- real harmony (melody + octave-{} bass)...".format(
                "down" if HARMONY_SHIFT < 0 else "up"))
            play_duet(hi, lo, melody, harmony)
        else:
            print("One-buzzer arpeggio -- fake chord (melody + its octave twin)...")
            play_duet_one_buzzer(hi, melody, harmony)
        print("Done.")
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        hi.duty(0)
        hi.deinit()
        if lo is not None:
            lo.duty(0)
            lo.deinit()


# ============================================================
# YOUR TURN
# ------------------------------------------------------------
# * Flip TWO_BUZZERS to True (wire a 2nd buzzer to GPIO 5) and hear the
#   difference between real harmony and the fake chord.
# * Change HARMONY_SHIFT to +1 for a bright, piccolo-style double instead
#   of a bass.
# * Advanced: instead of octave_shift(), write your OWN second voice -- a
#   real bass line -- as another list of (note, beats) the same length as
#   the melody, and pass it in place of `harmony`.
# ============================================================

main()
