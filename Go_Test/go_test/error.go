package main

import (
	"fmt"
)

type error struct {
	err string
	n   int
}

func Foo(err error , n int, er string ) error {
	err.err = er
	err.n = n
	return err
}

func main() {
	et := error{}
	err := Foo(et,2, "xx")

	if err.err == "" {
		fmt.Println("error occure")
	} else {
		fmt.Println(err.n)
	}
}


