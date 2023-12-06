using OrderService.Entities;
using OrderService.Repositories;
using OrderService.Saga;

namespace OrderService.Services;

public class OrderService : IOrderService
{
    private readonly IOrderRepository _orderRepository;
    private readonly ISagaCoordinator _sagaCoordinator;

    public OrderService(IOrderRepository orderRepository, ISagaCoordinator sagaCoordinator)
    {
        _orderRepository = orderRepository;
        _sagaCoordinator = sagaCoordinator;
    }

    public IEnumerable<Order> GetAllOrders()
    {
        return _orderRepository.GetAll();
    }

    public Order? GetOrderById(int id)
    {
        return _orderRepository.GetById(id);
    }

    public void AddOrder(Order order)
    {
        _orderRepository.Add(order);
    }

    public void UpdateOrder(Order order)
    {
        _orderRepository.Update(order);
    }

    public void DeleteOrder(int id)
    {
        _orderRepository.Delete(id);
    }

    public bool Save()
    {
        return _orderRepository.SaveChanges();
    }

    public async Task ProcessOrder(Order order)
    {
        await _sagaCoordinator.PlaceOrder(order);
    }
}