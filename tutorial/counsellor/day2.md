# Counsellor's Guide — Day 2: ESP32 First Steps

**Lab time:** ~2 hours. **Hands-on:** ~110 min.

This is the most physically chaotic day. Boards being plugged/unplugged, USB ports going wonky, drivers misbehaving. Have spare cables ready.

## Pacing

| Min | Activity | Watch out for |
|---:|---|---|
| 0–10 | Opener + Thonny demo | "Where do I plug the cable?" — show once |
| 10–25 | Thonny setup, find the COM port | Driver issues. Charging-only USB cables. |
| 25–45 | Blink LED at REPL → blink.py | Forgetting to save TO BOARD; forgetting to F5 |
| 45–70 | Button polling vs IRQ | Bouncing buttons; multiple "Pressed!" prints |
| 70–100 | Button toggles LED | Doing slow work in the IRQ |
| 100–115 | Read project's `led.py` and `button.py` | Quiet stretch — circulate |
| 115–120 | Demo + stretch supervision | — |

## Where they'll get stuck

1. **No COM port shown in Thonny** — most common cause: the cable is charge-only. Symptom: laptop doesn't beep on plug-in. Hint: try a different cable. Second cause: missing CP210x or CH340 driver. Have the installer on a USB stick.

2. **"Cannot connect to MicroPython"** — Thonny is trying the wrong port, or another program (like `mpremote`) is holding it. Tools → Options → Interpreter → re-pick the port.

3. **`from machine import Pin` fails** — they're running PyCharm's Python interpreter, not Thonny's. `machine` doesn't exist on the laptop. Make sure their code runs from Thonny, not PyCharm.

4. **F5 does nothing** — they're focused in the editor not the shell. Click into the shell, then F5. Or use the green "Run" button.

5. **Files saved to PC, not board** — Thonny defaults to "save to PC". The fix: **Save as…** → pick **MicroPython device**. After that, "Save" remembers. If they save to PC, the board can't see it.

6. **`main.py` accidentally created on the board** — they saved their experiment as `main.py` and now the board auto-runs it on every reset and they can't get to the REPL. **Fix:** in Thonny shell hit Ctrl-C to break, then `import os; os.remove("main.py")`. Or just rename their experiment to anything else (`test.py`).

7. **IRQ handler crashes the board** — they put `print()` or `time.sleep()` in the handler. Symptom: random crashes/freezes when pressing the button. Hint: "An IRQ runs on the hardware's clock — it must finish in microseconds. No prints, no sleeps."

8. **Button reads `1` always or `0` always** — wrong pin number, or forgot `Pin.PULL_UP`. Hint: "Button A is GPIO 26; check `config.py`. And use `Pin(26, Pin.IN, Pin.PULL_UP)`."

## Ready-to-paste hints

**Hint H1** — Blink works once but loop hangs:
> Are you running it WITHOUT the `while True:` loop? Check indentation. If your `time.sleep` and `led.value` aren't indented under the `while`, they only run once.

**Hint H2** — Multiple "Pressed!" messages:
> That's *bouncing* — real metal contacts vibrate. Switch to interrupts (Pin.irq) — the IRQ_FALLING trigger fires once per press.

**Hint H3** — IRQ-based code crashes the board:
> Show me your IRQ handler. If it has `print` or `time.sleep`, that's the bug. The handler should JUST set a flag (`self._pressed = True`). The main loop reads the flag.

**Hint H4** — They want to debounce in software:
> Track the last press timestamp. Ignore presses that come within 50 ms of the previous. Pseudocode:
> ```python
> from time import ticks_ms, ticks_diff
> last = 0
> def on_press(pin):
>     global last
>     now = ticks_ms()
>     if ticks_diff(now, last) > 50:
>         pressed_flag = True
>     last = now
> ```

**Hint H5** — They can't get back to REPL because main.py runs on boot:
> In the shell, press Ctrl-C twice quickly. That breaks the running script. Then you can `import os; os.remove("main.py")`.

## What "done" looks like

- **Milestone 2.1** — Their REPL shows MicroPython banner, `os.uname()` returns ESP32 info.
- **Milestone 2.2** — LED blinks 1×/sec running `blink.py` from the board (not from PC).
- **Milestone 2.3** — Pressing button A produces ONE "Button pressed!" message (allowing for occasional bounce).
- **Milestone 2.4** — Press → LED toggles state (on→off or off→on, persists between presses).

## Stretch supervision

- **SOS Morse blink** — fun, no hardware risk. Encourage.
- **Auto-off LED** — needs `time.ticks_ms()` understanding. Worth helping with: the same pattern is used in `app_sync.py` for the keepalive interval.
- **Software debouncing** — only point them here if they finished everything else AND understand IRQs well. Otherwise it's frustrating.

## Hardware care reminders

- **Don't plug/unplug the board while it's running with peripherals on.** It can momentarily short. Always Ctrl-C the shell first.
- **The fan motor draws spikes.** If their board resets when they spin the fan, they may have a weak USB port. Move them to a different port or plug into the wall via a powered hub.
- **Static electricity.** If the room is dry, touch the metal of the laptop chassis before handling the board. (Mostly cosmetic concern; modern boards are robust.)

## What you should hear from a good group

- "Why doesn't my button work?" → "Check the pin number." → "OH I had 25 not 26."
- "Should I use polling or interrupts?" → Right question.
- "Can I make it blink the LCD?" → They've finished early; pair them with a struggling team to teach.
