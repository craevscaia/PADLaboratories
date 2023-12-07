using System.Text.Json;
using OrderService.Entities;

namespace OrderService.Helpers;

public class OrderProcessor : IOrderProcessor
{
    private readonly HttpClient _httpClient;

    public OrderProcessor()
    {
        _httpClient = new HttpClient();
        _httpClient.BaseAddress = new Uri("http://apigateway:5000");
    }

    public async Task<Book?> FetchBookDetails(int bookId)
    {
        var response = await _httpClient.GetAsync($"/book/{bookId}");
        if (response.IsSuccessStatusCode)
        {
            var book = JsonSerializer.Deserialize<Book>(await response.Content.ReadAsStringAsync());
            return book;
        }
        return null;
    }

    public async Task<bool> ReduceBookStock(int bookId)
    {
        var response = await _httpClient.PostAsync($"/book/reduceStock/{bookId}", null);
        return response.IsSuccessStatusCode;
    }
}
