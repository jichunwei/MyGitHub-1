/*
	Go对于json有官方自己的解析包，先谈一下json的解码方式。解码的api如下：
	func Unmarshal (data []byte, v interface{})

	在go中，json解码的数据结构有两种，一种是解析到结构体，一种是解析到空的interface。
	以数据 {"changes": [{"index":5, "armid":6},{"index":9,"armid":10}]} 为例

	需要注意的是：

	（1）解析到结构体时只能解析到结构体中的首字母大写的变量
	（2）结构体中数值对应json中的key是大小写不敏感的
*/
*/

package main

import (
	"encoding/json"
	"fmt"
)

func main() {
	type change struct {
		Index int
		Armid int
	}

	type change_slice struct {
		Changes []change
	}

	var msg change_slice

	str := `{"changes": [{"armid":3,"Index":5}, {"armid":3,"Index":6}]}`
	err := json.Unmarshal([]byte(str), &msg)
	if err != nil {
		fmt.Println("Can't decode json message", err)
	}
	fmt.Println(msg)

	for _, change := range msg.Changes {
		fmt.Println(change.Armid, change.Index)
	}
}
