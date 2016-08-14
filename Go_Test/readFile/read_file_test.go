package readFile

import (
	"io/ioutil"
	"os"
	"fmt"
	. "github.com/onsi/ginkgo"
	//. "github.com/onsi/gomega"
	"bufio"
)


/*一次性读取
小文件推荐一次性读取，这样程序更简单，而且速度最快。*/

func ReadAll(filePth string) ([]byte, error) {
	f, err := os.Open(filePth)
	if err != nil {
		return nil, err
	}
	return ioutil.ReadAll(f)
}

var _ = Describe("a", func() {
	Context("b", func() {
		It("c", func() {
			data, err := ReadAll("D:\\JTMM.txt")
			//data, err := ReadAll("D:\\xx.txt")
			if err != nil {
				fmt.Println("err:", err)
			} else {
				fmt.Println("data:", data)
			}

		})
	})
})

