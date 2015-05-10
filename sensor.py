#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import os
import sys
import signal
import math
import RPi.GPIO as GPIO
from multiprocessing import Process, Pipe

TRIG = 11
VIBE = 12
ECHO = 13

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(VIBE, GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

def cleanup_GPIO(signal, frame):
  GPIO.output(TRIG, GPIO.LOW)
  GPIO.output(TRIG, False)
  GPIO.output(VIBE, GPIO.LOW)
  GPIO.output(VIBE, False)
  GPIO.output(ECHO, GPIO.LOW)
  GPIO.output(ECHO, False)

  GPIO.cleanup()
  sys.exit(0)

def measure():
  GPIO.output(TRIG, GPIO.LOW)
  GPIO.output(TRIG, True)
  time.sleep(0.00001)
  GPIO.output(TRIG, False)

  limit_signal_off = 128
  limit_signal_on  = 6400
  signal_off = 0
  signal_on  = 0

  while not GPIO.input(ECHO):
    signal_off = time.time()
    limit_signal_off -= 1
    if limit_signal_off == 0: break
  if limit_signal_off == 0: return -1

  while GPIO.input(ECHO):
    signal_on = time.time()
    limit_signal_on -= 1
    if limit_signal_on == 0: break
  if limit_signal_on == 0: return -2

  distance = (signal_on - signal_off) * 17000
  if distance <= 400.0:
    return distance
  else:
    return -3

def vibrate(n):
  sec = float(n) / 1000
  while True:
    print "        %s" % sec
    GPIO.output(VIBE, GPIO.LOW)
    GPIO.output(VIBE, True)
    time.sleep(0.05)
    GPIO.output(VIBE, False)
    time.sleep(sec)

if __name__ == '__main__':
  signal.signal(signal.SIGINT, cleanup_GPIO)
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  d1 = 999
  j = 0
  pid = -1
  while True:
    d2 = int(measure())
    if d2 != 0:
      print d2
    if d2 != 0 and math.fabs(d1 - d2) > 10:
      print j, datetime.datetime.now(), d2
      d1 = d2
      if pid != -1:
        os.kill(pid, signal.SIGTERM)
      p = Process(target=vibrate, args=(d1 * 2,))
      p.start()
      pid = p.pid

    j += 1
    time.sleep(0.01)
