# Counsellor's Guide — Day 1: The Hub

**Lab time:** ~2 hours (120 min). Subtract 10 min for the opener slide deck. **~110 min hands-on.**

> 🎲 **Optional opener:** run the [ice-breaker game](../icebreaker.md) ("You Are the Internet", ~20 min) *before* the slides. Campers physically act out HTTP, keepalives, and the alarm — so the code lands faster. If you do this, either start Day 1 earlier or trim Part 5 (the `disarm_all` endpoint) and set it as homework. Worth it on day one of camp when nobody knows each other yet.

## Pacing

| Min | Activity | Watch out for |
|---:|---|---|
| 0–10 | Opener slides + demo dashboard | Students trying to follow along on their laptops; ask them to just watch first |
| 10–25 | Setup PyCharm + offline pip install | Microsoft Store Python stub. Wheels path wrong. Firewall prompt on first run. |
| 25–40 | HTTP concepts + first `curl` | Students typing "curl" in Windows cmd vs. PyCharm terminal — both work |
| 40–60 | Register fake house + keepalive | Forgetting `Content-Type` header → `silent=True` returns `{}` and they think nothing broke |
| 60–80 | Read existing routes | Quietest stretch; circulate and ask "what does this line do?" |
| 80–110 | Build `/api/disarm_all` endpoint | Forgetting to restart the hub after editing. PyCharm's auto-restart is OFF (`use_reloader=False` in `app.py`). |
| 110–120 | Show milestones, brief stretch supervision | — |

## Where they'll get stuck

1. **`pip install` fails** — they didn't `cd` into `implementation/iot_hub` first, so `requirements.txt` and `wheels/` aren't found. Hint: "look at where your terminal is".

2. **`curl` not found on Windows** — Git Bash or PowerShell 7+ has it; old `cmd.exe` may not. Just direct them to PyCharm's bottom Terminal panel — it inherits Git Bash if Git is installed (which it is on every camp laptop).

3. **`{}` response when registering** — they sent JSON but forgot `-H "Content-Type: application/json"`. Flask's `request.get_json(silent=True)` returns `None` → falls back to `{}` → `unique_id` is missing → 400. Hint: paste this exact line:
   ```bash
   curl -X POST http://localhost:8080/api/houses -H "Content-Type: application/json" -d '{"unique_id":"FAKE001","ip_address":"127.0.0.1"}'
   ```

4. **Quoting hell on Windows** — single quotes around JSON don't work in `cmd.exe`. They DO work in Git Bash (PyCharm's default terminal). If they're using PowerShell, the JSON needs different escaping. Push them to PyCharm Terminal.

5. **"My endpoint returns 404"** — they edited the file but the running hub is the old code. PyCharm doesn't auto-restart Flask in this project (intentional — see `use_reloader=False` so the watchdog doesn't double up). Tell them to **stop and re-run** every code change.

6. **`disarm_all()` shadows `houses.disarm_all`** — when they name the route handler the same as the module function (`def disarm_all():` in `app.py`), Python finds the local function first. Hint:
   ```python
   @app.route("/api/disarm_all", methods=["POST"])
   def disarm_all():
       n = houses.disarm_all()   # <-- module name first!
       return jsonify({"ok": True, "count": n})
   ```

## Ready-to-paste hints

**Hint H1** — Student is staring at a blank `disarm_all()` data-layer function:
> Look at `arm_alarm()` right above. When `armed=False`, what three things does it clear? Do those three things, but for every house in the loop, not just one.

**Hint H2** — Endpoint registered but `curl` returns 404:
> Did you save the file (Ctrl+S)? Did you stop and restart the hub? Top-right red square, then green play.

**Hint H3** — `count` always returns 0:
> You're checking `if house["alarm_armed"]:` AFTER setting it to False. Increment `count` BEFORE you change `alarm_armed`.

**Hint H4** — They want to test without typing 4 curl commands:
> In PyCharm terminal, paste this all at once:
> ```bash
> for id in FAKE001 FAKE002 FAKE003; do
>   curl -X POST http://localhost:8080/api/houses -H "Content-Type: application/json" -d "{\"unique_id\":\"$id\",\"ip_address\":\"127.0.0.1\"}" >/dev/null
>   curl -X POST http://localhost:8080/api/houses/$id/arm -H "Content-Type: application/json" -d '{"armed":true}' >/dev/null
> done
> ```

## What "done" looks like

- **Milestone 1.1** — `http://localhost:8080/` shows "Waiting for houses to register…" in their browser.
- **Milestone 1.2** — Their `curl -X POST http://localhost:8080/api/disarm_all` returns `{"ok": true, "count": N}` with `N >= 2`, and the dashboard shows previously armed houses now disarmed.

## Stretch supervision

The Day 1 stretches are the gentlest of the week:
- **`/api/stats`** — 10-minute task; encourage everyone who finishes early.
- **Dashboard button** — needs editing JS; help them find `dashboard.js` and add to the existing button setup pattern.
- **`restart_requested` flag** — touches three places (`houses.py`, `app.py`, the keepalive return value). Only push this on a clearly fast pair.

## Things to look for in walkarounds

- **Are they reading errors?** If yes, they're learning. If no, sit next to them and read it together.
- **Is the dashboard refreshing?** If it's stuck on "Waiting…" but they know they registered houses, they're hitting a different hub (different port? different host?). Check their URL.
- **Are they comfortable in PyCharm?** If they don't know how to open the terminal, lost 30 minutes is real. Show once, they remember.
