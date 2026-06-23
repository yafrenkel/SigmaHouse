# Counsellor's Guide — Day 3: WiFi + Talking to the Hub

**Lab time:** ~2 hours. **Hands-on:** ~110 min.

This is the day with the most things that can go wrong. Half the troubleshooting on Days 4–5 traces back to a Day 3 misconfiguration. Get every team's house steadily showing in the dashboard before letting anyone leave.

## Pacing

| Min | Activity | Watch out for |
|---:|---|---|
| 0–10 | Opener slide. Write hub URL on whiteboard. | Different IP than yesterday (laptop got new DHCP lease). |
| 10–20 | Verify hub reachable from each laptop browser | Wrong WiFi (laptop on hotel WiFi instead of camp router). |
| 20–35 | Connect ESP32 to WiFi at the REPL | Wrong SSID/password. SSID with non-ASCII chars. |
| 35–55 | First HTTP request from board (`urequests`) | Forgetting `r.close()`. |
| 55–70 | Configure `secrets.py` | Saving to PC instead of board. Editing `secrets_example.py` and never copying it. |
| 70–95 | Upload all firmware files, hit RESET | Forgetting `devices/` folder. Old `main.py` still on the board. |
| 95–110 | Round-trip test: dashboard ↔ board | All of Day 1's possible misconfigurations now matter. |
| 110–120 | Demo + stretch | — |

## Where they'll get stuck

1. **WiFi connect blocks forever** — wrong password, SSID with a typo, or the camp router has client isolation enabled (wireless devices can't see each other). Symptom: `wlan.isconnected()` returns False after 30 seconds. Test: from the laptop, can you ping `192.168.1.107` (their board's IP) once it does connect? If not, AP isolation is the problem and you need router-side help.

2. **WiFi connects but `urequests.get` hangs** — laptop firewall blocking inbound 8080. Symptom: from the board, `urequests.get(hub_url)` blocks for ~30 sec then errors. From the LAPTOP itself, `curl localhost:8080/api/houses` works fine. Open inbound 8080 on Windows Firewall.

3. **Wrong hub URL in `secrets.py`** — leftover from yesterday or a typo. Common errors: missing port (`http://192.168.1.42` not `:8080`), wrong protocol (`https://`), trailing slash (technically OK but worth checking).

4. **`secrets.py` is on PC, not on board** — they edited it in Thonny but it shows `<computer>`. Symptom: board boots, but `from secrets import ...` fails with ImportError. Fix: Save as → MicroPython device → secrets.py.

5. **They edited `secrets_example.py` and never copied it** — they have valid creds but the import in `config.py` still says `from secrets import ...`. Either rename `secrets_example.py` → `secrets.py` (delete the example), or copy it. Just one file should exist on the board.

6. **`devices/` folder missing on board** — uploaded all the loose files but forgot the folder. Symptom: `ImportError: no module named 'devices'`. Fix: in Thonny, right-click in board pane → New directory → "devices". Then upload all device files INTO that folder.

7. **Board memory full** — they uploaded everything multiple times, or have leftover `app_org.py` from yesterday. Fix: remove old files; ESP32 has ~2 MB free, plenty if you don't hoard.

8. **Sockets leaking → board reboots** — a student wrote a test that does `urequests.get(...)` in a loop without `.close()`. After ~10 calls, board crashes. Hint: "ALWAYS close. Use `try/finally`."

9. **Two boards register the same `unique_id`** — a student copy-pasted code with a hardcoded uid. Symptom: only one row in the dashboard, devices fight each other. Fix: use `unique_id()` from machine module.

## Ready-to-paste hints

**Hint H1** — `wlan.isconnected()` won't return True:
> Try: `print(wlan.scan())` first. If your SSID isn't in the list, the board literally can't hear it. If it is, double-check the password — copy-paste from a known-good source.

**Hint H2** — HTTP call hangs:
> First, sanity check from the laptop: `curl http://<laptop-ip>:8080/api/houses` (use the laptop's actual IP, not localhost). If THAT fails, fix the firewall first. If it works, the board is on the wrong network.

**Hint H3** — `ImportError: no module named 'secrets'`:
> Look at your board's file list (right pane in Thonny). Do you see `secrets.py`? If you see only `secrets_example.py`, rename it.

**Hint H4** — Their board shows in the dashboard but goes "Lost":
> Watch the Thonny shell while it's running. You should see no errors. If you see HTTP timeouts every second, the laptop firewall is rejecting their keepalives. (Or the laptop went to sleep.)

**Hint H5** — Round-trip works one direction but not the other:
> Direction "dashboard → board" failing: open Thonny shell, what do you see when you toggle from the browser? You should see something happen. If silent, the board's keepalive isn't returning state_update=True. (Did you DELETE and re-register the house? Old state can be stuck.)
> Direction "button → dashboard" failing: the button is firing but `push_state` isn't reaching the hub. Open the shell while pressing.

## What "done" looks like

- **Milestone 3.1** — `wlan.isconnected()` returns True; `wlan.ifconfig()[0]` is a 192.x.x.x address.
- **Milestone 3.2** — Their MAC-based unique_id appears in the dashboard. May go "Lost" if they don't keep keepaliving (that's fine, they're not running the full firmware yet).
- **Milestone 3.3** — Full firmware running. LCD says "Ready". Dashboard shows their house staying Active.
- **Milestone 3.4** — Toggle LED from dashboard → physical LED reacts. Press button B on board → dashboard reflects within 1 sec.

## Stretch supervision

- **Toggle the fan** — hand back the demo and have them try; the only catch is if their board sometimes resets when the fan spins (USB port too weak — see Day 2 notes).
- **Print keepalives** — useful debug skill. Show them how to add `print(resp)` and watch it stream.
- **Loop curl** — fun, has a small lesson: the LED can't keep up because the keepalive loop is 1/sec, so toggles faster than 1/sec get coalesced (only the latest wins). That's actually a bug feature worth noticing.

## Critical: stable WiFi for tomorrow

Before you let students leave for the day, every team's row should be steadily Active. Day 4 (PIR alarm) requires stable connections — if a board flickers Lost/Active, the alarm gets lost. Take 5 minutes at the end to verify.
