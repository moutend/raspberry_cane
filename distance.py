#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import signal
import time
import datetime
import RPi.GPIO as GPIO

BUFFER_SIZE = 24
MAX_SIGNAL_OFF = 128
MAX_SIGNAL_ON = 4096
MAX_DISTANCE = 400.0
TRIG = 11
ECHO = 13

class Cue:
  def __init__(self, size):
    self.size = size
    self.list = [0]

  def push(self, item):
    if len(self.list) >= self.size:
      self.list.pop(0)
    self.list.append(item)

  def mean(self):
    if len(self.list) < self.size:
      return -1
    else:
      return reduce(lambda x, y: x + y, self.list) / len(self.list)

def cleanup_GPIO(signal, frame):
  print "\nDO:   cleanup_GPIO()"
  GPIO.output(TRIG, GPIO.LOW)
  GPIO.output(TRIG, False)
  GPIO.cleanup()
  print "DONE: cleanup_GPIO()"

  exit(0)

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
  signal.signal(signal.SIGINT, cleanup_GPIO)
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(TRIG,GPIO.OUT)
  GPIO.setup(ECHO,GPIO.IN)

  q = Cue(BUFFER_SIZE)
  d1 = 0

  print "Mean [cm]\tMeasured [cm]\tDate"
  while True:
    distance = measure()
    if distance > 0:
      q.push(distance)

    d2 = int(q.mean())
    print "%s\t%s\t%s" % (d2, distance, datetime.datetime.now())

    d1 = d2
    time.sleep(0.01)
