package main

import (
	"fmt"
)

func MyPrint(args ...interface{}) {
	for _, arg := range args {
		switch arg.(type) {
		case int:
			fmt.Println(arg, "is an int value")
		case string:
			fmt.Println(arg, "is a string value")
		default:
			fmt.Println(arg, "is a unkown type")
		}
	}
}

func main() {
	var v1 int = 1
	var v2 string = "hello"
	var v3 float32 = 1.234

	MyPrint(v1, v2, v3)
}
