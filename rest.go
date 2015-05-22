package main

import (
  "fmt"
  "log"
  "net"
  "net/http"
  "io"
  "io/ioutil"
  "encoding/json"
  "strconv"
)

var _distance int = 0

func reader(r io.Reader) {
  buf := make([]byte, 128)
  n, err := r.Read(buf[:])
  if err != nil {
    log.Fatal(err)
    return
  }
  distance := string(buf[0:n])
  println("Client got:", n, distance)
  res, err := strconv.Atoi(distance)
  if err != nil {
    log.Fatal(err)
    return
  }
  _distance = res
}

func recv() {
  c, err := net.Dial("unix", "/tmp/echo.sock")
  if err != nil {
    log.Fatal(err)
  }

  defer c.Close()
  for {
    reader(c)
    _, err := c.Write([]byte("hi"))

    if err != nil {
      log.Fatal("write error:", err)
      break
    }
  }
}

type Distance struct {
  Step int
  Distance int
}

func jsonHandler(w http.ResponseWriter, r *http.Request) {
  obj := Distance{0, _distance}
  out_json,err := json.Marshal(obj)
  if err != nil {
    log.Fatal(err)
  }
  w.Header().Set("Content-Type", "application/json")
  fmt.Fprint(w, string(out_json))
}

func viewHandler(w http.ResponseWriter, r *http.Request) {
  html, err := ioutil.ReadFile("./index.html")
  if err != nil {
    log.Fatal("ListenAndServe: ", err)
  }
  fmt.Fprintf(w, string(html))
}

func main() {
  go recv()
  http.HandleFunc("/", viewHandler)
  http.HandleFunc("/data.json", jsonHandler)
  err := http.ListenAndServe(":9090", nil)
  if err != nil {
    log.Fatal("ListenAndServe: ", err)
  }
  println("listen")
}
