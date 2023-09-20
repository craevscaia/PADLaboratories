using Microsoft.EntityFrameworkCore;
using OrderService.Entities;

namespace OrderService.Context;

public class OrderContext : DbContext
{
    public OrderContext(DbContextOptions<OrderContext> options) : base(options)
    {
    }

    public DbSet<Order> Orders { get; set; }
}