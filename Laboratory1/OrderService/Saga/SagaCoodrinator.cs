using OrderService.Context;
using OrderService.Entities;
using OrderService.Helpers;
using OrderService.Services;

namespace OrderService.Saga;

public class SagaCoordinator : ISagaCoordinator
{
    private readonly IOrderProcessor _orderProcessor;
    private readonly IOrderService _orderService;
    private readonly OrderContext _context;

    public SagaCoordinator(IOrderProcessor orderProcessor, IOrderService orderService, OrderContext context)
    {
        _orderProcessor = orderProcessor;
        _orderService = orderService;
        _context = context;
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

            var isStockReduced = await _orderProcessor.ReduceBookStock(order.BookId);
            if (!isStockReduced)
            {
                throw new InvalidOperationException("Failed to reduce book stock.");
            }

            // Add the order to the repository
            _orderService.AddOrder(order);
            _orderService.Save();
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