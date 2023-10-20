using Microsoft.EntityFrameworkCore;
using OrderService.Entities;
using OrderService.Extensions;

namespace OrderService.Context;

public class OrderContext : DbContext
{
    public OrderContext(DbContextOptions<OrderContext> options) : base(options)
    {
    }
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.SeedOrder();
    }

    public DbSet<Order> Orders { get; set; }
}