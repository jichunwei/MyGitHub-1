package books_test

import (
	//. "UNKNOWN_PACKAGE_PATH"
	. "book"

	. "github.com/onsi/ginkgo"
	. "github.com/onsi/gomega"
	"fmt"
)

//type Book struct {
//	Title  string
//	Author string
//	Pages  int
//}

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
			})
		})

		Context("With fewer than 300 pages", func() {
			It("should be a short story", func() {
				Expect(shortBook.CategoryByLength()).To(Equal("SHORT STORY"))
			})
		})

		It("panics in a goroutine", func(done Done) {
			go func() {
				defer GinkgoRecover()
				Ω(doSomething()).Should(BeTrue())
				close(done)
			}()
		})
	})

})

var _ = Describe("Book", func() {
	It("can be loaded from JSON", func() {
		//book := Book.NewBookFromJSON()
		book := BOOK.NewBookFromJSON()

		fmt.Println("book:", book)
		Expect(book.Title).To(Equal("mybook"))
		Expect(book.Author).To(Equal("liming"))
		Expect(book.Pages).To(Equal(100))
	})
})

func doSomething() bool {
	fmt.Println("do something!")
	return true
}