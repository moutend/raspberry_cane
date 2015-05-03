#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, os, sys, datetime
import RPi.GPIO as GPIO

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

MAX_OFF = 200
MAX_ON  = 5000
TRIG    = 11
ECHO    = 13

def reading():
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)

  GPIO.setup(TRIG,GPIO.OUT)
  GPIO.setup(ECHO,GPIO.IN)

  GPIO.output(TRIG, GPIO.LOW)
  GPIO.output(TRIG, True)
  time.sleep(0.00001)
  GPIO.output(TRIG, False)

  signal_off = 0
  k = 0
  while GPIO.input(ECHO) == 0:
    signal_off = time.time()
    k += 1
    if k > MAX_OFF:
      signal_off = 0
      break

  if signal_off == 0:
    return -1

  signal_on  = 0
  k = 0
  while GPIO.input(ECHO) == 1:
    signal_on = time.time()
    k += 1
    if k > MAX_ON:
      signal_on = 0
      break

  if signal_on == 0:
    return -1

  distance = (signal_on - signal_off) * 17000
  GPIO.cleanup()
  return (signal_on - signal_off) * 17000

while True:
  print datetime.datetime.now(), reading()
  time.sleep(0.05)
