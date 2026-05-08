class Book:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year
        self.is_available = True

    def info(self):
        status = "Доступна" if self.is_available else "Выдана"
        print(f"{self.title} | {self.author} | {self.year} г. | {status}")


class LibraryCard:
    def __init__(self, reader_name, card_number):
        self.reader_name = reader_name
        self.card_number = card_number
        self.borrowed_books = []

    def borrow_book(self, book_obj):
        if book_obj.is_available:
            self.borrowed_books.append(book_obj)
            book_obj.is_available = False
            print(f'Книга "{book_obj.title}" выдана {self.reader_name}')
        else:
            print(f'Книга "{book_obj.title}" уже выдана другому читателю')

    def return_book(self, book_obj):
        self.borrowed_books.remove(book_obj)
        book_obj.is_available = True
        print(f'Книга "{book_obj.title}" возвращена')

    def show_books(self):
        for book in self.borrowed_books:
            print("- ", end="")
            book.info()


book1 = Book("Война и мир", "Лев Толстой", 1869)
book2 = Book("Мастер и Маргарита", "Михаил Булгаков", 1967)
book3 = Book("1984", "Джордж Оруэлл", 1949)

print("=== Книги в библиотеке ===")
book1.info()
book2.info()
book3.info()
print()

card = LibraryCard("Ивану Петрову", 12345)

print("=== Действия с читательским билетом ===")
card.borrow_book(book1)
card.borrow_book(book2)
card.borrow_book(book1)
print()

print("=== Книги у Ивана Петрова ===")
card.show_books()
print()

card.return_book(book1)
print()

print("=== Обновлённый список книг ===")
card.show_books()