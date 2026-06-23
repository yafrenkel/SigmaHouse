# Ice-Breaker — "You Are the Internet"

A no-computer, get-up-and-move game for the very start of camp (Day 1, before any code). Campers physically *become* the browser, the server, the network, and the smart houses — so by the time they open PyCharm, the whole request/response idea already lives in their bodies.

- **Time:** 20-25 min total (5 min warm-up + 15-20 min main game)
- **Group size:** 6-30. Scales by adding more "houses".
- **Materials (all offline):** index cards or sticky notes, 1 pen per camper, 1 clipboard (or just a big sheet) for the "server", optional colored cards for LED states. That's it.
- **Energy:** loud and silly on purpose. The alarm round gets chaotic — that's the point.

---

## Warm-up (5 min) — "Pick your unique_id"

Real devices identify themselves by a **MAC address** — a unique code burned into the chip. Campers do the same.

🛠 **Run it:**
1. Each camper writes on a card: a made-up 6-character **hacker handle / unique_id** (letters + numbers, e.g. `R2D2X9`, `K1TT3N`) and **one true thing about themselves** ("I have 3 cats").
2. Go around: each person says *"I'm house `R2D2X9` and I have 3 cats."*
3. They keep this card — it's their identity for the whole game (and a fun callback when they see their ESP32's real `unique_id` on Day 3).

💡 **Bridge:** "That code is exactly what your ESP32 will send to register itself. Yours is random; the board's is its MAC address."

---

## Main game (15-20 min) — "You Are the Internet"

### Roles (assign out loud)

| Role | How many | Holds |
|---|---|---|
| 🖥 **Dashboard** (client) | 1-2 | A "remote control" card |
| 📡 **Router** | 1 | Nothing — just relays messages |
| 🐍 **Server** (the hub) | 1 (a counsellor is great here for round 1) | The clipboard = the **HOUSES** list |
| 🏠 **Smart Houses** | everyone else | Their unique_id card + an "LED: off" card |

Set the room up so the **Houses** are spread out, the **Server** sits at a desk with the clipboard, the **Router** stands between the Houses and the Server, and the **Dashboard** stands near the Router. Messages must physically travel: House → Router → Server, and back.

> **The rule:** you may only *speak the message out loud* and *walk it through the Router*. No shortcuts. The Router is the only path — just like real packets going through your camp router.

### Round 1 — Registration (POST)

Each House walks their card to the Router, who walks it to the Server, saying:

> **"POST! Register me — house `R2D2X9`!"**

The Server writes the unique_id on the clipboard. Now they're "Active".

💡 *This is exactly `POST /api/houses`.*

### Round 2 — Keepalive + the Watchdog (PUT)

Counsellor calls **"TICK!"** every ~10 seconds. On each tick, every House must shout **"PUT keepalive!"** and wave at the Server.

- Miss **two ticks in a row** (sat down, distracted, talking) → the Server crosses you off as **"Lost"**. To get back in, you must `POST` register again.

💡 *This is the `/keepalive` heartbeat and the watchdog that marks silent houses "Lost" after 60s. Now they'll never forget why their board "disappeared" if it stops phoning home.*

### Round 3 — Toggle the LED (POST + response)

The **Dashboard** picks a house and announces:

> **"POST! Toggle the LED on house `R2D2X9`!"**

The message travels Dashboard → Router → Server. The Server writes "LED = ON" next to that house. On the **next TICK**, when that house sends its keepalive, the Server replies:

> **"state_update! Go look at your state."**

The house then flips its card to **"LED: on"** and strikes a pose / raises both hands (they "light up" 💡).

💡 *This is the real round-trip you'll see on Day 3: dashboard click → hub stores it → next keepalive says "state_update" → device pulls new state → LED changes. There's a deliberate delay (you wait for the next tick) — exactly like the ~1-second lag on real hardware.*

### Round 4 — GLOBAL ALARM (the chaotic finale)

1. Pick a few houses to "arm" their alarm — they hold their card up high.
2. Counsellor secretly taps ONE armed house on the shoulder: **"You saw motion!"**
3. That house sprints (walks fast!) to the Server: **"POST report_motion!"**
4. The Server announces to every **armed** house: "alarm!"
5. On the next **TICK**, every armed house yells **"BZZZZZZ!"** at the top of their lungs. 📢
6. To stop it: the Dashboard sends **"POST disarm!"** for each house.

💡 *This is the global alarm: motion in one armed house fires the buzzer in ALL armed houses. The kids literally run the protocol — and it's the loudest, most memorable 60 seconds of Day 1.*

---

## 🎯 Tailored for THIS semilab: 7 campers + 1 TA + you

You don't have enough people to waste anyone on a passive role, so here's the exact casting:

| Who | Role | Why |
|---|---|---|
| **You (instructor)** | 🐍 **Server + Narrator** | The teaching seat. You hold the clipboard (the HOUSES list), you call **"TICK!"**, you decide who's "Lost", you announce the alarm, and you can freeze the action any time to explain. With only 7 kids you can comfortably do Server *and* tempo-caller at once. |
| **TA** | 📡 **Router + Packet Gremlin** | Relays every message House↔Server, and runs the "drop a packet" twist below. Also your second pair of eyes for spotting houses that miss a TICK. |
| **All 7 campers** | 🏠 **Smart Houses** (rounds 1-2) | Everyone registers, everyone keepalives. Maximum participation. |
| **1 camper, rotating** | 🖥 **Dashboard** (rounds 3-4) | For the toggle and alarm rounds, promote one House to Dashboard. **Rotate it each round** so different kids get the "boss" seat. Over the rounds (and a couple of repeats) everyone gets a turn. |

