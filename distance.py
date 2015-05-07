#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, datetime, os, sys, signal
import RPi.GPIO as GPIO

TRIG = 11
ECHO = 13

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

def cleanup_GPIO(signal, frame):
  GPIO.output(TRIG, GPIO.LOW)
  GPIO.output(TRIG, False)
  GPIO.cleanup()
  sys.exit(0)

def measure():
  GPIO.output(TRIG, GPIO.LOW)
  GPIO.output(TRIG, True)
  time.sleep(0.00001)
  GPIO.output(TRIG, False)

  limit_signal_off = 300
  limit_signal_on  = 5000
  signal_off = 0
  signal_on  = 0

  while not GPIO.input(ECHO):
    signal_off = time.time()
    limit_signal_off -= 1
    if limit_signal_off == 0: return -1

  while GPIO.input(ECHO):
    signal_on = time.time()
    limit_signal_on -= 1
    if limit_signal_on == 0: return -1

  distance = (signal_on - signal_off) * 17000
  if distance <= 400.0:
    return distance
  else:
    return -1

signal.signal(signal.SIGINT, cleanup_GPIO)
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

while True:
  print datetime.datetime.now(), measure()
  time.sleep(0.05)
