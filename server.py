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
  cleanup()
  quit()

def cleanup():
  try:
    os.unlink(SOCKET_PATH)
  except OSError:
    return

def serve():
  cleanup()

  sock = socket.socket(socket.AF_UNIX)
  sock.bind(SOCKET_PATH)
  sock.listen(1)

  print "Waiting for new connection."

  conn, addr = sock.accept()

  print "Connected: %s" % addr

  data = 0
  while True:
    try:
      conn.sendall(str(data))
      res = conn.recv(BUFFER_SIZE)
      print "Sent: %s %s" % (data, res)
      data += 1
      time.sleep(1)
    except IOError:
      conn.close()
      print "Disconnected"
      serve()
      break

if __name__ == '__main__':
  signal.signal(signal.SIGPIPE, signal.SIG_IGN)
  sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
  signal.signal(signal.SIGINT, handle_sigint)

  serve()
