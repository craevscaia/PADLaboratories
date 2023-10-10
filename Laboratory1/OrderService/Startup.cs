using AspNetCoreRateLimit;
using Microsoft.EntityFrameworkCore;
using OrderService.Context;
using OrderService.Infrastructure;
using OrderService.Middleware;
namespace OrderService;

public class Startup
{
    public IConfiguration Configuration { get; }

    public Startup(IConfiguration configuration)
    {
        Configuration = configuration;
    }

    public void ConfigureServices(IServiceCollection services)
    {
        // Database context
        services.AddDbContext<OrderContext>(options =>
            options.UseNpgsql(Configuration.GetConnectionString("DefaultConnection")));

        // MVC controllers
        services.AddControllers();

        // API documentation
        services.AddEndpointsApiExplorer();
        services.AddSwaggerGen();
        services.AddHealthChecks();

        DependencyRegistrar.Register(services, Configuration);
    }

    public void Configure(WebApplication app)
    {
        if (app.Environment.IsDevelopment())
        {
            app.UseSwagger();
            app.UseSwaggerUI();
        }

        app.UseMiddleware<ConcurrencyLimiterMiddleware>();
        app.UseMiddleware<RequestTimeoutMiddleware>();

        app.MapHealthChecks("/health");
        
        //2 requests per second
        app.UseIpRateLimiting();

        app.UseHttpsRedirection();
        app.UseAuthorization();
        app.MapControllers();
    }
}