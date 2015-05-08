#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, datetime, os, sys, signal
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

  limit_signal_off = 300
  limit_signal_on  = 5000
  signal_off = 0
  signal_on  = 0

  while not GPIO.input(ECHO):
    signal_off = time.time()
    limit_signal_off -= 1
    if limit_signal_off == 0: return 0

  while GPIO.input(ECHO):
    signal_on = time.time()
    limit_signal_on -= 1
    if limit_signal_on == 0: return 0

  distance = (signal_on - signal_off) * 17000
  if distance <= 400.0:
    return distance
  else:
    return 0

def vibrate(pipe):
  while True:
    distance = pipe.recv() / 1000
    print("    %s" % distance)
    GPIO.output(VIBE, GPIO.LOW)
    time.sleep(distance)
    GPIO.output(VIBE, True)
    time.sleep(0.125)
    GPIO.output(VIBE, False)

signal.signal(signal.SIGINT, cleanup_GPIO)
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

parent_pipe, child_pipe = Pipe()
vibration_process = Process(target=vibrate, args=(child_pipe,))
vibration_process.start()

while True:
  distance = measure()
  parent_pipe.send(distance)
  print datetime.datetime.now(), distance
  time.sleep(0.05)
