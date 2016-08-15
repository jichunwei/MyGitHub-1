package main

import (
	"net/http"
	"log"
)

func main() {
	resp, err := http.Head("http://www.baidu.com")

	if err != nil {
		log.Println(resp)
	}
	println("----->>",resp)
	log.Println(resp)

}

