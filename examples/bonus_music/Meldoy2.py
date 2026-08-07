"""BONUS (ADVANCED) - a tiny music machine with knobs: TEMPO, RHYTHM, OCTAVE.

Same hardware as play_melody.py: just the buzzer on GPIO 4. No WiFi, no hub.
Do the basic play_melody.py first -- this one assumes you already know that
a note is a frequency and a song is a list of (note, length) pairs.

WHAT'S NEW HERE -- three things you can dial:

  1) TEMPO  (how FAST)   -- set in BPM, "beats per minute", like real sheet
                            music. 120 BPM = 120 quarter-notes a minute.
                            Bigger BPM = faster song. One knob: BPM.

  2) RHYTHM (how LONG each note is) -- instead of raw numbers we use real
                            note-length codes, so a song reads like music:
                              "w" whole   = 4 beats
                              "h" half    = 2 beats
                              "q" quarter = 1 beat
                              "e" eighth  = 1/2 beat
                              "s" 16th    = 1/4 beat
                            Add a dot for +50%:  "q." = 1.5 beats (a quarter
                            plus an eighth). That's exactly how a dotted note
                            works in real music.

  3) OCTAVE (how HIGH)   -- OCTAVE_SHIFT moves the WHOLE song up or down by
                            whole octaves without rewriting a single note.
                            +1 = one octave up (every frequency doubles),
                            -1 = one octave down (every frequency halves).

BONUS KNOB -- ARTICULATION (the "feel" of the rhythm): what fraction of each
  note actually SOUNDS before a tiny silence. 0.9 = smooth/connected (legato),
  0.4 = short and punchy (staccato). Same notes, very different groove.

HOW OCTAVES ARE COMPUTED (the doubling rule, in code)
  We store the 12 note frequencies for octave 4 only. To get another octave
  we just double (go up) or halve (go down). So C4=262 -> C5=524 -> C6=1048,
  and C3=131. That's the whole trick, and it's why OCTAVE_SHIFT is so easy.

HOW TO USE
  1. Save on the board (Thonny: Save as -> MicroPython device).
  2. Run it (F5). It plays the SAME tune four times so you can HEAR each
     knob change it: normal, then faster, then an octave up, then staccato.
  3. Scroll to YOUR TURN and make it your own.

Ctrl-C to stop.
"""
ROW_YOUR_BOAT = [
    ("C4", "q."), ("C4", "q."), ("C4", "q"), ("D4", "e"), ("E4", "q."),
    ("E4", "q"), ("D4", "e"), ("E4", "q"), ("F4", "e"), ("G4", "h."),
    ("C5", "e"), ("C5", "e"), ("C5", "e"), ("G4", "e"), ("G4", "e"), ("G4", "e"),
    ("E4", "e"), ("E4", "e"), ("E4", "e"), ("C4", "e"), ("C4", "e"), ("C4", "e"),
    ("G4", "q"), ("F4", "e"), ("E4", "q"), ("D4", "e"), ("C4", "h."),
]

import time
from machine import Pin, PWM

BUZZER_PIN = 4

# ============================================================
# THE KNOBS  (change these, re-run, listen)
# ============================================================
BPM          = 120     # tempo: quarter-notes per minute. Bigger = faster.
OCTAVE_SHIFT = 0       # +1 = whole song one octave up, -1 = one octave down.
ARTICULATION = 0.85    # 0.0..1.0  -> smooth (0.9) vs. short/punchy (0.4)

# --- The 12 semitones, frequencies for octave 4 only (Hz). ---
# Every other octave is derived by doubling/halving these.
BASE4 = {
    "C": 262, "C#": 277, "D": 294, "D#": 311, "E": 330, "F": 349,
    "F#": 370, "G": 392, "G#": 415, "A": 440, "A#": 466, "B": 494,
}

# --- Note-length codes -> how many beats. A dot ("q.") adds +50%. ---
DURATIONS = {"w": 4.0, "h": 2.0, "q": 1.0, "e": 0.5, "s": 0.25, "dq": 1.5, "de": 0.75, "dh": 3, "t": 0.25}


