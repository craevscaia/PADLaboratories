using BookService.Entities;

namespace BookService.Services;

public interface IBookService
{
    IEnumerable<Book> GetAllBooks();
    Book? GetBookById(int id);
    void AddBook(Book book);
    void UpdateBook(Book book);
    void DeleteBook(int id);
    bool Save();
    void ReduceStock(int bookId);
}
