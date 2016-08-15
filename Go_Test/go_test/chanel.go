package main

import "fmt"

var count = 0

func Count(ch chan int) {
	count++
	fmt.Println("count:", count)
	ch <- 1
	//fmt.Println("count:",count)
}

func main() {
	chs := make([]chan int, 100)
	for i := 0; i < 100; i++ {
		chs[i] = make(chan int)

		go Count(chs[i])
	}

	for _, ch := range (chs) {
		<-ch
	}

	/*c := make(chan int, 1)
	for {
		select {
		case c <- 0:
		case c <- 1:
		}
		i := <-c
		fmt.Println("value received:", i)
	}*/
}
