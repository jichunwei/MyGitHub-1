package main

import (
	"fmt"
	"strings"
	"reflect"
	"strconv"
)

func main() {
	var lst = make(STR, 3)
	lst = Iplist(lst)
	fmt.Println("----->>>lst:", lst)

	//Todo: 切割
	s := strings.Split(lst[0], ".")[3]
	fmt.Println("----->>>s:", s)

	//
	v1, v2 := SplitIp("192.168.1.4")
	fmt.Println("---->>>v:", v1, v2)


	//Todo:
	IpListRange("192.168.0.1", "192.168.0.3")
}

type STR []string

func Iplist(Iplst STR) STR {
	Iplst[0] = "192.0.0.2"
	Iplst[1] = "192.0.0.3"

	return Iplst
}

//Todo: 取IP最后一个值
func SplitIp(ip string) (string, interface{}) {
	res := strings.Split(ip, ".")
	lg := len(res)
	s3 := strings.Join(res[0:3], ".")
	return res[lg - 1], s3
}
//
func IpListRange(Start_ip, End_ip string) {
	s1, _ := SplitIp(Start_ip)
	s4, _ := SplitIp(End_ip)

	//Todo:获取数据类型
	key := reflect.TypeOf(s1)
	fmt.Println("-->>key:",key)

	//Todo:转换数据类型
	data,_ := strconv.Atoi(s1)
	key_1 := reflect.TypeOf(data)
	fmt.Println("-->>key_1:",key_1)

	data_4,_ := strconv.Atoi(s4)
	res := data_4 - data

	fmt.Println("---->>>s1:", s1)
	fmt.Println("---->>>s4:", s4)
	fmt.Println("---->>res:", res)

}
