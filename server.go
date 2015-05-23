package main

import (
  "log"
  "net"
  "os"
  "time"
  "strconv"
)

func echoServer(c net.Conn) {
  data := 0
  for {
    _, err := c.Write([]byte(strconv.Itoa(data)))
    if err != nil {
      log.Fatal("Write: ", err)
    }
    buf := make([]byte, 128)
    n, err := c.Read(buf[:])
    if err != nil {
      return
    }
    println("Sent: ", data, string(buf[0:n]))
    time.Sleep(1000 * time.Millisecond)
    data += 1
  }
}

func main() {
  path := "/tmp/echo.sock"
  err := os.Remove(path)
  if err != nil {
    println("remove existing socket")
  }

  l, err := net.Listen("unix", path)
  if err != nil {
    log.Fatal("listen error:", err)
  }

  for {
    println("waiting for new connection")
    c, err := l.Accept()
    if err != nil {
      log.Fatal("accept error:", err)
    }
    go echoServer(c)
  }
}
