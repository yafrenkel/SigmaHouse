# Sigma Camp IoT — 5-Day Semilab

A 5-day, 2-hour-per-day curriculum for advanced 14-year-olds who already know basic Python. By the end you'll have an internet-of-things system: many ESP32 "smart houses" controlled from a dashboard running on a counsellor's laptop, with a global alarm that fires across every house.

## What you'll build

```
                            Dashboard in browser
                                    │
                                    ▼
                        ┌───────────────────────┐
                        │   Flask hub (laptop)  │
                        └───────────────────────┘
                            ▲    ▲    ▲    ▲
                  HTTP/WiFi │    │    │    │
                       ┌────┘    │    │    └────┐
                       ▼         ▼    ▼         ▼
                    [ESP32]   [ESP32] [ESP32]  [ESP32]
                     House A   House B  House C  House D
```

Each ESP32 has: LED, two buttons, motion sensor, fan, buzzer, LCD screen.

## Day plan

| Day | Topic | What works at the end |
|---|---|---|
| [1](day1.md) | **The Hub** — HTTP, Flask, dashboard | You can register fake houses with `curl` and see them appear. |
| [2](day2.md) | **ESP32 first steps** — MicroPython, LED, button | Pressing the button toggles the LED. No WiFi yet. |
| [3](day3.md) | **WiFi + talking to the hub** | Your physical board appears in the dashboard. Toggling the dashboard changes the real LED. |
| [4](day4.md) | **Sensors + global alarm** — PIR, interrupts | Wave at one armed house → all armed houses buzz. |
| [5](day5.md) | **Async + final project** | You diff `app_sync.py` vs `app_async.py` and add your own feature. |

## What you need to know going in

- Variables, `if`/`else`, `while`/`for`, lists, dicts, functions in Python.
- How to open files in PyCharm and Thonny.
- How to read an error message and look up what's wrong.

If any of those is shaky, ask a counsellor for a 5-minute refresher.

## Tools you'll use

- **PyCharm Community** — for the Flask hub (Python on the laptop).
- **Thonny** — for the ESP32 firmware (MicroPython on the board).
- **A web browser** — for the dashboard.
- **A terminal** — for `curl` (Day 1) and quick checks.

All software was pre-installed on your laptop before camp; no internet required during the lab.

## Hardware you'll touch

| Pin | Component | What it does |
|---:|---|---|
| 12 | LED | Light on/off |
| 26 | Button A | Cycles the LCD menu |
| 25 | Button B | Toggles the selected device |
| 13 | PIR motion sensor | Detects movement |
| 18, 19 | Fan | Spins (H-bridge motor) |
| 4 | Buzzer | Alarm tone |
| 22, 21 | LCD (I2C) | 2-line text screen |

Don't worry about memorising this — `claude/implementation/smart_house/config.py` has it all.

## Conventions in this tutorial

- 🛠 **Try this** = hands-on step. Do it, don't just read it.
- 💡 **Why?** = short explanation of what just happened.
- ✅ **Milestone** = checkpoint. Show a counsellor before continuing.
- ⚡ **Stretch** = optional bonus if you finish early.
- ▶ **Solution** = collapsible answer. Try yourself first.

## Files you'll edit vs. files you'll just read

You'll **edit** small things in:
- `implementation/iot_hub/app.py` (one new endpoint on Day 1)
- `implementation/smart_house/secrets.py` (your WiFi info on Day 3)
- `implementation/smart_house/config.py` (`USE_ASYNC` flag on Day 5)
- A new feature file of your choice on Day 5

You'll **read** (and understand) but mostly leave alone:
- `implementation/iot_hub/houses.py` — the data layer
- `implementation/smart_house/devices/*.py` — the hardware drivers
- `implementation/smart_house/hub_client.py` — the HTTP client
- `implementation/smart_house/app_sync.py` and `app_async.py` — the main loops

The whole project is small (~1500 lines including blank lines). You can read it all in a day.

## Kick-off

- **[icebreaker.md](icebreaker.md)** — "You Are the Internet": a 20-min no-computer game for the very start of Day 1. Campers physically act out HTTP requests, keepalives, and the global alarm before writing any code.

## Reference

- **[glossary.md](glossary.md)** — every acronym used anywhere in this camp (HTTP, TCP, WiFi, GPIO, I2C, IRQ, …), spelled out with a one-line meaning. Keep it open while you work.

## Optional deep-dives

- **[background/how_the_internet_works.md](background/how_the_internet_works.md)** — short history of the internet, TCP/IP layers, IP/ports, DNS, and how HTTP is "just text". Not required for the labs — for campers who want to know what's *really* happening. ~20 min read.

## Visual references

- **[diagrams/](diagrams/README.md)** — three draw.io diagrams (the hub side; the ESP32 side; HTTP + the server loop concept). Project on screen during sessions or print as A4 reference sheets.

## For staff (counsellors)

- **[counsellor/](counsellor/README.md)** — pacing, common mistakes, ready-to-paste hints (one page per day).
- **[slides/](slides/README.md)** — opening slide deck per day in Marp markdown. Render to PDF once before camp.

## Ready?

Open [day1.md](day1.md) and let's go.
