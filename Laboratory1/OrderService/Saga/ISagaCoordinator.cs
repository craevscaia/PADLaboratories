using OrderService.Entities;

namespace OrderService.Saga;

public interface ISagaCoordinator
{
    Task PlaceOrder(Order order);
}