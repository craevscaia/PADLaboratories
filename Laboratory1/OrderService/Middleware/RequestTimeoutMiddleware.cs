namespace OrderService.Middleware;

public class RequestTimeoutMiddleware
{
    private readonly RequestDelegate _next;
    private readonly TimeSpan _timeout;

    public RequestTimeoutMiddleware(RequestDelegate next, IConfiguration configuration)
    {
        _next = next;
        _timeout = TimeSpan.FromSeconds(configuration.GetValue<int>("RequestTimeoutSettings:TimeoutInSeconds"));
    }

    public async Task InvokeAsync(HttpContext context)
    {
        using var cts = new CancellationTokenSource(_timeout);
        var originalToken = context.RequestAborted;
        context.RequestAborted = cts.Token;

        try
        {
            await _next(context);
        }
        catch (OperationCanceledException) when (cts.IsCancellationRequested)
        {
            // Log the timeout event here if needed
            context.Response.StatusCode = 408; // Request Timeout
            await context.Response.WriteAsync("Request timed out.");
        }
        finally
        {
            cts.Dispose();
            context.RequestAborted = originalToken;
        }
    }
}
