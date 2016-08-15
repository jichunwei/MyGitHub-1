package book

type Book struct {
	Title  string
	Author string
	Pages  int
}

func (book Book)CategoryByLength() string {
	//category := string{}			//用这个将会编译不通过
	var category string
	if book.Pages < 300 {
		category = "SHORT STORY"
	} else {
		category = "NOVEL"
	}
	return category
}

var BOOK = new(Book)

func (book Book)NewBookFromJSON() Book {
	book.Title = "mybook"
	book.Author = "liming"
	book.Pages = 100
	return book
}
