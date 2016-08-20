package main

import "fmt"

func main() {
	fmt.Println("直接声明后调用函数")
	func(a string, b int, c int) (done bool) {
		fmt.Println("a:", a)
		fmt.Println("sum:", b + c)
		return
	}("直接调用", 1, 2)

}
