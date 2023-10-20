using Microsoft.EntityFrameworkCore;
using OrderService.Entities;

namespace OrderService.Extensions;

public static class ModelBuilderExtensions
{
    public static void OnModelCreating(this ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Order>().HasData(
            new Order { Id = 1, BookId = 1, Quantity = 2, TotalPrice = 21.98M },
            new Order { Id = 2, BookId = 2, Quantity = 1, TotalPrice = 12.99M },
            new Order { Id = 3, BookId = 3, Quantity = 3, TotalPrice = 44.97M },
            new Order { Id = 4, BookId = 4, Quantity = 1, TotalPrice = 9.99M },
            new Order { Id = 5, BookId = 5, Quantity = 2, TotalPrice = 23.98M }
        );
    }
    
}