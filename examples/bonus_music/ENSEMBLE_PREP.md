# TODO (before the lab): have 4 boards pre-flashed with voices 1–4

For the 4-board Frère Jacques round, prep 4 boards ahead of time so campers just press GO.

On **each** of the 4 boards (Thonny → upload to the board):
- [ ] Upload `orchestra_ensemble.py`
- [ ] Upload `melodies_options.py`
- [ ] Confirm the shared settings at the top of `orchestra_ensemble.py`:
      `SONG = songs.FRERE_JACQUES`, `ARRANGEMENT = "round"`, `ROUND_DELAY = 8`, `TEMPO_MS = 400`

Then set **one different line per board** and label the board:
- [ ] Board 1 → `VOICE = 1`
- [ ] Board 2 → `VOICE = 2`
- [ ] Board 3 → `VOICE = 3`
- [ ] Board 4 → `VOICE = 4`

Quick check: run one board — it should print `I am VOICE <n> ( round )` and play only when button A is pressed.
(3 boards is fine too — just skip Board 4.)
