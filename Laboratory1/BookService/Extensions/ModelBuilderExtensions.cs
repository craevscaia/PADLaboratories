using BookService.Entities;
using Microsoft.EntityFrameworkCore;

namespace BookService.Extensions;

public static class ModelBuilderExtensions
{
    public static void OnModelCreating(this ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Book>().HasData(
            new Book
            {
                Id = 1, Title = "The Great Gatsby", Author = "F. Scott Fitzgerald", Price = 10.99M, Quantity = 5
            },
            new Book { Id = 2, Title = "Moby Dick", Author = "Herman Melville", Price = 12.99M, Quantity = 3 },
            new Book { Id = 3, Title = "1984", Author = "George Orwell", Price = 14.99M, Quantity = 7 },
            new Book { Id = 4, Title = "To Kill a Mockingbird", Author = "Harper Lee", Price = 9.99M, Quantity = 10 },
            new Book { Id = 5, Title = "Pride and Prejudice", Author = "Jane Austen", Price = 11.99M, Quantity = 2 }
        );
    }
    
}