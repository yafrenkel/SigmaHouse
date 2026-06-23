# Opening Slides

One ~5-minute opening slide deck per day, in [Marp](https://marp.app/) markdown.

| File | Day |
|---|---|
| [day1.md](day1.md) | The Hub |
| [day2.md](day2.md) | ESP32 First Steps |
| [day3.md](day3.md) | WiFi + Hub |
| [day4.md](day4.md) | Sensors + Alarm |
| [day5.md](day5.md) | Async + Final |

Each deck is 6–8 slides. They're meant to be projected for the first 5–10 minutes of each session — campers don't need a copy.

## Render to PDF (one-time setup, before camp, ONLINE)

Marp CLI is a single Node.js binary. Easiest setup:

### Option A — VS Code extension (no terminal)

1. Install **VS Code** if not already.
2. Install the **Marp for VS Code** extension (search "Marp" in extensions).
3. Open any `dayN.md` from this folder.
4. Click the Marp icon in the top-right of the editor → **Export slide deck…** → PDF.

### Option B — CLI (scriptable)

```bash
# One time, online:
npm install -g @marp-team/marp-cli

# Per file:
marp --pdf day1.md
marp --pdf day2.md
# ...
```

This produces `day1.pdf`, `day2.pdf`, etc.

### Option C — Pre-render all five at once

```bash
cd claude/tutorial/slides
for f in day*.md; do
  marp --pdf "$f"
done
```

## Render at camp (offline)

Once Marp CLI is installed, it works offline. The `--pdf` flag uses a bundled Chromium for rendering — no internet needed at render time.

If you want to skip Marp entirely, you can:
- Open each `.md` in any markdown viewer (the slides degrade gracefully — `---` becomes horizontal rules).
- Project the markdown source directly. It's readable.

## Customizing

Each deck starts with a Marp front-matter block:
```markdown
---
marp: true
theme: default
paginate: true
---
```

To change theme: `theme: gaia` for a softer look, or `theme: uncover` for centered. To add your camp logo, drop a PNG in this folder and use `![bg](logo.png)` on the title slide.

Slide breaks are `---` on its own line.

## Tip for live presenting

Marp PDFs page-flip with arrow keys in any PDF reader. Acrobat Reader's Ctrl+L = full screen. Chrome's PDF viewer works too.
