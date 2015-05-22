#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
import signal
import socket
import sys
import time

BUFFER_SIZE = 128
SOCKET_PATH = '/tmp/echo.sock'

def handle_sigint(signal, frame):
  quit()

def dial():
  sock = socket.socket(socket.AF_UNIX)

  try:
    sock.connect("/tmp/echo.sock")
  except IOError:
    print "fatal: socket does not exist"
    return

  while True:
    try:
      data = sock.recv(BUFFER_SIZE)
      sock.send("ok")
      print "Received: %s" % repr(data)
    except IOError:
      sock.close()
      print "fatal: connection refused"
      return

if __name__ == '__main__':
  signal.signal(signal.SIGPIPE, signal.SIG_IGN)
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
  signal.signal(signal.SIGINT, handle_sigint)

  dial()
