/*
判断获取数据类型
 */

package main

import (
	"fmt"
	"reflect"
)

func main() {
	var x = "Hello"
	fmt.Println(reflect.TypeOf(x))
}