package json_book_test

import (
	. "book"

	"fmt"
	. "github.com/onsi/ginkgo"
	//. "github.com/onsi/gomega"
)

var _ = Describe("Book test", func() {
	It("can be loaded from JSON", func() {
		book := BOOK.FromJson(`{
            "title":"Les Miserables",
            "author":"Victor Hugo",
            "pages":1488
        }`)

		fmt.Println("Title:", book)
		//Expect(book.Title).To(Equal("Les Miserables"))
		//Expect(book.Author).To(Equal("Victor Hugo"))
		//Expect(book.Pages).To(Equal(1488))
	})
})
