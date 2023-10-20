using BookService.Entities;
using BookService.Services;
using Microsoft.AspNetCore.Mvc;

namespace BookService.Controllers;

[ApiController]
[Route("[controller]")]
public class BookController : ControllerBase
{
    private readonly IBookService _bookService;

    public BookController(IBookService bookService)
    {
        _bookService = bookService;
    }
    
    [HttpGet]
    public IEnumerable<Book> Get()
    {
        return _bookService.GetAllBooks();
    }

    [HttpGet("{id}")]
    public ActionResult<Book> GetBook(int id)
    {
        var book = _bookService.GetBookById(id);
        if (book == null) return NotFound();
        return book;
    }

    [HttpPost("reduceStock/{id}")]
    public IActionResult ReduceStock(int id)
    {
        var book = _bookService.GetBookById(id);
        if (book == null) return NotFound();

        if (!book.InStock) return BadRequest("Book not in stock");

        _bookService.ReduceStock(id);
        _bookService.Save();

        return NoContent();
    }
    
    [HttpPost]
    public ActionResult<Book> Post(Book book)
    {
        _bookService.AddBook(book);
        return CreatedAtAction(nameof(Get), new { id = book.Id }, book);
    }

    [HttpPut("{id}")]
    public IActionResult Put(int id, Book book)
    {
        var existingBook = _bookService.GetBookById(id);
        if (existingBook == null) return NotFound();

        existingBook.Title = book.Title;
        existingBook.Author = book.Author;

        _bookService.UpdateBook(book);

        return NoContent();
    }

    [HttpDelete("{id}")]
    public IActionResult Delete(int id)
    {
        var existingBook = _bookService.GetBookById(id);
        if (existingBook == null) return NotFound();

        _bookService.DeleteBook(id);
        return NoContent();
    }
}