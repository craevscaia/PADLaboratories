using OrderService.Context;
using OrderService.Entities;
using OrderService.Helpers;
using OrderService.Repositories;
using OrderService.Services;

namespace OrderService.Saga;

public class SagaCoordinator : ISagaCoordinator
{
    private readonly IOrderProcessor _orderProcessor;
    private readonly OrderContext _context;
    private readonly IOrderRepository _orderRepository;

    public SagaCoordinator(IOrderProcessor orderProcessor, OrderContext context, IOrderRepository orderRepository)
    {
        _orderProcessor = orderProcessor;
        _context = context;
        _orderRepository = orderRepository;
    }

    public async Task PlaceOrder(Order order)
    {
        await using var transaction = await _context.Database.BeginTransactionAsync();

        try
        {
            var book = await _orderProcessor.FetchBookDetails(order.BookId);
            if (book == null || !book.InStock)
            {
                throw new InvalidOperationException("Book is not available.");
            }

            order.TotalPrice = book.Price;
            
            
            // Add the order to the repository
            _orderRepository.Add(order);
            
            var isStockReduced = await _orderProcessor.ReduceBookStock(order.BookId);
            if (!isStockReduced)
            {
                throw new InvalidOperationException("Failed to reduce book stock.");
            }
            
            await transaction.CommitAsync();
        }
        catch (Exception ex)
        {
            // Rollback the transaction in case of any failure
            await transaction.RollbackAsync();
            Console.WriteLine($"Saga failed for placing order. Ex: {ex}");
            throw;
        }
    }
}