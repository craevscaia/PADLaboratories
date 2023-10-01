using OrderService.Entities;

namespace OrderService.Services;

public interface IOrderService
{
    IEnumerable<Order> GetAllOrders();
    Order? GetOrderById(int id);
    void AddOrder(Order order);
    void UpdateOrder(Order order);
    void DeleteOrder(int id);
    bool Save();
    Task ProcessOrder(Order order);
}
