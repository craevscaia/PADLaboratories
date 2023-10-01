using OrderService.Context;
using OrderService.Entities;

namespace OrderService.Repositories;

public class OrderRepository : IOrderRepository
{
    private readonly OrderContext _context;

    public OrderRepository(OrderContext context)
    {
        _context = context;
    }

    public IEnumerable<Order> GetAll()
    {
        return _context.Orders.ToList();
    }

    public Order? GetById(int id)
    {
        return _context.Orders.FirstOrDefault(o => o.Id == id);
    }

    public void Add(Order? order)
    {
        if (order == null)
        {
            throw new ArgumentNullException(nameof(order));
        }

        _context.Orders.Add(order);
    }

    public void Update(Order order)
    {
        // No code here as DbContext will track changes and apply them when SaveChanges is called.
    }

    public void Delete(int id)
    {
        var order = _context.Orders.FirstOrDefault(o => o.Id == id);
        if (order != null)
        {
            _context.Orders.Remove(order);
        }
    }

    public bool SaveChanges()
    {
        return (_context.SaveChanges() >= 0);
    }
}
