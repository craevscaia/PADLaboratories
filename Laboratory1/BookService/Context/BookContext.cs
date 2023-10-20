using BookService.Entities;
using BookService.Extensions;
using Microsoft.EntityFrameworkCore;

namespace BookService.Context;

public class BookContext : DbContext
{
    public BookContext(DbContextOptions<BookContext> options) : base(options)
    {
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.BookSeed();
    }

    public DbSet<Book> Books { get; set; }
}