def note_freq(name, octave_shift):
    """Turn a note name like 'F#4' (or 'REST') into a frequency in Hz.

    Uses the doubling rule: start from the octave-4 frequency, then double
    for each octave up or halve for each octave down.
    """
    if name == "REST":
        return 0
    octave = int(name[-1])          # last char is the octave digit, e.g. 4
    letter = name[:-1]              # the rest is the note, e.g. "F#" or "A"
    freq = BASE4[letter]
    diff = (octave + octave_shift) - 4     # how many octaves away from 4
    if diff > 0:
        freq = freq * (2 ** diff)          # up an octave = x2 each step
    elif diff < 0:
        freq = freq / (2 ** (-diff))       # down an octave = /2 each step
    return int(round(freq))


def duration_beats(code):
    """Turn a rhythm code like 'q' or 'q.' into a number of beats."""
    dotted = code.endswith(".")
    base = DURATIONS[code[:-1] if dotted else code]
    return base * 1.5 if dotted else base


def play_note(buzzer, name, code, bpm, octave_shift, articulation):
    """Play ONE note: its pitch from OCTAVE, its length from TEMPO + RHYTHM."""
    beat_ms  = int(60000 / bpm)                       # length of one beat
    total_ms = int(duration_beats(code) * beat_ms)     # this note's full slot
    sound_ms = int(total_ms * articulation)            # part that actually buzzes
    gap_ms   = max(total_ms - sound_ms, 8)             # short silence after it

    freq = note_freq(name, octave_shift)
    if freq == 0:
        buzzer.duty(0)                 # REST: silent for the whole slot
        time.sleep_ms(total_ms)
        return

    buzzer.freq(freq)
    buzzer.duty(512)                   # ~50% -> audible
    time.sleep_ms(sound_ms)
    buzzer.duty(0)                     # cut the sound; the gap separates notes
    time.sleep_ms(gap_ms)


def play_song(buzzer, song, bpm=None, octave_shift=None, articulation=None):
    """Play a list of (note, rhythm-code). Any knob left None uses the global."""
    bpm          = BPM          if bpm is None else bpm
    octave_shift = OCTAVE_SHIFT if octave_shift is None else octave_shift
    articulation = ARTICULATION if articulation is None else articulation
    for name, code in song:
        print(name, end=" ")
        play_note(buzzer, name, code, bpm, octave_shift, articulation)
    print()


def play_scale(buzzer, octave_shift=None):
    """C-major scale as a song, so you can hear the pitch climb one octave."""
    scale = [(n + "4", "e") for n in ["C", "D", "E", "F", "G", "A", "B"]]
    scale.append(("C5", "q"))
    play_song(buzzer, scale, octave_shift=octave_shift)


# --- "Ode to Joy" written in real rhythm codes (q = quarter, q. = dotted...) ---
ODE_TO_JOY = [
    ("E4", "q"), ("E4", "q"), ("F4", "q"), ("G4", "q"),
    ("G4", "q"), ("F4", "q"), ("E4", "q"), ("D4", "q"),
    ("C4", "q"), ("C4", "q"), ("D4", "q"), ("E4", "q"),
    ("E4", "q."), ("D4", "e"), ("D4", "h"),
    ("E4", "q"), ("E4", "q"), ("F4", "q"), ("G4", "q"),
    ("G4", "q"), ("F4", "q"), ("E4", "q"), ("D4", "q"),
    ("C4", "q"), ("C4", "q"), ("D4", "q"), ("E4", "q"),
    ("D4", "q."), ("C4", "e"), ("C4", "h"),
]


