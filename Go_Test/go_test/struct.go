package main

import "fmt"

type ST struct {
	a int
	b int
}
//1. 默认初始化为零
func func_defult(s_t ST, a, b int) ST {
	s_t.a = a
	s_t.b = b
	fmt.Println("s_t:", s_t)

	return s_t
}

func main() {

	//1. 默认初始化为零
	func_defult(ST{}, 1, 10)

	//2. &{}
	S1 := new(ST)  //&{  }
	fmt.Println("S1:", S1)
	S1.a = 1
	S1.b = 2
	fmt.Println("S1:", *S1)

	//3. 未被初始化 <nil>
	var s2 *ST
	fmt.Println("s2:", s2)
	s2 = &ST{a:3, b:4}
	fmt.Println("s2:", *s2)

}
