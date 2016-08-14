package main

import (
	"net/http"
	"io"
	"os"
	"log"
	"fmt"
)

func main() {
	//resp ,err := http.Get("http://www.baidu.com")
	resp, err := http.Get("http://127.0.0.1:8000")

	if err != nil {
		println("ok")
	}
	defer resp.Body.Close()

	io.Copy(os.Stdout, resp.Body)

	resp, err = http.Head("http://www.baidu.com")

	if err != nil {
		log.Println(resp)
	}
	fmt.Println("resp:",resp)
}
