---
marp: true
theme: default
paginate: true
size: 16:9
---

<!-- _class: lead -->

# Day 4
## Sensors + Global Alarm

Wave at one house. **Every** house screams.

---

## What you'll have at lunch

- Working PIR motion sensor
- Two armed houses → wave triggers all buzzers
- A new "Arm all" button on the dashboard

---

## The big idea today

```
[house A]   wave →   PIR fires
    │
    │ POST /report_motion
    ▼
[hub]   sets alarm_triggered = True
        on EVERY armed house
    │
    │ next keepalive returns alarm: true
    ▼
[house A][house B][house C] → all BUZZ
```

---

## Vocabulary

| Word | Meaning |
|---|---|
| **PIR** | "Passive Infrared" — sees body heat moving |
| **Edge** | The moment a pin's value changes |
| **Rising edge** | 0 → 1 |
| **Falling edge** | 1 → 0 |
| **One-shot** | Flag fires once, then auto-clears |

---

## Today's milestones

- ✅ **4.1** PIR's `pin.value()` returns 1 when you wave
- ✅ **4.2** Two-house alarm propagation works
- ✅ **4.3** Dashboard "Arm all" button works

---

## The flow on paper

Before code: **trace it on paper.**

1. Hardware → 2. IRQ → 3. Loop → 4. Hub → 5. Other houses → 6. Buzzer.

If you can draw the steps, you can debug them.

---

## A multi-house feature: the recipe

**Three places to edit:**

1. **`houses.py`** — function that does the actual work.
2. **`app.py`** — route that exposes it via HTTP.
3. **dashboard** — button or view that calls it.

That's it. Every Day-4 stretch follows this recipe.

---

<!-- _class: lead -->

# Open `tutorial/day4.md`
# Get the photo of the wave-and-buzz.
