namespace OrderService.Middleware;

public class ConcurrencyLimiterMiddleware
{
    private static readonly SemaphoreSlim Semaphore = new SemaphoreSlim(5); // Limit to 5 concurrent requests
    private readonly RequestDelegate _next;

    public ConcurrencyLimiterMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        await Semaphore.WaitAsync();
        try
        {
            await _next(context);
        }
        finally
        {
            Semaphore.Release();
        }
    }
}