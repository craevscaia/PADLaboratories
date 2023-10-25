using BookService.Entities;
using BookService.Repositories;

namespace BookService.Services;

public class BookService : IBookService
{
    private readonly IBookRepository _bookRepository;

    public BookService(IBookRepository bookRepository)
    {
        _bookRepository = bookRepository;
    }

    public IEnumerable<Book> GetAllBooks()
    {
        return _bookRepository.GetAll();
    }

    public Book? GetBookById(int id)
    {
        return _bookRepository.GetById(id);
    }

    public void AddBook(Book book)
    {
        _bookRepository.Add(book);
    }

    public void UpdateBook(Book book)
    {
        _bookRepository.Update(book);
    }

    public void DeleteBook(int id)
    {
        _bookRepository.Delete(id);
    }

    public bool Save()
    {
        return _bookRepository.SaveChanges();
    }

    public void ReduceStock(int bookId)
    {
        var book = _bookRepository.GetById(bookId);
        if (book == null)
        {
            throw new InvalidOperationException($"Book with ID {bookId} not found.");
        }

        if (book.Quantity <= 0)
        {
            throw new InvalidOperationException($"No stock available for book with ID {bookId}.");
        }

        book.Quantity -= 1;
        _bookRepository.Update(book);
    }
}