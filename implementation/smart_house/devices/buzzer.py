"""Piezo buzzer driven by PWM.

We use a single fixed tone (2 kHz) for the alarm. Simple is good --
no melodies, no timers, easy to read.
"""

import time
from machine import Pin, PWM

TONE_HZ = 2000
DUTY    = 512  # 50% -> loudest


class Buzzer:
    def __init__(self, pin_num):
        self._pwm = PWM(Pin(pin_num))
        self._pwm.freq(TONE_HZ)
        self._pwm.duty(0)
        self._on = False

    def on(self):
        self._on = True
        self._pwm.duty(DUTY)

    def off(self):
        self._on = False
        self._pwm.duty(0)

    def beep(self, ms=200):
        """Short blocking beep -- handy for button feedback."""
        self.on()
        time.sleep_ms(ms)
        self.off()

    def is_on(self):
        return self._on

    def state(self):
        return {"active": self._on}
