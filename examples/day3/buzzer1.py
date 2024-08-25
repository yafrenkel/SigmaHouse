# -*- coding: utf-8 -*-
"""Stand-alone module playing hardcoded melody with buzzer."""
from time import sleep

from machine import PWM, Pin

# initialize PWM on a pin
buzzer_pin_pwm = PWM(Pin(4))
buzzer_pin_pwm.freq(0)
buzzer_pin_pwm.duty(1000)

# play happy birthday melody
buzzer_pin_pwm.freq(294)
sleep(0.25)
buzzer_pin_pwm.freq(440)
sleep(0.25)
buzzer_pin_pwm.freq(392)
sleep(0.25)
buzzer_pin_pwm.freq(532)
sleep(0.25)
buzzer_pin_pwm.freq(494)
sleep(0.25)
buzzer_pin_pwm.freq(392)
sleep(0.25)
buzzer_pin_pwm.freq(440)
sleep(0.25)
buzzer_pin_pwm.freq(392)
sleep(0.25)
buzzer_pin_pwm.freq(587)
sleep(0.25)
buzzer_pin_pwm.freq(532)
sleep(0.25)
buzzer_pin_pwm.freq(392)
sleep(0.25)
buzzer_pin_pwm.freq(784)
sleep(0.25)
buzzer_pin_pwm.freq(659)
sleep(0.25)
buzzer_pin_pwm.freq(532)
sleep(0.25)
buzzer_pin_pwm.freq(494)
sleep(0.25)
buzzer_pin_pwm.freq(440)
sleep(0.25)
buzzer_pin_pwm.freq(698)
sleep(0.25)
buzzer_pin_pwm.freq(659)
sleep(0.25)
buzzer_pin_pwm.freq(532)
sleep(0.25)
buzzer_pin_pwm.freq(587)
sleep(0.25)
buzzer_pin_pwm.freq(532)
sleep(0.5)

# Disable PWM on a pin
buzzer_pin_pwm.duty(0)
buzzer_pin_pwm.deinit()
