"""SEE the difference between sync and async -- no WiFi, no hub needed.

A heartbeat LED blinks steadily (5 times a second). Every 5 seconds a
"slow job" runs that takes 2 seconds (pretend it's waiting for a network
reply).

Watch the LED:

  USE_ASYNC = False  ->  the slow job BLOCKS the loop.
                         The heartbeat LED FREEZES for 2 seconds each time. ⏸
  USE_ASYNC = True   ->  the slow job is a task that yields with `await`.
                         The heartbeat keeps blinking SMOOTHLY the whole time. ✅

That frozen-vs-smooth blink is the whole lesson in one glance.

HOW TO USE
  1. Save this on the board (Thonny: Save as -> MicroPython device -> async_demo.py).
  2. Run it (F5). Watch the LED for ~15 seconds -- note the 2-second freezes.
  3. Change USE_ASYNC to True below, save, run again. The freezes are gone.

The ONLY real difference is how the slow job waits:
  - sync:  time.sleep(2)            -> blocks everything
  - async: await asyncio.sleep(2)   -> "I'm waiting, let others run"
"""

import time
from machine import Pin

# ----- flip this and re-run -----
USE_ASYNC = False
# --------------------------------

LED_PIN = 12        # the kit's LED. (Many ESP32 boards also have an onboard LED on pin 2.)
BEAT_MS = 200       # heartbeat: blink every 200 ms
JOB_EVERY_MS = 5000 # run the slow job every 5 s
JOB_LENGTH_MS = 2000  # the slow job takes 2 s

led = Pin(LED_PIN, Pin.OUT)


# ===================== SYNC version =====================

def run_sync():
    print("SYNC mode -- watch the LED freeze during each slow job.")
    on = False
    last_beat = time.ticks_ms()
    last_job = time.ticks_ms()
    beats = 0
    while True:
        # heartbeat
        if time.ticks_diff(time.ticks_ms(), last_beat) >= BEAT_MS:
            last_beat = time.ticks_ms()
            on = not on
            led.value(on)
            beats += 1
            print("beat", beats)

        # slow job -- BLOCKS the whole loop, so the heartbeat stops
        if time.ticks_diff(time.ticks_ms(), last_job) >= JOB_EVERY_MS:
            last_job = time.ticks_ms()
            print(">>> slow job START (blocking for 2 s -- LED will freeze)")
            time.sleep_ms(JOB_LENGTH_MS)        # <-- the villain
            print(">>> slow job DONE")

        time.sleep_ms(10)


# ===================== ASYNC version =====================

import uasyncio as asyncio


async def heartbeat():
    on = False
    beats = 0
    while True:
        on = not on
        led.value(on)
        beats += 1
        print("beat", beats)
        await asyncio.sleep_ms(BEAT_MS)


async def slow_job():
    while True:
        await asyncio.sleep_ms(JOB_EVERY_MS)
        print(">>> slow job START (waiting 2 s -- but heartbeat keeps going)")
        await asyncio.sleep_ms(JOB_LENGTH_MS)   # <-- yields, so others run
        print(">>> slow job DONE")


async def _amain():
    asyncio.create_task(heartbeat())
    asyncio.create_task(slow_job())
    while True:
        await asyncio.sleep(3600)


def run_async():
    print("ASYNC mode -- watch the LED keep a steady beat through every slow job.")
    asyncio.run(_amain())


# ===================== pick one =====================

if USE_ASYNC:
    run_async()
else:
    run_sync()

