"""Day 2 - Read a button by POLLING, and see its big downside.

The CPU can only do ONE thing at a time. With polling, the main loop is
stuck babysitting the button: every other task has to wait its turn, and
any press that lands while the loop is busy doing work is MISSED entirely.

Watch the output. The loop is "busy" doing pretend work, one task at a
time. Press the button DURING a task and nothing happens -- the CPU
wasn't looking. Only a press that's still held at the exact poll moment
gets noticed. That's the whole problem, and why the next example
(3_button_irq.py) switches to interrupts.

Press Ctrl-C to stop.
"""

from machine import Pin
import time

button = Pin(26, Pin.IN, Pin.PULL_UP)


def do_work(name):
    # Pretend this is a real job: read a sensor, update the display, etc.
    # While we're in here, the button is NOT being watched at all.
    print(name, "... (busy - button ignored right now)")
    time.sleep(1)


while True:
    # The loop is fully occupied running tasks back-to-back.
    do_work("Task A")
    do_work("Task B")
    do_work("Task C")

    # The ONLY instant we glance at the button is right here, between
    # rounds of work. A press during the tasks above is already gone.
    if button.value() == 0:
        print(">>> Pressed! (you happened to hold it until the poll)")
    else:
        print("(polled the button - nothing / missed it)")
