"""Plain LED on a digital output pin."""

from machine import Pin


class LED:
    def __init__(self, pin_num):
        self._pin = Pin(pin_num, Pin.OUT)
        self._pin.value(0)

    def on(self):
        self._pin.value(1)

    def off(self):
        self._pin.value(0)

    def is_on(self):
        return self._pin.value() == 1

    def state(self):
        return {"active": self.is_on()}
