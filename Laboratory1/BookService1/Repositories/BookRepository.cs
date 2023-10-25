using BookService.Context;
using BookService.Entities;

namespace BookService.Repositories;

public class BookRepository : IBookRepository
{
    private readonly BookContext _context;

    public BookRepository(BookContext context)
    {
        _context = context;
    }

    public IEnumerable<Book> GetAll()
    {
        return _context.Books.ToList();
    }

    public Book? GetById(int id)
    {
        return _context.Books.FirstOrDefault(b => b.Id == id);
    }

    public void Add(Book? book)
    {
        if (book == null)
        {
            throw new ArgumentNullException(nameof(book));
        }

        _context.Books.Add(book);
    }

    public void Update(Book book)
    {
        // No code in this implementation as the DbContext will track changes
        // and apply them when SaveChanges is called.
    }

    public void Delete(int id)
    {
        var book = _context.Books.FirstOrDefault(b => b.Id == id);
        if (book != null)
        {
            _context.Books.Remove(book);
        }
    }

    public bool SaveChanges()
    {
        return (_context.SaveChanges() >= 0);
    }
}
