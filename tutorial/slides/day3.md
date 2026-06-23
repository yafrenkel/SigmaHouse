---
marp: true
theme: default
paginate: true
size: 16:9
---

<!-- _class: lead -->

# Day 3
## WiFi + Hub

The day your board joins the network.

---

## What you'll have at lunch

- Your ESP32 connected to camp WiFi
- Your house showing up in the dashboard
- Click the LED button in the browser → real LED switches

**It feels like magic. It's just HTTP.**

---

## The big idea today

```
        Day 1                    Day 2                    Day 3
   [hub on laptop]          [board with LED]          [hub] ↔ [board]
                                                       HTTP over WiFi
```

Your two systems shake hands.

---

## Vocabulary

| Word | Meaning |
|---|---|
| **WiFi** | Wireless network (2.4 GHz radio) |
| **IP address** | Each device's "phone number" on the network |
| **HTTP client** | Code that SENDS requests (vs. server that receives) |
| **`urequests`** | MicroPython's HTTP client library |
| **Keepalive** | Periodic message: "I'm still alive" |

---

## Today's milestones

- ✅ **3.1** `wlan.isconnected()` is True
- ✅ **3.2** Your `unique_id` appears in dashboard
- ✅ **3.3** Full firmware runs; row stays Active
- ✅ **3.4** Round-trip: dashboard ↔ button

---

## ⚠️ The trap nobody escapes

```python
r = urequests.get(url)
data = r.json()
# DO NOT FORGET:
r.close()
```

After ~10 unclosed responses, your board crashes. Use:

```python
r = urequests.get(url)
try:
    data = r.json()
finally:
    r.close()
```

---

## Setup checklist

Today's hub URL is on the whiteboard.

In `secrets.py`:
```python
WIFI_SSID = "..."         # camp WiFi name
WIFI_PASS = "..."         # camp WiFi password
HUB_URL   = "http://...:8080"   # from whiteboard
```

**Save it on the BOARD, not on the PC.**

---

<!-- _class: lead -->

# Open `tutorial/day3.md`
# Find your laptop's IP first.
