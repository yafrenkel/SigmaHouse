# Glossary — every acronym in this camp, spelled out

Lost in alphabet soup? Every short form used anywhere in this tutorial is here, with what the letters stand for and a one-line plain-English meaning. Grouped by topic; skim the section you need.

> Tip for counsellors: keep this open on a second screen. When a camper asks "what does I2C even mean?", you've got the answer in one line.

---

## Networking & the internet

| Short form | Stands for | What it means (plainly) |
|---|---|---|
| **HTTP** | HyperText Transfer Protocol | The rules for asking a server for something and getting an answer. Our whole hub speaks HTTP. |
| **HTTPS** | HTTP Secure | HTTP with encryption (the padlock in your browser). We use plain HTTP at camp — it's a private offline network. |
| **TCP** | Transmission Control Protocol | The layer that makes delivery reliable — nothing lost, everything in order. HTTP rides on top of it. |
| **IP** | Internet Protocol | The addressing layer. Every device gets an **IP address** like `192.168.1.8`. |
| **TCP/IP** | TCP + IP together | The combined rule-set that the entire internet runs on, designed in 1974. |
| **UDP** | User Datagram Protocol | TCP's fast-but-unreliable sibling. Used by games and video calls, not by us. |
| **WiFi** | Wireless Fidelity* | Wireless networking over radio. How the ESP32 reaches the hub. (*Really just a brand name that stuck; treat it as "wireless networking".) |
| **LAN** | Local Area Network | A small network in one place — your camp router and everything on it. |
| **IP address** | (see IP) | A device's "phone number" on the network. `192.168.1.8`. |
| **port** | (not an acronym) | A number that picks *which program* on a machine. Our hub uses port **8080**. IP = building, port = apartment. |
| **DNS** | Domain Name System | The internet's phone book — turns `youtube.com` into an IP address. We skip it at camp and type raw IPs. |
| **DHCP** | Dynamic Host Configuration Protocol | How your router automatically hands out IP addresses to devices that join the WiFi. |
| **NAT** | Network Address Translation | The router's trick for sharing one public internet address among many private devices. |
| **SSID** | Service Set IDentifier | The *name* of a WiFi network — the thing you pick from the WiFi list. |
| **MAC address** | Media Access Control address | A permanent hardware ID burned into every network chip. Your ESP32's `unique_id` is its MAC. |
| **OSI** | Open Systems Interconnection | A 7-layer textbook model of networking. We use the simpler 4-layer TCP/IP view. |
| **SYN / ACK** | Synchronize / Acknowledge | The "hello / hello back" messages that open a TCP connection (the "3-way handshake"). |
| **CDN** | Content Delivery Network | Servers spread worldwide that deliver files fast. Mentioned as why draw.io's HTML export needs internet. |

---

## The Web & data formats

| Short form | Stands for | What it means (plainly) |
|---|---|---|
| **URL** | Uniform Resource Locator | A web address, like `http://192.168.1.8:8080/api/houses`. |
| **HTML** | HyperText Markup Language | The language web pages are written in. Our dashboard page is HTML. |
| **CSS** | Cascading Style Sheets | The language that styles a web page (colors, layout). Our `style.css`. |
| **JS** | JavaScript | The programming language that runs *inside* the browser. Our `dashboard.js` polls the hub. |
| **JSON** | JavaScript Object Notation | A text way to write data that looks like a Python dict: `{"led": {"active": true}}`. How the hub and ESP32 swap data. |
| **API** | Application Programming Interface | The set of "doors" (routes) a program offers for others to use. Our hub's API is its 9 routes. |
| **REST** | REpresentational State Transfer | A popular style of API using HTTP verbs (GET/POST/PUT/DELETE) on "resources" like `/houses`. Ours is RESTish. |
| **UID** | Unique IDentifier | A value that's different for every house. We use the ESP32's MAC address. |

---

## Hardware & electronics