B = [
    ("C3", "s"), ("E3", "s"), ("G3", "s"), ("C4", "s"), ("D3", "s"), ("F3", "s"), ("A3", "s"), ("D4", "s"),
    ("E3", "s"), ("G3", "s"), ("B3", "s"), ("E3", "s"), ("F3", "s"), ("A3", "s"), ("C4", "s"), ("F4", "s"), 
    ("G3", "s"), ("A3", "s"), ("B3", "s"), ("C3", "s"), ("B3", "s"), ("C4", "s"), ("D4", "s"), ("E4", "s"),
    ("D4", "s"), ("E4", "s"), ("F4", "s"), ("G4", "s"), ("F4", "s"), ("G4", "s"), ("A4", "s"), ("B4", "s"), 
    ("C5", "e"), ("G4", "e"), ("C5", "e"), ("G4", "e"),
    ("C5", "e"), ("B4", "e"), ("C5", "e"), ("D5", "e"),
    ("E5", "e"), ("G4", "e"), ("D5", "e"), ("B4", "e"),
    ("C5", "q."), ("REST", "e"),
    ("E5", "e"), ("C5", "e"), ("E5", "e"), ("C5", "e"),
    ("E5", "e"), ("D5", "e"), ("E5", "e"), ("F5", "s."), ("C5", "t"),
    ("E5", "q"), ("F5", "q"),
    ("G5", "e"), ("REST", "t"), ("G#5", "t"), ("A5", "t"), ("A#5", "t"), ("B5", "e."), ("REST", "s"),
    ("C5", "e"), ("G4", "e"), ("C5", "e"), ("G4", "e"),
    ("C5", "e"), ("B4", "e"), ("C5", "e"), ("D5", "e"),
    ("E5", "e"), ("G4", "e"), ("F5", "e"), ("G#5", "e"),
    ("A5", "e"), ("A4", "e"), ("A5", "e"), ("G5", "e"),
    ("F5", "e"), ("B4", "e"), ("F5", "e"), ("E5", "e"),
    ("D5", "e"), ("G4", "e"), ("E5", "e"), ("D5", "e"),
    ("C5", "q"), ("C4", "s"), ("D5", "t"), ("E5", "t"), ("F5", "t"), ("G5", "t"), ("A5", "t"), ("B5", "t"), ("C6", "q")
    
]


def main():
    buzzer = PWM(Pin(BUZZER_PIN))
    buzzer.duty(0)
    try:
        print("Scale (hear the pitch climb one octave)...")
        #play_scale(buzzer)
        time.sleep(1)

        # The SAME song four times -- each time one knob is different, so you
        # can hear exactly what that knob does.
#         print("Ode to Joy -- normal ({} BPM)...".format(BPM))
#         play_song(buzzer, ODE_TO_JOY)
#         time.sleep(1)

#         print("Same song, faster (TEMPO 200 BPM)...")
#         play_song(buzzer, ODE_TO_JOY, bpm=200)
#         time.sleep(1)

#         print("Same song, one OCTAVE up (+1)...")
#         play_song(buzzer, ODE_TO_JOY, octave_shift=1)
#         time.sleep(1)

#         print("Same song, staccato (ARTICULATION 0.4 -> short & punchy)...")
#         play_song(buzzer, ODE_TO_JOY, articulation=0.4)


   
        play_song(buzzer, B, articulation=0.8)
        #play_song(buzzer, ROW_YOUR_BOAT, articulation=0.4)



    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        buzzer.duty(0)                 # always leave the buzzer quiet
        buzzer.deinit()


# ============================================================
# YOUR TURN
# ------------------------------------------------------------
# 1) TEMPO: change BPM at the top (try 80 for slow, 220 for fast),
#    re-run, and hear the whole feel change.
#
# 2) OCTAVE: set OCTAVE_SHIFT = 1 (chipmunk) or -1 (deep) at the top.
#    Notice you did NOT edit a single note -- that's the doubling rule.
#
# 3) RHYTHM: write your own tune using the length codes. Example -- the
#    first line of "Twinkle Twinkle" (all quarters, ends on a half):
#
#      TWINKLE = [
#          ("C4","q"), ("C4","q"), ("G4","q"), ("G4","q"),
#          ("A4","q"), ("A4","q"), ("G4","h"),
#          ("F4","q"), ("F4","q"), ("E4","q"), ("E4","q"),
#          ("D4","q"), ("D4","q"), ("C4","h"),
#      ]
#
#    Then in main(), call:  play_song(buzzer, TWINKLE)
#    Add ("REST","q") for a pause. Use "e"/"s" for quick notes,
#    "q."/"h." for long dotted ones, and "#" for sharps (e.g. "F#4").
#
# STRETCH: make a "swing" feel -- play with different ARTICULATION values
#    for on-beat vs off-beat notes, or write a play_song that alternates a
#    long eighth and a short eighth. Real jazz rhythm, from one buzzer.
# ============================================================

main()

