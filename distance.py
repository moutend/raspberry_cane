#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import RPi.GPIO as GPIO
from threading import Timer

def reading(sensor):
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BOARD)

  TRIG = 11
  ECHO = 13

  GPIO.setup(TRIG,GPIO.OUT)
  GPIO.setup(ECHO,GPIO.IN)

  GPIO.output(TRIG, GPIO.LOW)
  GPIO.output(TRIG, True)
  time.sleep(0.00001)
  GPIO.output(TRIG, False)

  MAX_SIGNALL_OFF_PERIOD = 300
  MAX_SIGNALL_ON_PERIOD = 8000
  signal_off = 0
  signal_on  = 0

  k = 0
  while GPIO.input(ECHO) == 0:
    signal_off = time.time()
    k += 1
    if k > MAX_SIGNALL_OFF_PERIOD:
      signal_off = -1
      break

  k = 0
  while GPIO.input(ECHO) == 1:
    signal_on = time.time()
    k += 1
    if k > MAX_SIGNALL_ON_PERIOD:
      signal_on = -1
      break

  if signal_on == -1 or signal_off == -1:
    return -1
  else:
    return (signal_on - signal_off) * 17000
    GPIO.cleanup()

# for _ in xrange(100):
while True:
  print reading(0)
  time.sleep(0.05)
