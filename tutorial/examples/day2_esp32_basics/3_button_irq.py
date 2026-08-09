"""Day 2 - Read a button with an INTERRUPT (IRQ), and do real work too.

The hardware watches the button for us. The MOMENT it's pressed, the CPU
drops what it's doing, runs our handler, then goes right back to where it
was. That means the main loop is free to run any other tasks, functions,
or commands you like -- and the button is STILL caught instantly, even in
the middle of a task.

Compare with 2_button_poll.py: there the button is only seen if you press
at the exact instant it polls, so presses during work are lost. Here, the
tasks run freely AND no press is ever missed.

RULE OF INTERRUPTS: keep the handler tiny. We print here just for the
demo, but in real code the handler should only set a flag (see
4_button_led.py). You may occasionally get 2-3 prints from contact
"bounce"; that's real, and we fix it with debounce in the full firmware's
button.py.

Press Ctrl-C to stop.
"""

from machine import Pin
import time

button = Pin(26, Pin.IN, Pin.PULL_UP)


def on_press(pin):
    # Fires the instant the pin goes 1 -> 0, no matter what the main loop
    # is doing. The CPU jumps here mid-task, then returns automatically.
    print(">>> Button pressed! (interrupted mid-task, handled instantly)")


button.irq(trigger=Pin.IRQ_FALLING, handler=on_press)


def do_work(name):
    # Real jobs run freely here -- the button no longer needs babysitting,
    # so a press during any of these is still caught right away.
    print(name, "... (working - press anytime, it'll still register)")
    time.sleep(1)


# The main loop just does its own thing. The button takes care of itself
# in the background via the interrupt above.
while True:
    do_work("Task A")
    do_work("Task B")
    do_work("Task C")
