using OrderService.Entities;
using OrderService.Helpers;
using OrderService.Repositories;

namespace OrderService.Services;

public class OrderService : IOrderService
{
    private readonly IOrderRepository _orderRepository;
    private readonly OrderProcessor _orderProcessor;

    public OrderService(IOrderRepository orderRepository, OrderProcessor orderProcessor)
    {
        _orderRepository = orderRepository;
        _orderProcessor = orderProcessor;
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
        var book = await _orderProcessor.FetchBookDetails(order.BookId);
        if (book == null || !book.InStock)
        {
            throw new InvalidOperationException("Book is not available.");
        }

        order.TotalPrice = book.Price;

        var isStockReduced = await _orderProcessor.ReduceBookStock(order.BookId);
        if (!isStockReduced)
        {
            throw new InvalidOperationException("Failed to reduce book stock.");
        }

        // Add the order to the repository
        AddOrder(order);
        Save();
    }
}