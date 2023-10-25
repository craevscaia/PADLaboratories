using OrderService.Entities;

namespace OrderService.Helpers;

public interface IOrderProcessor
{
    Task<Book?> FetchBookDetails(int bookId);
    Task<bool> ReduceBookStock(int bookId);
}