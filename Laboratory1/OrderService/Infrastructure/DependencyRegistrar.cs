using AspNetCoreRateLimit;
using OrderService.Helpers;
using OrderService.Repositories;
using OrderService.Saga;
using OrderService.Services;

namespace OrderService.Infrastructure;

public static class DependencyRegistrar
{
    public static void Register(IServiceCollection services, IConfiguration configuration)
    {
        services.AddHttpClient("BookServiceClient", client =>
        {
            client.BaseAddress = new Uri(configuration["BookService:BaseUrl"] ?? string.Empty);
        });
        
        services.AddScoped<IOrderRepository, OrderRepository>();
        services.AddScoped<IOrderService, Services.OrderService>();
        services.AddScoped<ISagaCoordinator, SagaCoordinator>();
        services.AddScoped<IOrderProcessor, OrderProcessor>();
        
        RegisterServicesForConcurrency(services, configuration);
    }

    private static void RegisterServicesForConcurrency(IServiceCollection services, IConfiguration configuration)
    {
        services.AddMemoryCache();
        services.Configure<IpRateLimitOptions>(configuration.GetSection("IpRateLimiting"));
        services.Configure<IpRateLimitPolicies>(configuration.GetSection("IpRateLimitPolicies"));
        services.AddInMemoryRateLimiting();
        services.AddSingleton<IIpPolicyStore, MemoryCacheIpPolicyStore>();
        services.AddSingleton<IRateLimitCounterStore, MemoryCacheRateLimitCounterStore>();
        services.AddSingleton<IHttpContextAccessor, HttpContextAccessor>();
        services.AddSingleton<IRateLimitConfiguration, RateLimitConfiguration>();
    }
}