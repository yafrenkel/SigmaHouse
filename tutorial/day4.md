# Day 4 — Sensors and the Global Alarm

**Goal:** Understand how the PIR motion sensor works, trace exactly how the global alarm fires across all houses, and add your own twist.

**Time:** ~2 hours.

**Prereqs:** Day 3 — your house is in the dashboard, dashboard toggles work both ways.

> 🔬 **Runnable example:** [examples/day4_sensors/motion_test.py](examples/day4_sensors/motion_test.py) reads the PIR on its own (no WiFi, no hub) — the quickest way to *see* the sensor fire and learn its quirks before wiring it into the alarm.

---

## Part 1 — How the PIR sensor works (15 min)

A **PIR** (Passive Infrared) sensor sees the heat that bodies give off. When something warm moves through its view, the output pin goes from `0` to `1` for about a second.

🛠 **Try this** at the Thonny REPL (your firmware is running in the background — that's fine, just open the shell):

```python
>>> from machine import Pin
>>> pir = Pin(13, Pin.IN)
>>> pir.value()
0
>>> # wave a hand in front of the sensor
>>> pir.value()
1
```

💡 **Why `Pin.IN` with no pull-up?** The PIR has its own driver chip that pushes the line either low or high — it doesn't need our help.

### Why interrupts again?

We *could* poll `pir.value()` in the main loop. But the loop also has to send keepalives, read buttons, write to the LCD… If motion happens during a 200 ms keepalive HTTP call, we'd miss it. Interrupts catch it regardless.

🛠 **Try this**: read `claude/implementation/smart_house/devices/motion.py`. Find the IRQ trigger.

```python
self._pin.irq(trigger=Pin.IRQ_RISING, handler=self._on_irq)
```

`IRQ_RISING` because the PIR pulls the line FROM 0 TO 1 when it sees you. The handler just sets `self._triggered = True`. The main loop calls `was_triggered()` which returns *and clears* the flag.

This *return-and-clear* pattern (also called "edge-consume") is exactly what `was_pressed()` does for buttons. Same idea, same implementation.

✅ **Milestone 4.1**: Wave at the sensor — `pir.value()` returns `1`.

---

## Part 2 — Trace the alarm flow on paper (20 min)

Before code, let's draw the flow. Imagine TWO houses (A and B), both armed. You wave at house A's sensor.

🛠 **Try this**: write down on paper or whiteboard, in order, what happens. Don't peek.

<details>
<summary>▶ Solution</summary>

1. PIR pin on house A goes LOW→HIGH.
2. Hardware fires the IRQ. `motion._triggered = True`.
3. House A's main loop tick: sees `motion.was_triggered()` returns True.
4. House A calls `hub.report_motion()` → `POST /api/houses/A/report_motion`.
5. Hub's `houses.report_motion("A")`:
   - House A is armed → set `alarm_triggered = True` on EVERY armed house (A and B).
6. ~0.5 sec later, house A's keepalive: `PUT /api/houses/A/keepalive`. Hub returns `{"alarm": true, "state_update": false}` and **clears A's `alarm_triggered`** (one-shot).
7. House A: `if resp.get("alarm"): buzzer.on()`.
8. ~0.5 sec later, house B's keepalive. Hub returns `{"alarm": true, ...}` and clears B's flag.
9. House B: `buzzer.on()`.
10. Both buzzers are now on until disarmed.

So the *worst-case* delay between motion and the *farthest* buzzer is **(A's report) + (B's keepalive interval)** ≈ 1.0 second. Not bad.
</details>

💡 **Why one-shot?** If `alarm_triggered` stayed `true` forever, the buzzer would re-fire on every keepalive even after the user pressed `disarm`. Clearing on read means "you got the message".

---

## Part 3 — Test it for real (20 min)

Two teams pair up. You need TWO houses both armed.

🛠 **Try this**:

1. In the dashboard, find both houses. Click **Disarmed (arm)** on each. Both should turn yellow with **Armed**.
2. Wave a hand in front of the PIR sensor of either house.
3. Within ~1 second, **both buzzers** start beeping. Both rows turn red with **TRIGGERED**.
4. Click **TRIGGERED (disarm)** on either row. That house's buzzer stops AND its row goes back to neutral.
5. The other house still buzzes — disarm it too.

✅ **Milestone 4.2**: Motion on one house fires the buzzer on another.

🛠 **Try this**: with both houses *Disarmed*, wave at one PIR. Nothing should happen — the alarm doesn't fire because no one is armed.

🛠 **Try this**: arm only ONE house. Wave at the *disarmed* house's PIR. What happens?

<details>
<summary>▶ Answer</summary>

Nothing fires. Look at `houses.report_motion`: the **reporter** has to be armed for propagation to start. If the disarmed house sees motion, it just records `state.motion.detected = True` and stops. (The "Motion!" badge briefly flashes in the dashboard, which is a nice tell.)

This is intentional: it lets a counsellor unplug a malfunctioning sensor without killing the alarm system.
</details>

---

## Part 4 — Read `houses.report_motion` (10 min)

🛠 **Try this**: Open `implementation/iot_hub/houses.py` and find `report_motion`. It's 11 lines.

```python
def report_motion(unique_id: str) -> bool:
    with _LOCK:
        reporter = HOUSES.get(unique_id)
        if reporter is None:
            return False
        reporter["state"]["motion"]["detected"] = True
        if not reporter["alarm_armed"]:
            return True
        for house in HOUSES.values():
            if house["alarm_armed"]:
                house["alarm_triggered"] = True
        return True
```

Questions:

1. Why `with _LOCK:`?
2. Why does the reporter house also get `alarm_triggered` set?
3. What if a house is `Lost` — would it get the alarm flag?

<details>
<summary>▶ Answers</summary>

1. The Flask dev server is multi-threaded. Two requests could call `report_motion` at the same time. The lock makes the dict update atomic — no half-applied changes. (Try removing the lock and pounding the endpoint with 100 parallel requests; you'll see weird state.)
2. The for loop walks EVERY armed house. The reporter is in `HOUSES.values()`, so it gets caught too — its own buzzer fires.
3. Yes, *if* it's still marked `alarm_armed`. But look at `mark_lost_if_stale()`: it sets `alarm_armed = False` when a house goes Lost. So in practice, Lost houses are never in the armed set.
</details>

---

## Part 5 — Write a feature: "panic mode" (30 min)

Right now, the dashboard has `arm` per house. Let's add **arm all** — single click arms every house at once, like setting an alarm system before everyone leaves.

### Step 1 — data layer

Add to `houses.py`:

```python
def arm_all() -> int:
    """Arm every active house. Returns how many were armed."""
    count = 0
    with _LOCK:
        for house in HOUSES.values():
            # TODO: only arm if status is "Active"
            # TODO: set alarm_armed = True
            # TODO: increment count
            pass
    return count
```

<details>
<summary>▶ Solution</summary>

```python
def arm_all() -> int:
    """Arm every active house. Returns how many were armed."""
    count = 0
    with _LOCK:
        for house in HOUSES.values():
            if house["status"] == "Active":
                house["alarm_armed"] = True
                count += 1
    return count
```
</details>

### Step 2 — route

Add to `app.py`:

```python
@app.route("/api/arm_all", methods=["POST"])
def arm_all():
    n = houses.arm_all()
    return jsonify({"ok": True, "count": n})
```

### Step 3 — dashboard button

Open `templates/index.html`. Above the table, add:

```html
<p>
  <button id="arm-all">Arm all</button>
  <button id="disarm-all">Disarm all</button>
</p>
```

Open `static/dashboard.js`. At the top, after `const REFRESH_MS`:

```javascript
document.getElementById("arm-all").onclick = async () => {
  await fetch("/api/arm_all", { method: "POST" });
  refresh();
};
document.getElementById("disarm-all").onclick = async () => {
  await fetch("/api/disarm_all", { method: "POST" });
  refresh();
};
```

(Day 1 added `disarm_all` already. If your team didn't, the solution from Day 1 has it.)

### Step 4 — try it

Restart the hub. Refresh the dashboard hard (Ctrl-Shift-R) so the new HTML loads. Click **Arm all** — every house turns yellow. Wave at one PIR — every house's buzzer fires. Click **Disarm all** — silence.

✅ **Milestone 4.3**: One click arms/disarms all houses.

---

## Part 6 — Stretch (10 min)

⚡ **Easy**: Add a counter on the dashboard: "Houses armed: X / Y".

⚡ **Medium**: Make `arm_all` skip houses that have been silent for >30 seconds (define "silent" by checking `last_seen`). Reduces false alarms from flaky boards.

⚡ **Hard**: Add a "delayed arm" feature: clicking arm waits 10 seconds before actually setting `alarm_armed`, displayed as a countdown on the LCD of each house. Lets people leave the room before the alarm goes live. Real alarm panels do exactly this.

---

## What you learned today

- PIR sensors output a digital pulse on motion.
- The `was_triggered()` flag pattern keeps interrupts fast and the main loop in control.
- The global alarm has TWO conditions: the *reporter* must be armed, AND each *receiver* must be armed.
- The "one-shot" alarm flag avoids re-firing on every keepalive.
- A multi-house feature usually needs: one new function in `houses.py`, one route in `app.py`, and (sometimes) one button in the dashboard.

**Tomorrow:** the async version of the firmware, and a final project of your choice. → [day5.md](day5.md)
