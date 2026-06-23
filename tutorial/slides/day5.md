---
marp: true
theme: default
paginate: true
size: 16:9
---

<!-- _class: lead -->

# Day 5
## Async + Final Project

Same code, two shapes. Then build your own.

---

## What you'll have at lunch

- Both `app_sync.py` and `app_async.py` working
- A **final project** of your choice, demo'd to the room

---

## The big idea today

Same task. Two solutions.

| Sync | Async |
|---|---|
| One loop checks everything | Multiple tasks check independently |
| Easy to read top-to-bottom | Each task has its own "clock" |
| Slow call **freezes** the loop | Slow call **pauses just that task** |
| Default for beginners | Better when many things happen |

---

## What `await` does

**Sync:**
```python
time.sleep(1)        # CPU does NOTHING for 1 second
```

**Async:**
```python
await asyncio.sleep(1)   # "Wake me in 1 sec — others go meanwhile"
```

`await` is "I'll be busy — run something else".

---

## Today's milestones

- ✅ **5.1** `USE_ASYNC=True` works identically
- ✅ **5.2** Your final project runs end-to-end
- ✅ **5.3** Demo for 2 minutes

---

## Final project — pick ONE

| Option | Difficulty | What |
|---|:---:|---|
| **A** Doorbell | Medium | Cross-house LED flash |
| **B** Fan party | Easy | Reverse direction every press |
| **C** Stats page | Medium | New web page with counts |
| **D** Soft alarm | Hard | Buzzer escalates over time |
| **E** Morse chat | Hard (paired) | Long-press → flash partner |

Or invent your own (run it past staff first).

---

## Demo time at the end

Each pair: 2 minutes.

- 60 sec: show it working
- 30 sec: explain what surprised you
- 30 sec: questions

Cheering allowed. **Failure is normal** — show your previous milestone.

---

## Where to go after camp

- **Frontend:** rebuild the dashboard with React or HTMX
- **Real-time:** WebSockets/MQTT instead of polling
- **Persistence:** SQLite for state across restarts
- **Security:** API tokens
- **Hardware:** Raspberry Pi Pico W, more sensors

You learned a real distributed system this week.

---

<!-- _class: lead -->

# Open `tutorial/day5.md`
# Make something we'll remember.
