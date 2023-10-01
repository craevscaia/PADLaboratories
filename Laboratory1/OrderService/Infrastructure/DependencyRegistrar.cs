using OrderService.Repositories;
using OrderService.Services;

namespace OrderService.Infrastructure;

public static class DependencyRegistrar
{
    public static void Register(IServiceCollection services)
    {
        services.AddScoped<IOrderRepository, OrderRepository>();
        services.AddScoped<IOrderService, Services.OrderService>();
    }
}