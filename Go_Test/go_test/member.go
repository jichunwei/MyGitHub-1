package main

import (
	"fmt"
)

func main() {
	conf := [...]interface{}{
		"a",
		1,
		nil,
		true,
	}

	fmt.Println(conf)

	var bodyParameters []interface{}
	bodyParameters = []interface{}{
		map[string]interface{}{
			"id":    "xxDsc0-dx",
		},
		map[string]interface{}{
			"id":    "aaabbbbcccc",
		},
		map[string]interface{}{
			"id":    "xxxxxxxxxx",
		},
	}

	fmt.Println(bodyParameters)

	rm_conf := map[string]interface{}{
		"delete":    []interface{}{
		},
	}

	lth := len(bodyParameters)
	fmt.Println(lth)
	for i := 0; i < lth; i++ {
		rm_conf["delete"] = bodyParameters[i]
		fmt.Println(rm_conf)
	}

}
