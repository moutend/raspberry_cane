#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal
import time
import RPi.GPIO as GPIO
from multiprocessing import Process

PULSE = 0.05
VIBE = 12
STEP = 0.05

def cleanup_GPIO(signal, frame):
  print "\nDO:   cleanup_GPIO()"
  GPIO.output(VIBE, GPIO.LOW)
  GPIO.output(VIBE, False)
  GPIO.cleanup()
  print "DONE: cleanup_GPIO()"

  exit(0)

def getKey():
  import sys, tty, termios
  old_settings = termios.tcgetattr(0)
  new_settings = old_settings[:]
  new_settings[3] &= ~termios.ICANON
  try:
    termios.tcsetattr(0, termios.TCSANOW, new_settings)
    ch = sys.stdin.read(1)
  finally:
   termios.tcsetattr(0, termios.TCSANOW, old_settings)
  return ord(ch)

def vibrate(wait, interval):
  GPIO.output(VIBE, GPIO.LOW)
  GPIO.output(VIBE, False)

  time.sleep(wait)
  while True:
    GPIO.output(VIBE, True)
    time.sleep(PULSE)
    GPIO.output(VIBE, False)
    time.sleep(interval)

if __name__ == '__main__':
  print "To control, hit the following key."
  print "=================================="
  print "Ctrl-C => Quit"
  print "k      => Slow down"
  print "j      => Speed up"

  signal.signal(signal.SIGINT, cleanup_GPIO)
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  GPIO.setwarnings(True)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(VIBE, GPIO.OUT)

  interval = 1.0 - PULSE

  p = Process(target=vibrate, args=(0, interval,))
  p.daemon = True
  p.start()
  pid = p.pid

  while True:
    c = getKey()

    if c == 106 and interval >= 0.1:
      interval -= STEP
    elif c == 107 and interval < 1.0 - PULSE:
      interval += STEP
    else:
      continue

    os.kill(pid, signal.SIGTERM)

    p = Process(target=vibrate, args=(0, interval,))
    p.daemon = True
    p.start()
    pid = p.pid

    print "\ninterval: %s" % interval
