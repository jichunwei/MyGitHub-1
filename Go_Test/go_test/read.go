package main

import (
	"fmt"
	//"io/ioutil"
	"bufio"
	"os"
)

func main() {

	inputFile, inputError := os.Open(os.Args[1])
	if inputError != nil {
		fmt.Fprintf(os.Stderr, "File Error: %s\n", inputError)
	}
	fileReader := bufio.NewReader(inputFile)
	counter := 0
	for {
		buf := make([]byte, 1024)
		n, _ := fileReader.Read(buf)
		counter++
		//fmt.Printf("%d,%s", n, string(buf))
		if n == 0 {
			break
		}
		//fmt.Println(n, buf)

		fmt.Printf("%d,%s", n, string(buf))
		fmt.Printf("/////////////////\n")
	}
	fmt.Println(counter)
}
