#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import os
import sys
import signal
import math
import threading
import RPi.GPIO as GPIO
from multiprocessing import Process, Pipe

VIBE    = 12

def cleanup_GPIO(signal, frame):
  GPIO.output(VIBE, GPIO.LOW)
  GPIO.output(VIBE, False)
  GPIO.cleanup()
  sys.exit(0)

def vibrate(sec):
  GPIO.output(VIBE, GPIO.LOW)
  GPIO.output(VIBE, True)
  time.sleep(sec)
  GPIO.output(VIBE, False)
  return sec

def f(sec):
  print datetime.datetime.now(), vibrate(0.0628)
  t2 = time.time() + sec
  t = threading.Timer(sec, f, args=[sec])
  t.start()
  while time.time() < t2:
    print "tid %s" % t
    time.sleep(0.125)

if __name__ == '__main__':
  signal.signal(signal.SIGINT, cleanup_GPIO)
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  GPIO.setwarnings(True)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(VIBE, GPIO.OUT)

  f(1.0)
