# Counsellor's Guide

One page per day, written for whoever is running the lab. Skim the right day BEFORE the session.

| File | Day | Focus |
|---|---|---|
| [day1.md](day1.md) | 1 | Flask hub, HTTP, first endpoint |
| [day2.md](day2.md) | 2 | MicroPython REPL, LED, button, IRQ |
| [day3.md](day3.md) | 3 | WiFi, urequests, full firmware |
| [day4.md](day4.md) | 4 | PIR sensor, global alarm |
| [day5.md](day5.md) | 5 | Async, final project |

Each day includes:
- **Pacing** — minute-by-minute breakdown so you know if a group is behind.
- **Where they'll get stuck** — the predictable confusion points.
- **Ready-to-paste hints** — small nudges to copy into the chat or onto a whiteboard. Use these instead of giving away solutions.
- **What "done" looks like** — concrete checks for each milestone.

## General running tips

- **Start with a 5-minute framing** before campers touch keyboards — state the day's goal and show the finished result. (Project the top of that day's tutorial page if you like.)
- **Demo the milestone first.** If you show the working result, students know what they're aiming at.
- **Pair students.** Two campers per ESP32 is the sweet spot — one types, one looks up reference. Swap halfway.
- **Hint, don't solve.** When a student is stuck, ask "what does the error message say?" before offering hints. The fastest learners are the ones who read the error first.
- **Watch for power vampires.** A few students always race ahead and start helping/distracting others. Direct them to the stretch challenges — that's what they're for.

## Common across all days

- **Saving to the wrong place.** In Thonny, "File → Save" defaults to PC, NOT the board. They need "Save as… → MicroPython device" the first time. Once `main.py` exists on the board, hitting RESET runs it. Files saved to PC don't run.
- **Forgetting to close `urequests` responses.** Symptom: board crashes after ~10 HTTP calls. Always `r.close()` (or use `try/finally`).
- **Hardcoded IP in `secrets.py`.** If the laptop reboots and gets a new DHCP lease, every student's `secrets.py` is wrong. Either set a static IP on the laptop or write today's IP on the whiteboard at the start of each day.
- **Firewall blocking inbound 8080.** Windows asks ONCE on first run; if a student clicked "Block" by mistake, no boards can connect. Re-run as admin or open the firewall manually.
- **One team's flaky board affecting another's debug.** When something doesn't work, eliminate variables: from PyCharm terminal, `curl http://laptop-ip:8080/api/houses` should always show what the dashboard shows. If they differ, refresh the browser. If `curl` fails, the student is on the wrong WiFi.

## End-of-day routine

1. Last 10 minutes: stop new work, demo at least one team's milestone to the room.
2. Have students leave their boards plugged in (boards keep running with `main.py`).
3. **Don't shut down the hub** between days — losing in-memory state means every team has to re-register tomorrow morning. Just lock the laptop.

## Tools you should have open

- A terminal at `claude/implementation/iot_hub/` for poking the API while diagnosing.
- The dashboard in a browser, kept refreshed.
- This guide on a second monitor or printed.
- The corresponding `tutorial/dayN.md` so you can quote the same text the students are reading.
