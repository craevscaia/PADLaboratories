namespace BookService.Middleware;

public class ConcurrencyLimiterMiddleware
{
    private readonly SemaphoreSlim _semaphore; //used in asynchronous scenarios,  limit the number of concurrent requests
    private readonly RequestDelegate _next; //next middleware in the pipeline

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
