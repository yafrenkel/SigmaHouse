"""Friendly facade over the I2C 1602 LCD.

The actual driver lives in lcd_api.py + lcd_i2c.py (vendor code).
This wrapper hides the I2C boilerplate so the rest of the firmware
just calls lcd.show("hello", "world").
"""

from machine import I2C, Pin

from lcd_i2c import I2cLcd


class LCD:
    def __init__(self, scl_pin, sda_pin, addr, rows, cols):
        i2c = I2C(0, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=400000)
        self._lcd = I2cLcd(i2c, addr, rows, cols)
        self._cols = cols

    def show(self, line1, line2=""):
        """Replace the screen with up to two lines of text."""
        self._lcd.clear()
        self._lcd.move_to(0, 0)
        self._lcd.putstr(line1[: self._cols])
        if line2:
            self._lcd.move_to(0, 1)
            self._lcd.putstr(line2[: self._cols])