| Short form | Stands for | What it means (plainly) |
|---|---|---|
| **ESP32** | (Espressif chip family) | The little WiFi-enabled microcontroller board that is each "smart house". |
| **MCU** | MicroController Unit | A tiny computer-on-a-chip (the ESP32 is one). Runs your code directly, no operating system needed. |
| **GPIO** | General-Purpose Input/Output | A pin you can control in code — read a button, or switch an LED. "GPIO 12" = pin number 12. |
| **PWM** | Pulse-Width Modulation | Switching a pin on/off very fast to fake "in-between" levels — used to set fan speed and buzzer tone. |
| **I2C** | Inter-Integrated Circuit | A 2-wire system for talking to chips like the LCD. Uses pins SCL (clock) + SDA (data). Say it "I-squared-C" or "I-two-C". |
| **IRQ** | Interrupt ReQuest | The hardware shouting "this pin just changed!" so your code reacts instantly instead of constantly checking. |
| **LED** | Light-Emitting Diode | The little light on GPIO 12. |
| **PIR** | Passive InfraRed (sensor) | The motion sensor — it sees body heat moving. On GPIO 13. |
| **LCD** | Liquid Crystal Display | The 2-line text screen. Talks over I2C. |
| **RFID** | Radio-Frequency IDentification | Tap-card tech (like a bus pass). In the original project but **removed** from ours to keep it simple. |
| **USB** | Universal Serial Bus | The cable connecting the ESP32 to your laptop (power + data). |
| **COM port** | Communication port | Windows' name for the USB serial connection, like `COM3`. Thonny needs to know which one. |
| **SCL / SDA** | Serial CLock / Serial DAta | The two I2C wires. On our board SCL=GPIO 22, SDA=GPIO 21. |
| **RAM** | Random Access Memory | Short-term memory. The ESP32 has very little (~520 KB), which is why we always `close()` HTTP responses. |

---

## Software & tools

| Short form | Stands for | What it means (plainly) |
|---|---|---|
| **REPL** | Read-Eval-Print Loop | The interactive `>>>` prompt where you type one line and see the result instantly. Thonny's Shell is a REPL on the ESP32. |
| **IDE** | Integrated Development Environment | An app for writing/running code. PyCharm and Thonny are IDEs. |
| **CLI** | Command-Line Interface | Typing commands in a terminal (like `curl ...`) instead of clicking buttons. |
| **OS** | Operating System | The software running your computer (Windows, macOS). The ESP32 has *no* OS — your code is in charge. |
| **pip** | Pip Installs Packages | Python's tool for installing libraries, like Flask. (Yes, the name is a joke that refers to itself.) |
| **venv** | Virtual ENVironment | A private, isolated set of Python libraries for one project, so projects don't clash. |
| **PDF / PNG / SVG** | Portable Document Format / Portable Network Graphics / Scalable Vector Graphics | File types for the diagrams. PDF = print, PNG = pixel image, SVG = scalable image. |

---

## History (from the internet deep-dive)

| Short form | Stands for | What it means (plainly) |
|---|---|---|
| **ARPANET** | Advanced Research Projects Agency NETwork | The 1969 US military research network — the internet's grandparent. |
| **CERN** | Conseil Européen pour la Recherche Nucléaire | The European physics lab where Tim Berners-Lee invented the Web in 1989-91. (French acronym — the English is "European Council for Nuclear Research".) |

---

## The four HTTP verbs (not acronyms, but always worth repeating)

| Verb | Means | Example in our project |
|---|---|---|
| **GET** | "give me" | `GET /api/houses` — list all houses |
| **POST** | "make a new thing" | `POST /api/houses` — register a house |
| **PUT** | "replace / update this" | `PUT .../keepalive` — heartbeat |
| **DELETE** | "remove this" | `DELETE /api/houses/<uid>` — unregister |

> **Idempotent** = doing it once or ten times leaves the same result. `GET`, `PUT`, `DELETE` are idempotent (safe to retry on flaky WiFi); `POST` is **not** (a retried `POST /toggle` flips the LED back). That's why the safe-to-repeat *keepalive* is a `PUT` and the action-with-side-effects *toggle* is a `POST`. (Full explanation: `day1.md`, Part 2.)

---

## Common status codes (the number the server replies with)

| Code | Means |
|---|---|
| **200 OK** | It worked. |
| **201 Created** | Made a new thing (a house registered). |
| **400 Bad Request** | You sent something malformed (missing data). |
| **404 Not Found** | That thing doesn't exist (unknown house). |

---

*Still see a short form that isn't here? Tell a counsellor — it should get added. A good glossary is never quite finished.*
