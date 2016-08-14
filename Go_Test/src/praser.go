package main

import "fmt"

func Test() interface{} {
	body := map[string]interface{}{
		"a":    "xx",
		"b":    "bb",
		"c":    12,
	}
	return body
}

//获取单个要删除的member
func getMemberBody(MemberId string) interface{} {
	conf := map[string]interface{}{
		"removeInfo": []interface{}{
			MemberId,
		},
	}
	return conf
}

func GetMembersBody(MemberList []string) interface{} {
	//var myslice =make([]interface{},0,3)
	var myslice []interface{}
	lth := len(MemberList)
	for i := 0; i < lth; i++{
		fmt.Println("before:",myslice)
		myslice = append(myslice,MemberList[i])
		fmt.Println("after:",myslice)
	}
	return myslice
}

func main() {
	v := Test()
	fmt.Println("---------->>>v:", v)

	M_id := "ab-cd-xd-xf"

	conf := getMemberBody(M_id)
	fmt.Println("------->>>conf:", conf)

	lst := []string{"aaa","bbbb","cccc"}
	conf_1 := GetMembersBody(lst)
	fmt.Println("----->>>conf_1:",conf_1)
}