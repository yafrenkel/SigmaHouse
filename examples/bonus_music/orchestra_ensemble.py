"""BONUS - an orchestra of houses: 2, 3, 4 (or more!) boards play together.

Each board plays ONE voice; together they harmonise. Runs on just the buzzer
(GPIO 4) + button A (GPIO 26) -- no hub, no WiFi.

SET UP (on EVERY board):
  1. Upload THIS file and melodies_options.py to each board.
  2. Pick the SAME song, arrangement, tempo, and ROUND_DELAY on all boards.
  3. Give each board a different VOICE number: 1, 2, 3, 4, ...
  4. Run it on every board -- each prints which voice it is.

PLAY:
  Everyone holds button A; someone counts "3-2-1-GO" and you all press
  together. Each board plays its voice; together it's an ensemble.

TWO ARRANGEMENTS (both built automatically from ONE melody):
  * "round"  -> a canon: voice 2 starts ROUND_DELAY beats after voice 1, voice
                3 after voice 2, and so on. Scales to ANY number of boards, and
                it hardly matters if your starts aren't perfectly together.
                Frere Jacques is a classic FOUR-part round -- perfect for 4
                boards. Row Row Row Your Boat is a great round too.
  * "octave" -> each voice plays a different octave (voice 1 = melody,
                2 = one lower, 3 = one higher, 4 = two lower). Best with 2-3
                boards. Any tune works; try Ode to Joy or Twinkle.

  --> For 3 or 4 boards, use "round". It's the easy, great-sounding path.

TIGHTER SYNC (optional stretch): for "octave" you may hear a slight echo if the
starts aren't together. Wire the boards -- join a GND pin on each, and run an
OUTPUT pin on the "conductor" board to an INPUT pin on the others; the conductor
raises it to say "GO". Ask a counsellor.

Ctrl-C to stop.
"""

import time
from machine import Pin, PWM
import melodies_options as songs

# ===== set these the SAME on EVERY board =====
SONG        = songs.FRERE_JACQUES   # any melody from melodies_options.py
ARRANGEMENT = "round"               # "round" (any number of boards) or "octave"
ROUND_DELAY = 8                     # beats between each voice's entry (round)
TEMPO_MS    = 400                   # length of one beat, in milliseconds

# ===== set this DIFFERENTLY on each board =====
VOICE = 1                           # this board's part: 1, 2, 3, 4, ...

BUZZER_PIN = 4
BUTTON_PIN = 26                     # button A on the Keyestudio kit

# In "octave" mode, which octave each voice plays (0 = melody as written).
# Voices past this table just play the melody (shift 0).
OCTAVE_BY_VOICE = {1: 0, 2: -1, 3: 1, 4: -2}

# Notes and frequencies (Hz). Octaves 2-6 so voices can spread up and down.
NOTES = {
    "C2": 65,  "CS2": 69,  "D2": 73,  "DS2": 78,  "E2": 82,  "F2": 87,
    "FS2": 93,  "G2": 98,  "GS2": 104, "A2": 110, "AS2": 117, "B2": 123,
    "C3": 131, "CS3": 139, "D3": 147, "DS3": 156, "E3": 165, "F3": 175,
    "FS3": 185, "G3": 196, "GS3": 208, "A3": 220, "AS3": 233, "B3": 247,
    "C4": 262, "CS4": 277, "D4": 294, "DS4": 311, "E4": 330, "F4": 349,
    "FS4": 370, "G4": 392, "GS4": 415, "A4": 440, "AS4": 466, "B4": 494,
    "C5": 523, "CS5": 554, "D5": 587, "DS5": 622, "E5": 659, "F5": 698,
    "FS5": 740, "G5": 784, "GS5": 831, "A5": 880, "AS5": 932, "B5": 988,
    "C6": 1047,
    "REST": 0,
}


def octave_shift(melody, delta):
    """A copy of a melody moved by `delta` octaves (leaves RESTs alone;
    keeps a note unchanged if the shifted one is off our range)."""
    out = []
    for note, beats in melody:
        if note == "REST":
            out.append((note, beats))
            continue
        base, octave = note[:-1], int(note[-1])
        shifted = base + str(octave + delta)
        out.append(((shifted if shifted in NOTES else note), beats))
    return out


def my_part():
    """Work out THIS board's voice from the shared song + its VOICE number."""
    if ARRANGEMENT == "round":
        # voice 1 leads; each later voice waits (VOICE-1) x ROUND_DELAY beats
        delay = (VOICE - 1) * ROUND_DELAY
        return [("REST", delay)] + SONG
    # "octave": spread the voices across octaves
    return octave_shift(SONG, OCTAVE_BY_VOICE.get(VOICE, 0))


def play_note(buzzer, note, beats):
    freq = NOTES[note]
    if freq == 0:
        buzzer.duty(0)                              # REST = silence
    else:
        buzzer.freq(freq)
        buzzer.duty(512)                            # ~50% -> audible
    time.sleep_ms(int(beats * TEMPO_MS))
    buzzer.duty(0)
    time.sleep_ms(20)                               # tiny gap between notes


def play_melody(buzzer, melody):
    for note, beats in melody:
        play_note(buzzer, note, beats)


def main():
    buzzer = PWM(Pin(BUZZER_PIN))
    buzzer.duty(0)
    button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)   # pressed reads 0
    part = my_part()
    print("I am VOICE", VOICE, "(", ARRANGEMENT, "). Hold button A; press on 'GO'!")
    try:
        while True:
            while button.value() == 1:              # wait for a press
                time.sleep_ms(20)
            print("Playing voice", VOICE, "...")
            play_melody(buzzer, part)
            buzzer.duty(0)
            print("Done -- press again to replay.")
            while button.value() == 0:              # wait for release
                time.sleep_ms(20)
            time.sleep_ms(150)
    except KeyboardInterrupt:
        pass
    finally:
        buzzer.duty(0)
        buzzer.deinit()


main()
