package book_test

import (
	. "book"

	"fmt"
	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
)

var _ = Describe("Book", func() {
	var (
		longBook Book
		shortBook Book
	)

	BeforeEach(func() {
		longBook = Book{
			Title:  "Les Miserables",
			Author: "Victor Hugo",
			Pages:  1488,
		}

		shortBook = Book{
			Title:  "Fox In Socks",
			Author: "Dr. Seuss",
			Pages:  24,
		}
	})

	Describe("Categorizing book length", func() {
		Context("With more than 300 pages", func() {
			It("should be a novel", func() {
				Expect(longBook.CategoryByLength()).To(Equal("NOVEL"))
				//Fail("Failure reason: nothing")
			})
		})

		Context("With fewer than 300 pages", func() {
			It("should be a short story", func() {
				Expect(shortBook.CategoryByLength()).To(Equal("SHORT STORY"))
			})

			It("panics in a goroutine", func(done Done) {
				go func() {
					defer GinkgoRecover()

					Ω(doSomething()).Should(BeTrue())

					close(done)
				}()
			})
		})

		Context("when calling Foo()", func() {
			Context("when no ID is provided", func() {
				Specify("an ErrNoID error is returned", func() {
				})
			})
		})
	})
})

func doSomething() bool {
	fmt.Println("do something!")
	return true
}