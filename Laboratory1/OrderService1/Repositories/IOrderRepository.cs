using OrderService.Entities;

namespace OrderService.Repositories;

public interface IOrderRepository
{
    IEnumerable<Order> GetAll();
    Order? GetById(int id);
    void Add(Order? order);
    void Update(Order order);
    void Delete(int id);
    bool SaveChanges();
}
