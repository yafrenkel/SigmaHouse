---
marp: true
theme: default
paginate: true
size: 16:9
---

<!-- _class: lead -->

# Day 1
## The Hub

A web server you control with `curl`.

---

## What you'll have at lunch

- Flask running on your laptop at `http://localhost:8080`
- A dashboard listing connected houses
- One new endpoint **YOU wrote**: `/api/disarm_all`

---

## The big idea today

A **server** sits and waits.
**Clients** ask it questions and tell it things.

Every question/answer is one **HTTP request**.

```
client  ────GET /api/houses──▶  server
client  ◀────[house1, house2]──  server
```

---

## Vocabulary you'll meet

| Word | Meaning |
|---|---|
| **HTTP** | The conversation rules between browsers/apps and servers |
| **GET** | "Give me…" |
| **POST** | "Create a new…" |
| **PUT** | "Replace this…" |
| **DELETE** | "Remove this…" |
| **JSON** | A way to write Python dicts as text |
| **endpoint / route** | One specific URL the server handles |

---

## Today's milestones

- ✅ **1.1** Dashboard loads in browser
- ✅ **1.2** `curl POST /api/disarm_all` works

---

## Two tools you'll use

**PyCharm** — write and run Python code.
**curl** — send HTTP requests from the terminal.

```bash
curl http://localhost:8080/api/houses
```

(Use PyCharm's **Terminal** tab — Git Bash, handles JSON quoting nicely.)

---

## When you get stuck

1. Read the error. Out loud.
2. Did you save? Did you restart the hub?
3. Ask a counsellor — but bring the error message with you.

> "I don't know" is fine. **"It's broken"** is not — show me what you tried.

---

<!-- _class: lead -->

# Open `tutorial/day1.md`
# Let's go.
