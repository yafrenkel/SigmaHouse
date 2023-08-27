# -*- coding: utf-8 -*-
"""Provides Fan device class."""

from time import ticks_ms

from devices.device import Device

from machine import PWM, Pin


class Fan(Device):
    """Implements Fan class."""

    def __init__(
        self,
        name="/dev/fan",
        pin_a_num=0,
        pin_b_num=0,
        pwm_freq=1000,
        event_queue=None,
        debug=False,
    ):
        """Initiate object's internal state."""
        super().__init__(name=name, event_queue=event_queue, debug=debug)

        self._state = {
            "active": False,
            "clockwise": True,
            "timestamp": 0,
        }

        self._log(f"Initiating PWM on pins {pin_a_num} and {pin_b_num}")
        self._pin_a_pwm = PWM(Pin(pin_a_num, Pin.OUT, value=0))
        self._pin_a_pwm.duty(0)
        self._pin_a_pwm.freq(pwm_freq)

        self._pin_b_pwm = PWM(Pin(pin_b_num, Pin.OUT, value=0))
        self._pin_b_pwm.duty(0)
        self._pin_b_pwm.freq(pwm_freq)

    def _set_fan(self):
        """Synchronize fan state with real world and message event queue."""
        self._state["timestamp"] = ticks_ms()

        if self._state["active"] and self._state["clockwise"]:
            self._pin_a_pwm.duty(512)
            self._pin_b_pwm.duty(0)
        elif self._state["active"] and not self._state["clockwise"]:
            self._pin_a_pwm.duty(0)
            self._pin_b_pwm.duty(512)
        elif not self._state["active"]:
            self._pin_a_pwm.duty(0)
            self._pin_b_pwm.duty(0)

        self._push_event_state()

    def turn_on(self, clockwise):
        """Start fan in specific direction."""
        if not self._state["active"]:
            self._state["active"] = True
            self._state["clockwise"] = clockwise
            self._set_fan()

    def turn_off(self):
        """Turn fan off."""
        if self._state["active"]:
            self._state["active"] = False
            self._set_fan()

    def finalize(self):
        """Disable PWM."""
        self._log("Disabling PWM")
        self._pin_a_pwm.duty(0)
        self._pin_b_pwm.duty(0)
        self._pin_a_pwm.deinit()
        self._pin_b_pwm.deinit()
