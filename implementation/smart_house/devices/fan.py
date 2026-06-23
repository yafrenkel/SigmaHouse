"""Fan driven by a 2-pin H-bridge.

Two PWM outputs control the motor:
  - PWM A high, B low  -> spin one way (clockwise)
  - PWM A low,  B high -> spin the other way (counter-clockwise)
  - Both low           -> stopped

We always use 50% duty (512/1023) -- enough torque, won't overheat.
"""

from machine import Pin, PWM

PWM_FREQ = 1000
PWM_DUTY = 512  # half power


class Fan:
    def __init__(self, pin_a, pin_b):
        self._a = PWM(Pin(pin_a))
        self._b = PWM(Pin(pin_b))
        self._a.freq(PWM_FREQ)
        self._b.freq(PWM_FREQ)
        self._on = False
        self._clockwise = True
        self.off()

    def on(self, clockwise=True):
        self._on = True
        self._clockwise = clockwise
        if clockwise:
            self._a.duty(PWM_DUTY)
            self._b.duty(0)
        else:
            self._a.duty(0)
            self._b.duty(PWM_DUTY)

    def off(self):
        self._on = False
        self._a.duty(0)
        self._b.duty(0)

    def is_on(self):
        return self._on

    def state(self):
        return {"active": self._on, "clockwise": self._clockwise}
