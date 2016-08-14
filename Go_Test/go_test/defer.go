package main

import "fmt"

func main() {
	//Todo: defer，延迟函数
	for i := 0; i < 5; i++ {
      defer fmt.Printf("%d ", i)
  }

	for i := 0; i < 5; i++ {
		fmt.Printf("%d ", i)
	}
	fmt.Println("\n..........")
}
