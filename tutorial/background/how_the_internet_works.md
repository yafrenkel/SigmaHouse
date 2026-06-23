# How the Internet Actually Works (optional deep-dive)

> **Who's this for?** Campers who finish early and want to know what's *really* happening when their ESP32 talks to the hub. Not required for the labs — but if you've ever wondered "what is the internet, physically?", read on. ~20 minutes.

You can read this on Day 1 (before HTTP), or Day 3 (after you've seen WiFi work). Either order is fine.

> 🔤 Every acronym below (HTTP, TCP, IP, DNS, NAT, …) is spelled out in the **[glossary](../glossary.md)** if you want the quick version.

---

## Part 1 — A very short history (so the acronyms make sense)

Every weird name in networking is a fossil from some decade. Knowing the story makes them stop being scary.

- **1969 — ARPANET.** The US military funded a network connecting four university computers so researchers could share machines. The first message ever sent was meant to be "LOGIN" — the system crashed after "LO". So the internet's first word was literally *"lo"*. 🎤
- **1974 — TCP/IP invented.** Vint Cerf and Bob Kahn designed a set of rules for *any* network to talk to *any other* network — an "inter-network". That's where the word **internet** comes from. Their rules are still what your ESP32 uses today, 50 years later.
- **1983 — the switch.** On 1 January 1983, ARPANET switched to TCP/IP overnight. People wore buttons that said "I survived the TCP/IP transition." (Peak nerd.)
- **1989-91 — the Web.** Tim Berners-Lee, at CERN, invented **HTTP**, **HTML**, and the **URL** so physicists could link documents. The Web is *not* the same thing as the internet — the Web is one thing that runs *on top of* the internet (like your smart-house API is one thing running on top of the Web's plumbing).
- **1990s-now — everything else.*[glossary.md](../glossary.md)* Email, video, games, your fridge. All of it rides on the same TCP/IP rules from 1974.

**Key idea:** the internet is not one machine or one company. It's an agreement — a set of rules (*protocols*) that millions of independent machines follow so they can pass messages to each other.

---

## Part 2 — Layers: envelopes inside envelopes

The single most important idea in networking: **you don't send one big thing, you wrap a small thing in bigger and bigger envelopes.** Each layer only worries about its own job.

When your ESP32 sends `POST /api/houses` to the hub, here's what's really wrapped around it:

```
┌─────────────────────────────────────────────┐
│ ETHERNET / WiFi frame  (layer 1-2)            │  "deliver to the machine
│  ┌──────────────────────────────────────────┐│   at this WiFi address"
│  │ IP packet           (layer 3)             ││  "deliver to IP 192.168.1.8"
│  │  ┌───────────────────────────────────────┐││
│  │  │ TCP segment      (layer 4)            │││  "to port 8080, in order,
│  │  │  ┌────────────────────────────────────┐│││   nothing lost"
│  │  │  │ HTTP message  (layer 7)           ││││  "POST /api/houses
│  │  │  │  POST /api/houses                 ││││   {unique_id: ...}"
│  │  │  │  {"unique_id": "FAKE001"}         ││││
│  │  │  └────────────────────────────────────┘│││
│  │  └───────────────────────────────────────┘││
│  └──────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

Think of mailing a letter:
- **HTTP** = the letter you wrote (the actual message).
- **TCP** = putting it in an envelope, numbering the pages so they arrive in order, and demanding a delivery receipt.
- **IP** = writing the street address on the envelope.
- **WiFi/Ethernet** = the actual mail truck (radio waves, or a copper cable).

Each layer is sealed: the mail truck doesn't read your letter, and your letter doesn't care whether it travels by truck or plane. This is why the same HTTP works over WiFi, fibre, or 5G — only the bottom layer changes.

---

## Part 3 — IP addresses and ports (buildings and apartments)

- An **IP address** identifies a *machine* on a network. Your laptop is `192.168.1.8`. Your ESP32 got something like `192.168.1.107`.
- A **port** identifies *which program* on that machine. Your hub listens on **port 8080**. A web browser usually talks to port 80 or 443. Email uses 25 / 587. Minecraft servers default to 25565.

Analogy: the **IP address is the building**, the **port is the apartment number**. `192.168.1.8:8080` means "apartment 8080 in building 192.168.1.8." That's exactly why your `HUB_URL` has both: `http://192.168.1.8:8080`.

### Why your camp addresses all start with 192.168

`192.168.x.x` is a **private** address range — reserved for local networks. They're not reachable from the public internet; your router hands them out to everything on your WiFi. (Other private ranges: `10.x.x.x` and `172.16-31.x.x`.) That's perfect for camp: the whole smart-house network lives inside your router, no internet needed.

The router itself has TWO addresses: a private one facing your devices (often `192.168.1.1`) and a public one facing the internet. It translates between them — a trick called **NAT** (Network Address Translation). At camp you only ever use the private side.

---

## Part 4 — TCP: the part that makes it reliable

WiFi and IP, by themselves, are *unreliable* — packets can arrive out of order, get duplicated, or vanish. **TCP** is the layer that fixes that. It:

1. **Establishes a connection** with a 3-step handshake (the famous "SYN / SYN-ACK / ACK" — like "Can you hear me?" / "Yes, can you hear me?" / "Yes!").
2. **Numbers every chunk** so the receiver can reassemble them in order.
3. **Re-sends anything lost**, waiting for an acknowledgement of each piece.

You never write this code — `urequests` on the ESP32 and Flask on the laptop both sit on top of TCP and get all of it for free. But it's why your `urequests.get(...)` either returns the *whole* correct answer or raises an error — never half a JSON.

> **Nerd note:** there's a sibling protocol, **UDP**, that skips all the reliability for speed. Video calls and games often use UDP — a dropped frame is better than a laggy one. HTTP uses TCP because for an API you'd rather be correct than fast.

---

## Part 5 — DNS: the internet's phone book

When you type `youtube.com`, your machine first asks a **DNS** server "what's the IP address for youtube.com?" and gets back something like `142.250.74.46`. DNS turns human names into machine addresses.

**At camp you skip DNS entirely** — you type the laptop's IP (`192.168.1.8`) directly, because there's no DNS server on your little offline network. That's also why the tutorial has you run `ipconfig` to find the raw IP: you're being your own phone book.

---

## Part 6 — HTTP: just text, on top of all that

Here's the punchline that surprises people: **HTTP is just text.** The request your browser sends is literally these characters, sent over the TCP connection:

```
POST /api/houses HTTP/1.1
Host: 192.168.1.8:8080
Content-Type: application/json
Content-Length: 48

{"unique_id": "FAKE001", "ip_address": "..."}
```

A blank line separates the **headers** from the **body**. The server reads this text, does its thing, and sends text back:

```
HTTP/1.1 201 Created
Content-Type: application/json

{"ok": true, "unique_id": "FAKE001"}
```

That's it. That's the Web. You could type these by hand into a raw TCP connection (with a tool like `telnet` or `nc`) and a server would answer. `curl`, your browser, and `urequests` are just conveniences that format the text for you.

> **Try it (needs internet):** `curl -v http://example.com` and read the lines starting with `>` (what you sent) and `<` (what came back). Those are the raw HTTP headers.

---

## Part 7 — The whole journey, for one button click

You click **LED → off** in the dashboard. Here's the full stack of what happens, end to end:

1. **Browser** builds an HTTP request: `POST /api/houses/<uid>/toggle/led`.
2. It's wrapped in TCP (envelope + receipt), then IP (address `192.168.1.8`), then WiFi (radio waves).
3. Radio waves hit your **router**, which forwards the IP packet to the laptop.
4. The laptop's OS sees port **8080**, hands the bytes to **Flask**.
5. Flask's loop (the one from diagram 03) **matches the route** and runs `toggle()`, which flips a value in the `HOUSES` dict.
6. Flask sends back `200 OK` + JSON — same journey in reverse.
7. Meanwhile your **ESP32** is doing its own `PUT /keepalive` every second. Its next keepalive gets `{"state_update": true}`.
8. ESP32 sends `GET /state`, receives `{"led": {"active": false}}`, and calls `led.off()`.
9. Photons stop coming out of the LED. 💡→⚫

Every arrow in that list is HTTP-over-TCP-over-IP-over-WiFi. Same four envelopes, every time.

---

## Where this connects to the rest of the camp

- The **request/response + status codes** here are drawn in [diagrams/03_http_and_server.drawio](../diagrams/03_http_and_server.drawio).
- The **hub's loop** (listen → match → run → respond) is diagram 03's bottom section, and the real code is `implementation/iot_hub/app.py`.
- The **ESP32's HTTP calls** are all in `implementation/smart_house/hub_client.py`.

## Five things to remember

1. The internet is an **agreement** (protocols), not a machine.
2. Messages are **wrapped in layers** — each layer has one job.
3. **IP = building, port = apartment.** `192.168.1.8:8080`.
4. **TCP** makes delivery reliable so you don't have to.
5. **HTTP is just text** riding on top of all of it.

---

*Want to go further? Look up: the OSI 7-layer model, the TCP 3-way handshake, what a MAC address is (hint: your ESP32's `unique_id` is one), and why HTTPS adds an 'S'.*
