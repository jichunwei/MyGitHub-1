package main

import (
	"fmt"
	"github.com/onsi/gomega"
)

func main() {
	st := `{
            "title":"Les Miserables",
            "author":"Victor Hugo",
            "pages":1488
        }`

	fmt.Println("st:", gomega.MatchJSON(st))
}
