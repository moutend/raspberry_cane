#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, datetime, os, sys, signal
import RPi.GPIO as GPIO

TRIG    = 12

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIG, GPIO.OUT)

def cleanup_GPIO(signal, frame):
  GPIO.output(TRIG, GPIO.LOW)
  GPIO.output(TRIG, False)
  GPIO.cleanup()
  sys.exit(0)

def shake(sec):
  GPIO.output(TRIG, GPIO.LOW)
  GPIO.output(TRIG, True)
  time.sleep(sec)
  GPIO.output(TRIG, False)
  return sec

signal.signal(signal.SIGINT, cleanup_GPIO)
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

while True:
  print datetime.datetime.now(), shake(0.125)
  time.sleep(0.875)
