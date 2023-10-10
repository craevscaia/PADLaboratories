using System.Text.Json;
using OrderService.Entities;

namespace OrderService.Helpers;

public class OrderProcessor : IOrderProcessor
{
    private readonly HttpClient _httpClient;

    public OrderProcessor(IHttpClientFactory httpClientFactory)
    {
        _httpClient = httpClientFactory.CreateClient("BookServiceClient");
    }

    public async Task<Book?> FetchBookDetails(int bookId)
    {
        var response = await _httpClient.GetAsync($"/books/{bookId}");
        if (response.IsSuccessStatusCode)
        {
            var book = JsonSerializer.Deserialize<Book>(await response.Content.ReadAsStringAsync());
            return book;
        }
        return null;
    }

    public async Task<bool> ReduceBookStock(int bookId)
    {
        var response = await _httpClient.PostAsync($"/books/reduceStock/{bookId}", null);
        return response.IsSuccessStatusCode;
    }
}
