using AspNetCoreRateLimit;
using BookService.Repositories;
using BookService.Services;

namespace BookService.Infrastructure;

public static class DependencyRegistrar
{
    public static void Register(IServiceCollection services, IConfiguration configuration)
    {
        services.AddHttpClient("OrderServiceClient", client =>
        {
            client.BaseAddress = new Uri(configuration["OrderService:BaseUrl"] ?? string.Empty);
        });
        
        services.AddScoped<IBookRepository, BookRepository>();
        services.AddScoped<IBookService, Services.BookService>();

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