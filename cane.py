#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal
import time
import datetime
import threading
import RPi.GPIO as GPIO

BUFFER_SIZE = 24
MAX_SIGNAL_OFF = 128
MAX_SIGNAL_ON = 4096
MAX_DISTANCE = 400.0
PULSE = 0.05
TRIG = 11
ECHO = 13
VIBE = 12
__interval = 1.0
__timer = None

class Cue:
  def __init__(self, size):
    self.size = size
    self.list = [0]

  def push(self, item):
    if len(self.list) >= self.size:
      self.list.pop(0)
    self.list.append(item)

  def clear(self):
    self.list = [0]

  def mean(self):
    return int(reduce(lambda x, y: x + y, self.list) / len(self.list))

  def getD(self):
    if len(self.list) < self.size or self.list[0] == 0:
      return -1
    d1 = self.list[0]
    for i in range(len(self.list) - 1):
      d2 = self.list[i] - self.list[i + 1]
      if d2 < 0:
        return -2
    return d1 - self.list[4]

def cleanup(signal, frame):
  global __timer
  __timer.cancel()
  print "\nDO:   cleanup GPIO()"
  GPIO.output(VIBE, GPIO.LOW)
  GPIO.output(VIBE, False)
  GPIO.cleanup()
  print "DONE: cleanup GPIO()"

  exit(0)

def shake():
  GPIO.output(VIBE, True)
  time.sleep(PULSE)
  GPIO.output(VIBE, False)
  return time.time()

def desc(sec):
  if sec < 0.75:
    return
  interval = sec / 4
  t2 = time.time() + sec
  while time.time() < t2:
    shake()
    time.sleep(interval)
    interval /= 1.375

def kick():
  global __timer
  global __interval

  __timer = threading.Timer(__interval, kick)
  __timer.start()

  shake()

  q = Cue(5)
  t2 = time.time() + __interval
  while time.time() < t2:
    q.push(__interval)
    if q.getD() >= 0.4:
      desc(t2 - time.time())
      break
    time.sleep(0.05)

def measure():
  GPIO.output(TRIG, GPIO.LOW)
  GPIO.output(TRIG, True)
  time.sleep(0.00001)
  GPIO.output(TRIG, False)

  limit_signal_off = MAX_SIGNAL_OFF
  limit_signal_on  = MAX_SIGNAL_ON
  signal_off = 0
  signal_on  = 0

  while not GPIO.input(ECHO):
    signal_off = time.time()
    limit_signal_off -= 1
    if limit_signal_off == 0:
      return -1

  while GPIO.input(ECHO):
    signal_on = time.time()
    limit_signal_on -= 1
    if limit_signal_on == 0:
      return -2

  distance = (signal_on - signal_off) * 17000
  if distance <= MAX_DISTANCE:
    return distance
  else:
    return -3

if __name__ == '__main__':
  signal.signal(signal.SIGINT, cleanup)
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  GPIO.setwarnings(True)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(VIBE, GPIO.OUT)
  GPIO.setup(TRIG,GPIO.OUT)
  GPIO.setup(ECHO,GPIO.IN)

  q = Cue(BUFFER_SIZE)

  kick()
  while True:
    distance = measure()

    if distance > 0:
      q.push(distance)

    i = q.mean() - 50

    if i < 50:
      __interval = 0.1
    elif i >= 50 and i <= 150:
      __interval = float(i) / 500
    else:
      __interval = 1.0

    time.sleep(0.01)
    print q.mean()
