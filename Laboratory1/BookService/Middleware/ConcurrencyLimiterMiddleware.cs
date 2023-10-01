namespace BookService.Middleware;

public class ConcurrencyLimiterMiddleware
{
    private readonly SemaphoreSlim _semaphore;
    private readonly RequestDelegate _next;

    public ConcurrencyLimiterMiddleware(RequestDelegate next, IConfiguration configuration)
    {
        _next = next;
        var maxConcurrentRequests = configuration.GetValue<int>("ConcurrencySettings:MaxConcurrentRequests");
        _semaphore = new SemaphoreSlim(maxConcurrentRequests);
    }

    public async Task InvokeAsync(HttpContext context)
    {
        await _semaphore.WaitAsync();
        try
        {
            await _next(context);
        }
        finally
        {
            _semaphore.Release();
        }
    }
}
