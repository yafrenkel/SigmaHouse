# Counsellor's Guide — Day 5: Async + Final Project

**Lab time:** ~2 hours. **Hands-on:** ~110 min.

The first 50 minutes are tightly scripted (sync vs async). The last 60 are open-ended (final project). Your role flips: from "lecturer" in the first half to "consultant" in the second.

## Pacing

| Min | Activity | Watch out for |
|---:|---|---|
| 0–10 | Opener slide + day 5 milestones | — |
| 10–25 | Switch USE_ASYNC=True, observe identical behavior | Saving `config.py` to PC instead of board (again) |
| 25–50 | Side-by-side compare in PyCharm | "Compare Files" hides in right-click menu — show once |
| 50–60 | Discussion: when sync vs async | Don't over-lecture — keep momentum |
| 60–110 | Final project (5 options) | The role of staff: ask "what's your next step?", not "here's how" |
| 110–120 | Project demos | Each pair gets 2 minutes |

## Where they'll get stuck

### First half (sync vs async)

1. **`config.py` change doesn't take effect** — saved to PC. Same Day 2 lesson, different file. Hint: "Right-click in board pane → Save here? Where does Thonny say it's editing the file?"

2. **Async version doesn't start** — they typoed something while exploring. If a board boots and silently does nothing, swap back to sync first to confirm the board itself is OK, then debug the async file.

3. **They believe async is "faster"** — common misconception. Both versions take the same time per HTTP call (since `urequests` is blocking either way). The difference is responsiveness — buttons are checked more often in async because the keepalive task isn't blocking the button task. Set up the experiment: with sync, count how many button presses register during a 1-sec keepalive (zero, because the loop sleeps). With async, multiple register because `task_buttons` has its own clock.

### Second half (final project)

Each option has its own gotchas:

**Option A — Doorbell:**
- They forget to turn LEDs back OFF after 2 sec. Hint: `threading.Timer` in the route handler.
- They iterate `HOUSES` outside the lock. Hint: same pattern as `arm_all`.

**Option B — Fan party:**
- The fan's `on()` method takes `clockwise=True/False`. They miss this — point them at `devices/fan.py`.
- They want to alternate per click → store state in `app_sync.py` (a module-level boolean works).

**Option C — Statistics page:**
- Jinja syntax bites them: `{{ var }}` for variables. Show one example.
- They forget to add a `last_alarm_time` global to `houses.py`.

**Option D — Soft alarm escalation:**
- Buzzer's PWM `duty()` parameter is 0–1023, not 0–1. They'll often write `set_level(0.5)` — show that 0.5 truncates to 0.
- They want to use `time.sleep` in the main loop. That blocks keepalives. Show them the timestamp pattern: store `alarm_started_at`, recompute level each loop iteration based on `ticks_diff`.

**Option E — Two-house Morse chat:**
- Long-press detection: easiest pattern is to NOT use IRQ_FALLING+IRQ_RISING; use IRQ_FALLING (start), record `ticks_ms()`, then poll for release in the main loop. Subtle.
- They need to know the partner's uid. Easiest: hardcode in `secrets.py` as `PARTNER_UID = "AABBCC..."`. (Adds a line that students who picked other options don't have — that's fine.)

## Ready-to-paste hints

**Hint H1** — They claim "async is broken":
> Switch back to USE_ASYNC=False, reset, verify behavior. If sync works, the async file has a bug. Show me your async file's `task_buttons`. Most async bugs in this project are forgetting `await` somewhere.

**Hint H2** — Doorbell LEDs don't turn off:
> Look up `threading.Timer(seconds, function)`. In the route, after turning all LEDs on, schedule a function to run in 2 sec that turns them off and clears `pending_state_update`.

**Hint H3** — Stats page Jinja syntax:
> ```html
> <p>Total: {{ total }}</p>
> <p>Active: {{ active }} / {{ total }}</p>
> ```
> In the route:
> ```python
> return render_template("stats.html", total=len(HOUSES), active=...)
> ```

**Hint H4** — Buzzer escalation: where to track time:
> In `app_sync.py`, near the top:
> ```python
> alarm_started_at = None
> ```
> When `resp["alarm"]` becomes True, set `alarm_started_at = time.ticks_ms()` IF it was None. When alarm goes False, set it to None. Each tick of the loop, compute `elapsed = ticks_diff(now, alarm_started_at)` and pick a duty level.

**Hint H5** — Long press detection:
> Don't fight the interrupt. Use IRQ_FALLING to record the start, then in the main loop poll the pin's value. When it goes back to 1, compute the duration:
> ```python
> if button._pin.value() == 1 and button._press_started:
>     duration = ticks_diff(ticks_ms(), button._press_started)
>     button._press_started = None
>     send_dot() if duration < 200 else send_dash()
> ```

## What "done" looks like

- **Milestone 5.1** — `USE_ASYNC=True` runs identically to sync.
- **Milestone 5.2** — Their final project runs end-to-end at the demo.
- **Milestone 5.3** — Each pair speaks for 2 minutes about what they built.

## Demo session structure (last 10 min)

- 90 sec setup per team (camera on their dashboard, board in the corner of the frame)
- 60 sec demo
- 30 sec Q&A

Suggested order:
1. Easiest projects first (B — Fan party) to build confidence.
2. Most visual ones in the middle (A — Doorbell, D — Soft alarm).
3. Most impressive last (E — Morse chat between two teams) for a finale.

## Things to be ready for

- **A team will want to keep going past time.** That's a great problem. Note their idea, send them home with the project link, encourage them to pick it up.
- **A team will produce something you didn't predict.** Lean into it — ask them to explain it to the room.
- **A team's project will fail at demo.** Have a backup: their previous milestone (Day 4) still works. Demo that.

## Closing the camp

- Show the original `SigmaHouse-master/` for 2 minutes — students can see what the "messy production version" of their work looks like, and the connection between camp and real software.
- Mention the Day 5 "where to go next" list. The keenest will follow up.
- Hand out USB sticks with the full project so they can keep tinkering at home.
