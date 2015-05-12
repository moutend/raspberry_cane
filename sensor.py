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

  def get_mean(self):
    return reduce(lambda x, y: x + y, self.list) / len(self.list)

def cleanup_GPIO(signal, frame):
  GPIO.output(TRIG, GPIO.LOW)
  GPIO.output(TRIG, False)
  GPIO.output(VIBE, GPIO.LOW)
  GPIO.output(VIBE, False)

  GPIO.cleanup()
  sys.exit(0)

def measure():
  GPIO.output(TRIG, GPIO.LOW)
  GPIO.output(TRIG, True)
  time.sleep(0.00001)
  GPIO.output(TRIG, False)

  limit_signal_off = 2568
  limit_signal_on  = 8192
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

def shake():
  for _ in range(2):
    GPIO.output(VIBE, GPIO.LOW)
    GPIO.output(VIBE, True)
    time.sleep(0.05)
    GPIO.output(VIBE, False)
    time.sleep(0.05)

def vibrate(sec):
  time.sleep(0.1)
  while True:
    GPIO.output(VIBE, GPIO.LOW)
    GPIO.output(VIBE, True)
    time.sleep(0.05)
    GPIO.output(VIBE, False)
    time.sleep(sec)

if __name__ == '__main__':
  signal.signal(signal.SIGINT, cleanup_GPIO)
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

  GPIO.setwarnings(True)
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(TRIG,GPIO.OUT)
  GPIO.setup(VIBE, GPIO.OUT)
  GPIO.setup(ECHO,GPIO.IN)

  d1 = -1
  pid = -1

  if pid != -1:
    os.kill(pid, signal.SIGTERM)
  p = Process(target=vibrate, args=(0.75,))
  p.daemon = True
  p.start()
  pid = p.pid

  q = Cue(25)
  q.clear()
  flag = False
  while True:
    d2 = int(measure()) / 10
    if d2 > 0:
      q.push(d2)

    if flag == False and  q.get_mean() < 7:
      time.sleep(0.1)
      os.kill(pid, signal.SIGTERM)
      p = Process(target=vibrate, args=(0.125,))
      p.daemon = True
      p.start()
      pid = p.pid
      flag = True

    if flag == True and q.get_mean() >= 7:
      time.sleep(0.1)
      os.kill(pid, signal.SIGTERM)
      p = Process(target=vibrate, args=(0.75,))
      p.daemon = True
      p.start()
      pid = p.pid
      flag = False

    print datetime.datetime.now(), q.get_mean(), d2
    d1 = d2
    time.sleep(0.01)
