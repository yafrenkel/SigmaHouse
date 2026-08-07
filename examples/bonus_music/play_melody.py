"""BONUS - make the buzzer play a melody (a little music theory).

No WiFi, no hub -- just the buzzer on GPIO 4.

MUSIC THEORY IN 30 SECONDS
  * A musical note is just a frequency -- how fast the buzzer vibrates,
    measured in hertz (Hz).
  * Higher frequency = higher pitch. Middle A ("A4") is 440 Hz.
  * Going UP one octave DOUBLES the frequency:  A4 = 440,  A5 = 880.
  * The 12 notes in an octave (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
    are evenly spaced -- each is about 1.06x the one below it.
  * A song is just a list of (note, how-long) pairs played in order.
  * A frequency of 0 means REST -- silence for that beat.

HOW THE BUZZER MAKES A NOTE
  We use PWM (Pulse-Width Modulation). Setting the PWM *frequency* to a
  note's Hz makes the buzzer buzz at that pitch. duty(512) = ~50% volume.

HOW TO USE
  1. Upload BOTH play_melody.py AND melodies_options.py to the board
     (Thonny: select both -> right-click -> Upload to /).
  2. Run it (F5). You'll hear a scale, then "Ode to Joy", then a menu of
     16 more tunes prints in the shell.
  3. Set CHOICE (near the top) to a number 1..16 to pick one, 0 for all,
     or None to be asked each time. Re-run to hear your pick.
  4. Scroll to YOUR TURN at the bottom and write your own tune!

Ctrl-C to stop.
"""

import time
from machine import Pin, PWM

# The 16 bonus melodies live in melodies_options.py.
# Upload BOTH files to the board, or the menu just won't appear.
try:
    from melodies_options import MELODIES
except ImportError:
    MELODIES = []

BUZZER_PIN = 4
TEMPO_MS   = 400     # length of one beat in milliseconds. Smaller = faster song.

# Which bonus melody to play after the demo:
#   a number 1..16 from the menu that prints when you run this,
#   0 to play ALL of them, or None to be asked in the shell each time.
CHOICE = 1

# --- Notes and their frequencies (Hz). Two octaves is plenty for simple tunes. ---
# Notice C5 (523) is roughly double C4 (262) -- that's the "one octave up" rule.
NOTES = {
    "C4": 262, "CS4": 277, "D4": 294, "DS4": 311, "E4": 330, "F4": 349,
    "FS4": 370, "G4": 392, "GS4": 415, "A4": 440, "AS4": 466, "B4": 494,
    "C5": 523, "CS5": 554, "D5": 587, "DS5": 622, "E5": 659, "F5": 698,
    "FS5": 740, "G5": 784, "GS5": 831, "A5": 880, "AS5": 932, "B5": 988,
    "C6": 1047,
    "REST": 0,        # silence
}

# --- A melody is a list of (note, beats). "Ode to Joy" (Beethoven) ---
# It uses only the plain notes (no sharps) -- nice and simple to read.
ODE_TO_JOY = [
    ("E4", 1), ("E4", 1), ("F4", 1), ("G4", 1),
    ("G4", 1), ("F4", 1), ("E4", 1), ("D4", 1),
    ("C4", 1), ("C4", 1), ("D4", 1), ("E4", 1),
    ("E4", 1.5), ("D4", 0.5), ("D4", 2),
    ("E4", 1), ("E4", 1), ("F4", 1), ("G4", 1),
    ("G4", 1), ("F4", 1), ("E4", 1), ("D4", 1),
    ("C4", 1), ("C4", 1), ("D4", 1), ("E4", 1),
    ("D4", 1.5), ("C4", 0.5), ("C4", 2),
]


def play_note(buzzer, note, beats):
    """Play one note for a number of beats (0 = rest/silence)."""
    freq = NOTES[note]
    if freq == 0:
        buzzer.duty(0)                 # rest -- stay silent
    else:
        buzzer.freq(freq)
        buzzer.duty(512)               # ~50% -> audible
    time.sleep_ms(int(beats * TEMPO_MS))
    buzzer.duty(0)                     # tiny gap so repeated notes don't blur
    time.sleep_ms(20)


def play_melody(buzzer, melody):
    """Play a whole list of (note, beats)."""
    for note, beats in melody:
        print(note, end=" ")
        play_note(buzzer, note, beats)
    print()


def play_scale(buzzer):
    """Play the C-major scale so you can HEAR the pitch climb, one octave up."""
    for note in ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]:
        play_note(buzzer, note, 0.6)


def list_melodies():
    """Print the numbered menu of bonus melodies from melodies_options.py."""
    print("Bonus melodies (set CHOICE at the top of this file):")
    for i, (title, _) in enumerate(MELODIES, 1):
        print("  {:2d}. {}".format(i, title))


def play_choice(buzzer, choice):
    """Play one bonus melody by its menu number (0 = play them all)."""
    if not MELODIES:
        print("(melodies_options.py isn't on the board -- upload it to unlock the menu.)")
        return
    if choice == 0:
        for title, melody in MELODIES:
            print("Playing:", title)
            play_melody(buzzer, melody)
            time.sleep_ms(400)
        return
    if choice < 1 or choice > len(MELODIES):
        print("No melody #{} -- pick 1..{}.".format(choice, len(MELODIES)))
        return
    title, melody = MELODIES[choice - 1]
    print("Playing:", title)
    play_melody(buzzer, melody)


def main():
    buzzer = PWM(Pin(BUZZER_PIN))
    buzzer.duty(0)
    try:
        print("Scale (listen to the pitch rise)...")
        play_scale(buzzer)
        time.sleep(1)
        print("Ode to Joy...")
        play_melody(buzzer, ODE_TO_JOY)
        time.sleep(1)
        if MELODIES:
            list_melodies()
            choice = CHOICE
            if choice is None:
                try:
                    choice = int(input("Pick a melody number (0 = all): "))
                except (ValueError, EOFError):
                    choice = 1     # default if nothing / junk was typed
            play_choice(buzzer, choice)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        buzzer.duty(0)                 # always leave the buzzer quiet
        buzzer.deinit()


# ============================================================
# YOUR TURN
# ------------------------------------------------------------
# Write your own tune! Make a list of (note, beats) using the
# note names in NOTES above, then play it. Example -- the first
# line of "Twinkle Twinkle Little Star":
#
#   TWINKLE = [
#       ("C4",1), ("C4",1), ("G4",1), ("G4",1),
#       ("A4",1), ("A4",1), ("G4",2),
#       ("F4",1), ("F4",1), ("E4",1), ("E4",1),
#       ("D4",1), ("D4",1), ("C4",2),
#   ]
#
# Then in main(), call:  play_melody(buzzer, TWINKLE)
#
# Ideas: change TEMPO_MS to speed up/slow down. Add REST for pauses.
# Try higher notes (C5, E5...) for a brighter sound.
# ============================================================

main()
