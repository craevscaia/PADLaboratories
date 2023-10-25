using System.Net;
using System.Text.Json;

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
        var originalCts = context.RequestAborted;
        context.RequestAborted = cts.Token;

        try
        {
            await _next(context);
        }
        catch (OperationCanceledException) when (!originalCts.IsCancellationRequested)
        {
            context.Response.StatusCode = (int)HttpStatusCode.RequestTimeout;
            var timeoutResponse = new { error = "Request timed out" };
            var jsonResponse = JsonSerializer.Serialize(timeoutResponse);
            await context.Response.WriteAsync(jsonResponse);
        }
    }
}
