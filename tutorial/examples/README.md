# Examples

Runnable code that goes with the tutorial — one folder per day. Open a file
in Thonny and run it on the board (or run the hub for Day 1).

| Day | Folder | What it shows |
|---|---|---|
| 1 | *(none)* | The example is the running hub itself — see [day1](../day1.md) (Flask + `curl`/browser). |
| 2 | [day2_esp32_basics/](day2_esp32_basics/) | Blink an LED, read a button (polling vs interrupt), button toggles LED |
| 3 | [day3_wifi_hub/](day3_wifi_hub/) | `simple_led.py` — the whole "smart house" in one small file (WiFi + hub + LED) |
| 4 | [day4_sensors/](day4_sensors/) | `motion_test.py` — read the PIR sensor on its own |
| 5 | [day5_async/](day5_async/) | `async_demo.py` — *see* the difference between sync and async |

## Day 2 — run these in order
1. `1_blink.py` — blink the LED
2. `2_button_poll.py` — read a button by asking repeatedly (polling)
3. `3_button_irq.py` — read a button with an interrupt (one press = one event)
4. `4_button_led.py` — press the button to toggle the LED (the flag pattern the real firmware uses)

No WiFi or hub needed for Day 2 — just the board.

## Day 3+ — the networked example
`day3_wifi_hub/simple_led.py` needs the **hub running** and your details filled
into the `EDIT THESE` block at the top (WiFi name/password, and `HUB_URL` =
your laptop's IP + `:8080`). It's the same idea as `secrets.py` in the full
firmware, just inline so the file stands alone.

## How these relate to the full firmware
These examples are teaching scaffolds. The real project
(`implementation/smart_house/`) combines all of them: the button/IRQ pattern
from Day 2, the WiFi + hub calls from Day 3's `simple_led.py`, the PIR from
Day 4, and the sync/async choice from Day 5 — for six devices at once.
