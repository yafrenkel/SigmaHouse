# -*- coding: utf-8 -*-
"""Stand-alone module playing parametrized melody with buzzer using timers."""
from time import sleep_ms, ticks_diff, ticks_ms

from machine import PWM, Pin, Timer


class Buzzer:
    """Implements Buzzer class."""

    def __init__(self, pin_num, timer_num):
        """Initiate object's internal state."""
        self._state = {
            "active": False,
            "timestamp": 0,
        }

        # fmt: off
        self._melody = {
            "tempo": 1200,
            "note_index": 0,
            "tones": [
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
            ],
            "rhythm": [
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
            ],
        }
        # fmt: on

        print(f"Initiating on pin {pin_num}")
        self._buzzer = PWM(Pin(pin_num))
        self._buzzer.freq(0)
        self._buzzer.duty(512)

        print("Registering Timer")
        self._timer = Timer(timer_num)
        self._timer.deinit()

    def _start_tone(self, tone, active_duty=512):
        """Start playing single tone with buzzer."""
        if tone == 0:
            self._buzzer.duty(0)
        else:
            self._buzzer.duty(active_duty)
            self._buzzer.freq(tone)

    def _play_note_callback(self, timer):
        """Play current note from melody and re-arm timer for next note."""
        tempo = self._melody["tempo"]
        note_index = self._melody["note_index"]
        tone = self._melody["tones"][note_index]
        divider = self._melody["rhythm"][note_index]
        duration = int(tempo / divider)

        self._start_tone(tone)

        self._melody["note_index"] += 1
        if self._melody["note_index"] == len(self._melody["tones"]):
            self._melody["note_index"] = 0

        timer.init(
            period=duration, mode=Timer.ONE_SHOT, callback=self._play_note_callback
        )

    def start_melody(self, start_delay=100):
        """Start playing melody."""
        self._state.update(
            {
                "active": True,
                "timestamp": ticks_ms(),
            }
        )

        self._timer.init(
            period=start_delay, mode=Timer.ONE_SHOT, callback=self._play_note_callback
        )

    def stop_melody(self):
        """Stop playing melody."""
        self._state.update(
            {
                "active": False,
                "timestamp": ticks_ms(),
            }
        )

        self.finalize()

    def finalize(self):
        """Disable PWM and timer hardware."""
        print("Disabling PWM")
        self._buzzer.duty(0)
        self._buzzer.deinit()

        print("Disabling timer")
        self._timer.deinit()


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

buzzer = Buzzer(4, -1)
buzzer.start_melody()

play_cycles = 3
time_start = ticks_ms()
try:
    while True:
        # calculate uptime in seconds
        uptime_sec = ticks_diff(ticks_ms(), time_start) // 1000

        print(f"UPTIME[{uptime_sec:0>4}s]: Main loop")

        # wait for 5s
        sleep_ms(5000)

        play_cycles -= 1
        if play_cycles == 0:
            buzzer.stop_melody()

except KeyboardInterrupt:
    print("Caught keyboard interrupt.")
    raise

finally:
    buzzer.stop_melody()
    buzzer.finalize()
