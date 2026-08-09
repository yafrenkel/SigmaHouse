"""BONUS - the RFID lock, done the ASYNC way (day-5 showcase).

This is the elegant version: the lock watches for cards WHILE a heartbeat
LED keeps blinking and (optionally) the hub gets updated -- all at once,
none of them freezing the others. That "many things at once, nothing
blocks" is the whole point of async.

Runs with NO RFID hardware and NO WiFi: the reader is simulated (a list of
pretend taps) and the LED is skipped if there's no board. So you can run it
right now in Thonny, on the board or on your laptop.

THE THREE TASKS (they run concurrently)
  * reader_task    -- waits for the next card, then opens or denies it
  * heartbeat_task -- blinks the LED ~2x/sec so you can SEE nothing freezes
  * (report_task)  -- where you'd tell the hub the lock's state (stubbed)

Compare to 1_rfid_lock_simple.py: same allow-list logic, but instead of one
tap after another in a straight line, everything happens on its own timer
and they share the CPU by `await`-ing. Watch the heartbeat keep its rhythm
even as cards arrive.

HOW TO USE
  1. Run it (F5). Cards tap every couple of seconds; the heartbeat never
     stutters between them.
  2. Scroll to YOUR TURN to wire in a REAL reader, or report to the hub.
"""

# Run on the board (uasyncio) OR on a laptop (asyncio) -- same code.
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


async def sleep_ms(ms):
    # Both the board (uasyncio) and a laptop (asyncio) have asyncio.sleep()
    # in SECONDS. (uasyncio also has sleep_ms, but CPython doesn't -- this
    # one helper lets the SAME file run on both.)
    await asyncio.sleep(ms / 1000)


# Use the real LED if we're on a board; quietly skip it if we're not.
try:
    from machine import Pin
    _led = Pin(12, Pin.OUT)
    def set_led(on):
        _led.value(1 if on else 0)
except ImportError:
    def set_led(on):
        pass   # running on a laptop -- no LED, no problem


class RfidLock:
    """Same allow-list lock as 1_rfid_lock_simple.py."""

    def __init__(self, allowed):
        self.allowed = set(allowed)
        self.locked = True
        self.last_uid = None

    def tap(self, uid):
        self.last_uid = uid
        self.locked = uid not in self.allowed
        return not self.locked

    def status(self):
        return "OPEN" if not self.locked else "LOCKED"


# ---- the simulated reader: pretend cards, each after a short wait ----
# (delay in ms before this tap, card UID). Two are allowed, one isn't.
_SIM_TAPS = [
    (2000, "DE AD BE EF"),   # allowed
    (2500, "99 99 99 99"),   # stranger
    (2000, "12 34 56 78"),   # allowed
    (3000, "DE AD BE EF"),   # allowed again
]


async def read_next_card():
    """Return the next tapped card's UID, or None when the demo is done.

    THIS is the only part that touches hardware in a real build. Here it
    just plays back the simulated taps. To use a real MFRC522 reader,
    replace the body with a poll of the reader (see YOUR TURN).
    """
    if not _SIM_TAPS:
        return None
    delay, uid = _SIM_TAPS.pop(0)
    await sleep_ms(delay)     # wait as if someone walked up
    return uid


# ---- TASK 1: watch for cards and open/deny the lock ----
async def reader_task(lock):
    while True:
        uid = await read_next_card()
        if uid is None:
            print("(no more cards -- demo done, heartbeat keeps going)")
            return
        opened = lock.tap(uid)
        if opened:
            print(">>> card", uid, "-> GRANTED, door", lock.status())
            set_led(True)
            await sleep_ms(800)   # hold the door/LED briefly...
            set_led(False)
        else:
            print(">>> card", uid, "-> DENIED (unknown)")
            for _ in range(3):            # angry blink
                set_led(True);  await sleep_ms(80)
                set_led(False); await sleep_ms(80)
        # await report_to_hub(lock)   # <- see YOUR TURN


# ---- TASK 2: heartbeat, so you can SEE async never freezes ----
async def heartbeat_task():
    beat = 0
    while True:
        beat += 1
        print("   heartbeat", beat)
        await sleep_ms(500)


async def amain():
    lock = RfidLock(allowed=["DE AD BE EF", "12 34 56 78"])
    print("RFID lock running (async). Cards will tap themselves...")
    # Start both tasks; they now run at the same time.
    asyncio.create_task(heartbeat_task())
    await reader_task(lock)      # finishes when the sim runs out
    await sleep_ms(1500) # let a few more heartbeats show
    print("Stopped.")


asyncio.run(amain())


# ============================================================
# YOUR TURN
# ------------------------------------------------------------
# 1) A REAL reader. If you have an MFRC522, replace read_next_card() with a
#    poll of the reader and return the UID as a "DE AD BE EF" style string:
#
#       async def read_next_card():
#           while True:
#               if reader.PICC_IsNewCardPresent() and reader.PICC_ReadCardSerial():
#                   uid = reader.uid.uidByte[0:reader.uid.size]
#                   return " ".join("%02X" % b for b in uid)
#               await sleep_ms(150)   # yield so the heartbeat keeps beating
#
#    Notice it AWAITS between checks -- that's what keeps the lock responsive
#    while still doing everything else.
#
# 2) Tell the hub. Add a third task that reports lock state, the same way
#    simple_led.py talks to the hub (day3_wifi_hub/simple_led.py). Sketch:
#
#       async def report_to_hub(lock):
#           # PUT the lock's {"locked": bool, "card_uid": lock.last_uid} to the hub
#           ...
#
# 3) Auto-relock. Add a task that relocks the door a few seconds after it
#    opens -- easy with `await sleep_ms(...)`, and it won't freeze
#    the reader or the heartbeat.
# ============================================================