So: nobody sits out, you stay in control of pace, and the TA gets the fun chaos job. If you'd rather roam and teach hands-free, swap — **TA = Server**, **you = Narrator/"Internet Weather"** injecting events ("storm! packets drop!", "power flicker!"). Either works.

### A 7-house tip
With 7 houses the alarm round is loud but manageable. Arm **4-5** of them (leave 2-3 disarmed so the contrast is visible — disarmed houses stay silent while the armed ones scream). That visibly proves "only *armed* houses buzz."

---

## Optional twist — "The Router drops packets" (teaches TCP)

Give the Router a secret power: once per round, they may **crumple a message and drop it on the floor** instead of delivering it.

When a House's keepalive vanishes and they almost get marked "Lost", ask: *"How could we make sure a message always gets through?"*

💡 *Answer: you'd re-send until you get a confirmation. That's **TCP** — the layer that re-sends lost packets so HTTP never has to worry. Real `urequests` gets this for free.*

---

## Debrief (3 min) — connect it to the code

Stand everyone in a circle and map the game to what they're about to build:

| In the game you… | In the code it's… |
|---|---|
| Walked a card to the Server | An **HTTP request** |
| Got an answer back | An **HTTP response** |
| Shouted "POST / PUT" | The **HTTP verb** |
| The Server's clipboard | The **HOUSES dict** in `houses.py` |
| The Router | Your camp **router** (and TCP/IP underneath) |
| "Lost" after missing ticks | The **watchdog** in `app.py` |
| The whole alarm chaos | `report_motion` → keepalive → buzzer |

Closing line: *"Everything you just did with your bodies, you'll now make computers do — about a thousand times per second. Let's open PyCharm."*

---

## Do we need prizes?

**Short answer: no — and competitive prizes would actually work against you here.** This game is *cooperative*, not a contest. The whole neighborhood wins or loses together (did the alarm fire and get disarmed in time?). A "winner takes the candy" twist would break that.

For 14-year-olds, **status and humor beat stuff**. What lands:

- **Silly fake-serious titles** awarded at the debrief (free, and they remember them all week):
  - 🏆 *Most Reliable House* — the one camper who never missed a keepalive.
  - 🦠 *Patient Zero* — whoever triggered the alarm.
  - 👹 *Packet Gremlin* — the TA, for dropping packets.
  - 🎖 *"I Survived the TCP/IP Transition"* — everyone (a callback to the [internet history doc](background/how_the_internet_works.md) — real engineers wore these buttons in 1983).
- **A shared treat** *after* the alarm round (a bowl of candy passed around) — fits the cooperative framing because everyone gets it, not just a "winner".

**Skip:** medals, points leaderboards, "first team to finish" races. They turn an ice-breaker (whose job is to make kids comfortable *together*) into a competition that leaves someone feeling slow on day one.

---

## What does "success" look like?

Success is **not** a score. The game worked if, by the end, you can tick these:

**Social (the real point of an ice-breaker):**
- ✅ Every camper spoke out loud at least once (the unique_id intro guarantees this).
- ✅ Kids learned a few names and laughed together.
- ✅ The shy ones were *carried by the activity* — they had a clear thing to do (keepalive, buzz) without being put on the spot.

**Conceptual (bonus — it pre-teaches Day 1):**
- ✅ A camper can answer "what's a request? what's a response?" in their own words.
- ✅ They can explain why a house got marked **Lost** (it stopped sending keepalives).
- ✅ They remember the alarm chain: *one armed house sees motion → tells the hub → hub tells all armed houses → everyone buzzes.*

**Energy:**
- ✅ The room is louder and looser than when you started.
- ✅ When you say "now let's make the computers do this", they're curious, not groaning.

**Quick 30-second check** at the debrief — ask the room (not individuals):
1. "If your house stops waving at me every TICK, what happens?" → *"You mark us Lost!"*
2. "When I clicked toggle, why didn't your LED change instantly?" → *"We had to wait for the next keepalive."*
3. "Who buzzes when one armed house sees motion?" → *"All the armed houses!"*

If those three answers come back fast, the game did its job — the protocol is already in their heads before they write a line of code.

> **You don't pass or fail this game.** If it was loud, everyone moved, and those three questions land — it's a win. If a round flops, just narrate louder and move to the alarm; the alarm round saves everything.

---

## Counsellor notes

- **Prep:** 2 minutes — just cards and pens. Pre-write role labels if you like.
- **Small group (<8):** drop the Router (Houses talk straight to the Server) and skip the TCP twist.
- **Big group (>20):** add a second Router and a second Server desk; split into two "neighborhoods" that share one alarm — when one neighborhood's alarm fires, both go off (shows the hub is shared).
- **Low-energy group:** keep it seated — messages get passed hand-to-hand down a row instead of walking. Still works.
- **The TICK is your tempo control.** Speed it up to raise energy, slow it down to explain.
- **Let the alarm round be loud.** Then immediately channel that energy into "now let's make the machines do it" — straight into [day1.md](day1.md).

> Tie-in: the diagrams in [diagrams/](diagrams/README.md) are the *picture* of what they just *acted out*. Project [03_http_and_server.drawio](diagrams/03_http_and_server.drawio) right after the debrief and say "see — you were the arrows."
