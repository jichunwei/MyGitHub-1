package main

import "server"
import (
	"fmt"
	"reflect"
)

func main() {
	//声明
	var ss server.SomeType
	fmt.Println("type ss is:", reflect.TypeOf(ss))
	fmt.Println("---->>>ss=", ss)

	s1 := new(server.SomeType)
	//s1 := &server.SomeType{}

	fmt.Println("---->>>s1:",*s1)

	s2 := server.SomeType{}
	fmt.Println("---->>>s2:",s2)

}


