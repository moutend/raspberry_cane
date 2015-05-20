#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal
import time
import datetime
import threading
import RPi.GPIO as GPIO
from multiprocessing import Process

PULSE = 0.05
VIBE = 12
STEP = 0.05
__interval = 1.0
__timer = None

def cleanup_GPIO(signal, frame):
  global __timer
  __timer.cancel()
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

def shake():
  GPIO.output(VIBE, True)
  time.sleep(PULSE)
  GPIO.output(VIBE, False)
  return time.time()

def kick():
  global __timer
  global __interval

  __timer = threading.Timer(__interval, kick)
  __timer.start()
  shake()

if __name__ == '__main__':
  print "To control, hit the following key."
  print "=================================="
  print "Ctrl-C => Quit"
  print "k      => Slow down"
  print "j      => Speed up\n"

  signal.signal(signal.SIGINT, cleanup_GPIO)
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  GPIO.setwarnings(True)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(VIBE, GPIO.OUT)

  kick()
  while True:
    c = getKey()

    if c == 106 and __interval > 0.1:
      __interval -= 0.05

    if c == 107 and __interval < 1.0:
      __interval += 0.05

    print "interval: %s" % __interval
