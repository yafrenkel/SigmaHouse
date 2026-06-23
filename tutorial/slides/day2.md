---
marp: true
theme: default
paginate: true
size: 16:9
---

<!-- _class: lead -->

# Day 2
## ESP32 First Steps

The Python you know, on a tiny computer.

---

## What you'll have at lunch

- An ESP32 you can program from Thonny
- A blinking LED running on the board, no laptop required
- A button that toggles the LED

**No WiFi today.** Just the board.

---

## The big idea today

The same `print("hello")` you've written runs the same way on a $5 chip.

But this chip has **pins** — physical wires you control with code.

```python
from machine import Pin
led = Pin(12, Pin.OUT)
led.value(1)    # 3.3V on the wire → LED lights up
```

---

## Vocabulary

| Word | Meaning |
|---|---|
| **MicroPython** | Python for microcontrollers (mostly the same) |
| **GPIO** | "General-Purpose Input/Output" — a pin you control |
| **Pin.OUT** | We control the pin's voltage |
| **Pin.IN** | We read the pin's voltage |
| **PULL_UP** | Default to 1 when nothing's pressing |
| **IRQ** | "Hey CPU, this pin just changed!" |

---

## Today's milestones

- ✅ **2.1** REPL talks to the board
- ✅ **2.2** LED blinks running `blink.py` from the board
- ✅ **2.3** ONE message per button press (interrupt-based)
- ✅ **2.4** Button toggles LED

---

## Polling vs. Interrupts

**Polling** — keep asking "are you pressed?" 100×/sec.

**Interrupt** — the hardware tells you when it changes.

```python
def on_press(pin):
    led.value(not led.value())

button.irq(trigger=Pin.IRQ_FALLING, handler=on_press)
```

---

## ⚠️ The one rule of interrupts

**Interrupt handlers must be FAST.**

| Inside an IRQ | OK? |
|---|:---:|
| Set a variable | ✅ |
| Toggle a pin | ✅ |
| `print()` | ❌ |
| `time.sleep()` | ❌ |
| Send HTTP | ❌❌❌ |

---

<!-- _class: lead -->

# Open `tutorial/day2.md`
# Plug in your ESP32.
