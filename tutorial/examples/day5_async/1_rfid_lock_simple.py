"""BONUS - an RFID door lock, the elegant way (no hardware needed).

An RFID reader's whole job is tiny: when you tap a card, it hands you the
card's UID (a unique code, like "DE AD BE EF"). A lock just has to answer
one question: "is this card allowed?" -- and open or stay shut.

This file is that logic, with NO reader and NO WiFi, so you can run it
right now in Thonny (on the board OR on your laptop) and see it work.

  >>> This file will NOT read your card -- there is no reader in it at
  >>> all. The "taps" below are a hardcoded list of pretend UIDs.
  >>> rfid_hello.py is the file that talks to real MFRC522 hardware;
  >>> day5.md ("Bonus - Reading a real RFID card") explains how.

THE DESIGN
  * We keep an ALLOW-LIST: a set of UIDs that are allowed to open the door.
  * Tap a card -> if its UID is on the list, the door opens; if not, denied.
  * That's it. An allow-list is clean and easy to read.

  (The original hardware version checked whether the UID's bytes added up
   to a magic number. That works, but "is this UID on the allowed list?"
   is much clearer -- and you can enroll new cards without doing math.)

HOW TO USE
  1. Run it (F5). Watch a few pretend card taps get granted or denied.
  2. Scroll to YOUR TURN and add your own card, or an "admin" card that
     enrolls new cards on the fly.

Next file: 2_rfid_lock_async.py runs this same idea the async way, with a
heartbeat LED and a simulated reader -- the real day-5 async showcase.
"""


class RfidLock:
    """A door lock driven by card UIDs. Pure logic -- no hardware."""

    def __init__(self, allowed):
        self.allowed = set(allowed)   # UIDs that may open the door
        self.locked = True            # start locked
        self.last_uid = None          # the most recent card we saw

    def tap(self, uid):
        """A card was tapped. Return (opened, message)."""
        self.last_uid = uid
        if uid in self.allowed:
            self.locked = False
            return True, "GRANTED - welcome"
        else:
            self.locked = True
            return False, "DENIED - unknown card"

    def enroll(self, uid):
        """Add a new card to the allow-list."""
        self.allowed.add(uid)

    def relock(self):
        """Shut the door again (e.g. after someone walks through)."""
        self.locked = True

    def status(self):
        return "OPEN" if not self.locked else "LOCKED"


def main():
    # Two cards are allowed. (These UIDs are just examples -- a real reader
    # gives you the card's actual code.)
    lock = RfidLock(allowed=["DE AD BE EF", "12 34 56 78"])

    # A pretend sequence of taps at the door.
    taps = [
        "DE AD BE EF",   # allowed -> opens
        "99 99 99 99",   # stranger -> denied
        "12 34 56 78",   # allowed -> opens
    ]

    print("Door starts:", lock.status())
    print("-" * 40)
    for uid in taps:
        opened, message = lock.tap(uid)
        icon = "[OPEN] " if opened else "[LOCK] "
        print(icon, "card", uid, "->", message)
        print("        door is now:", lock.status())
        lock.relock()   # door swings shut again, ready for the next person
    print("-" * 40)
    print("Done.")


# ============================================================
# YOUR TURN
# ------------------------------------------------------------
# 1) Add YOUR card: put a new UID in the allowed=[...] list, then add it to
#    `taps` and watch it get in.
#
# 2) An ADMIN card: pick one UID to be the "master." If it's tapped, the
#    NEXT card tapped gets enrolled. Sketch:
#
#       ADMIN = "AD 00 AD 00"
#       enrolling = False
#       for uid in taps:
#           if uid == ADMIN:
#               enrolling = True
#               print("admin card: tap a new card to enroll it")
#               continue
#           if enrolling:
#               lock.enroll(uid)
#               print("enrolled", uid)
#               enrolling = False
#               continue
#           opened, message = lock.tap(uid)
#           ...
#
# 3) Auto-relock after a delay instead of every tap (see the async file for
#    how to wait without freezing everything).
# ============================================================

main()
