# Counsellor's Guide — Day 4: Sensors and the Global Alarm

**Lab time:** ~2 hours. **Hands-on:** ~110 min.

This is the most fun day if connectivity from Day 3 is stable. The "wave at one house, all houses scream" moment is the camp's greatest hit. Plan a 5-min photo opportunity around it.

## Pacing

| Min | Activity | Watch out for |
|---:|---|---|
| 0–10 | Opener slide; demo the alarm yourself first | Don't spoil it — they'll see in 30 min |
| 10–25 | PIR sensor at the REPL | Sensitivity dials on the PIR — they may need adjustment |
| 25–45 | Paper trace of the alarm flow | Quiet stretch; encourage discussion within pairs |
| 45–70 | Test with TWO real houses | The "wave → BUZZ" moment. Get the photo. |
| 70–80 | Read `houses.report_motion` together | Group discussion of why-the-lock |
| 80–110 | Build "arm-all" + "disarm-all" buttons | HTML + JS edits; static assets cached |
| 110–120 | Demo + stretch | — |

## Where they'll get stuck

1. **PIR sensor doesn't fire** — most common cause: PIR has TWO trim potentiometers (sensitivity and time-out). One may be cranked all the way down. Show them the orange screws on the back — quarter-turn clockwise to increase sensitivity. Also: PIRs need ~30 sec of "warm up" after power on; first wave may be ignored.

2. **PIR fires constantly even in still rooms** — sensitivity too high, or air-conditioning vent blowing on it. Reduce sensitivity, or block the AC current.

3. **One house's wave triggers the wave-er but not other houses** — the receiving house isn't actually armed in the dashboard. Re-arm it, look at the row color (yellow = armed). Also check: did its keepalive actually run? Watch the receiving board's shell for HTTP activity.

4. **Buzzer fires once and stays on** — that's actually correct, but they may expect it to time out. The model is "alarm stays on until disarmed". Mention this in advance.

5. **Disarm doesn't stop the buzzer** — they're disarming via the dashboard, but the board hasn't pulled new state yet. State updates lag by 1 keepalive (~1 sec). If it lasts >2 sec, something is wrong: check `arm_alarm` actually clears `state.buzzer.active` and sets `pending_state_update`.

6. **Edited HTML, dashboard looks the same** — browsers cache HTML and JS aggressively. Force-refresh with **Ctrl-Shift-R** (or **Ctrl-F5**).

7. **`arm_all()` button does nothing visible** — they forgot to set `pending_state_update = True`, so devices don't know to pull new state, so the LCD/buzzer don't update on the boards. The dashboard column updates fine because it just shows `alarm_armed` directly. Hint: "the dashboard updates but the board doesn't — what flag tells the board to refresh?"

8. **`arm_all()` arms `Lost` houses** — the spec said "active only". Check their `if house["status"] == "Active":` is correct.

## Ready-to-paste hints

**Hint H1** — PIR doesn't trigger:
> Two things: (1) PIR has trim screws on the back. Turn the orange "sensitivity" one a quarter turn clockwise. (2) PIR ignores the first 30 sec after power-up. Wait, then test.

**Hint H2** — Wave on house A doesn't fire house B's buzzer:
> Three checks in order:
> 1. Is house B's row YELLOW (armed) before the wave? If not, click "Disarmed (arm)" first.
> 2. Open Thonny on house B's laptop. After waving at A, do you see the keepalive returning `{"alarm": true, ...}`? If yes, it's a buzzer issue. If no, hub state didn't propagate.
> 3. From any laptop: `curl -X POST http://<laptop-ip>:8080/api/houses/HOUSE_A/report_motion`. Does that fire B? If yes, the issue is the PIR. If no, the issue is `houses.report_motion`.

**Hint H3** — Dashboard arm-all button doesn't visibly do anything:
> Open browser DevTools (F12) → Network tab → click the button. Do you see `arm_all` appear? If 404, the route isn't registered (restart the hub). If 200, the call worked but the dashboard hasn't refreshed — try `refresh()` in the click handler.

**Hint H4** — They want to also disable on Lost houses:
> ```python
> for house in HOUSES.values():
>     if house["status"] != "Active":
>         continue
>     ...
> ```

## What "done" looks like

- **Milestone 4.1** — Wave at PIR → REPL `pir.value()` returns 1.
- **Milestone 4.2** — Two armed houses; wave at house A → both buzzers fire, both rows red.
- **Milestone 4.3** — Single click on dashboard "Arm all" → every Active row turns yellow.

## Stretch supervision

- **Counter "X / Y armed"** — small JS task; help them locate the right place to add it (above the table).
- **Skip silent houses** — needs comparing `last_seen` to current time. Show them how Python's `datetime.strptime` works if needed.
- **Delayed arm** — fairly involved (countdown timer on LCD AND server-side state). Only push to the strongest pair.

## Things to celebrate publicly

- The first "wave → BUZZ" of the day. Get everyone to look.
- The first team that successfully adds `arm_all`. Their screen on the projector for 30 sec.

## Things to debug publicly (if they happen)

- **A board went Lost mid-demo** — perfect teaching moment for what the watchdog does. Show that disarming Lost houses doesn't help (it's not in the armed set).
- **A keepalive returned `alarm: true` twice** — bug somewhere. Likely the one-shot logic broke. Hunt it together.

## Setup before students arrive

- Verify all boards from yesterday still register Active when powered on.
- Test the alarm yourself with two boards. Should "just work" — if not, fix it before students see the broken version.
- Have a working `disarm_all` from Day 1 ready in your hub. Otherwise the dashboard arm-all/disarm-all pair won't work fully.
