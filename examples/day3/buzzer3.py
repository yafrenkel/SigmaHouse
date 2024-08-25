# -*- coding: utf-8 -*-
"""Stand-alone module playing parametrized melody with buzzer using hardware timer."""
from time import sleep_ms, ticks_diff, ticks_ms

from machine import PWM, Pin, Timer

# Tones
B0 = 31
C1 = 33
CS1 = 35
D1 = 37
DS1 = 39
E1 = 41
F1 = 44
FS1 = 46
G1 = 49
GS1 = 52
A1 = 55
AS1 = 58
B1 = 62
C2 = 65
CS2 = 69
D2 = 73
DS2 = 78
E2 = 82
F2 = 87
FS2 = 93
G2 = 98
GS2 = 104
A2 = 110
AS2 = 117
B2 = 123
C3 = 131
CS3 = 139
D3 = 147
DS3 = 156
E3 = 165
F3 = 175
FS3 = 185
G3 = 196
GS3 = 208
A3 = 220
AS3 = 233
B3 = 247
C4 = 262
CS4 = 277
D4 = 294
DS4 = 311
E4 = 330
F4 = 349
FS4 = 370
G4 = 392
GS4 = 415
A4 = 440
AS4 = 466
B4 = 494
C5 = 523
CS5 = 554
D5 = 587
DS5 = 622
E5 = 659
F5 = 698
FS5 = 740
G5 = 784
GS5 = 831
A5 = 880
AS5 = 932
B5 = 988
C6 = 1047
CS6 = 1109
D6 = 1175
DS6 = 1245
E6 = 1319
F6 = 1397
FS6 = 1480
G6 = 1568
GS6 = 1661
A6 = 1760
AS6 = 1865
B6 = 1976
C7 = 2093
CS7 = 2217
D7 = 2349
DS7 = 2489
E7 = 2637
F7 = 2794
FS7 = 2960
G7 = 3136
GS7 = 3322
A7 = 3520
AS7 = 3729
B7 = 3951
C8 = 4186
CS8 = 4435
D8 = 4699
DS8 = 4978


# fmt: off
melody_tones = [
    E7, E7, 0, E7, 0, C7, E7, 0,
    G7, 0, 0, 0, G6, 0, 0, 0,
    C7, 0, 0, G6, 0, 0, E6, 0,
    0, A6, 0, B6, 0, AS6, A6, 0,
    G6, E7, 0, G7, A7, 0, F7, G7,
    0, E7, 0, C7, D7, B6, 0, 0,
    C7, 0, 0, G6, 0, 0, E6, 0,
    0, A6, 0, B6, 0, AS6, A6, 0,
    G6, E7, 0, G7, A7, 0, F7, G7,
    0, E7, 0, C7, D7, B6, 0, 0,
]

melody_rhythm = [
    8, 8, 8, 8, 8, 8, 8, 8,
    8, 8, 8, 8, 8, 8, 8, 8,
    8, 8, 8, 8, 8, 8, 8, 8,
    8, 8, 8, 8, 8, 8, 8, 8,
    8, 8, 8, 8, 8, 8, 8, 8,
    8, 8, 8, 8, 8, 8, 8, 8,
    8, 8, 8, 8, 8, 8, 8, 8,
    8, 8, 8, 8, 8, 8, 8, 8,
    8, 8, 8, 8, 8, 8, 8, 8,
    8, 8, 8, 8, 8, 8, 8, 8,
]
# fmt: on

global_note_index = 0
global_tempo = 1200 #1200


def play_tone(buzzer, tone, active_duty=512):
    """Play single tone with buzzer."""
    if tone == 0:  # Special case for silence
        buzzer.duty(0)
        print("_", end="")
    else:
        buzzer.duty(active_duty)
        buzzer.freq(tone)
        print(".", end="")


def play_note_callback(timer):
    """Play current tone from melody and re-arm timer."""
    global global_note_index

    tone = melody_tones[global_note_index]
    duration = int(global_tempo / melody_rhythm[global_note_index])

    play_tone(global_buzzer, tone)

    global_note_index += 1
    if global_note_index == len(melody_tones):
        global_note_index = 0

    # schedule next note with timer
    timer.init(period=duration, mode=Timer.ONE_SHOT, callback=play_note_callback)


# initialize PWM on a pin
global_buzzer = PWM(Pin(4))
global_buzzer.freq(0)
global_buzzer.duty(512)

# initialize Timer
buzzer_timer = Timer(0)
buzzer_timer.init(period=1000, mode=Timer.ONE_SHOT, callback=play_note_callback)

time_start = ticks_ms()

try:
    while True:
        # calculate uptime in seconds
        uptime_sec = ticks_diff(ticks_ms(), time_start) // 1000

        print(f"\nUPTIME[{uptime_sec:0>4}s]: Main loop")

        # wait for 5s
        sleep_ms(5000)

except KeyboardInterrupt:
    print("Caught keyboard interrupt.")
    raise

finally:
    # Disable timer
    buzzer_timer.deinit()

    # Disable PWM on a pin
    global_buzzer.duty(0)
    global_buzzer.deinit()
