using AspNetCoreRateLimit;
using Microsoft.EntityFrameworkCore;
using OrderService.Context;
using OrderService.Infrastructure;
using OrderService.Middleware;
namespace OrderService;

public class Startup
{
    public IConfiguration Configuration { get; }

    public Startup(IHostEnvironment environment)
    {
        var builder = new ConfigurationBuilder()
            .SetBasePath(environment.ContentRootPath)
            .AddJsonFile("appsettings.json", optional: true, reloadOnChange: true)
            .AddJsonFile($"appsettings.{environment.EnvironmentName}.json", optional: true)
            .AddEnvironmentVariables(); // This line ensures environment variables are used

        Configuration = builder.Build();
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
        app.UseIpRateLimiting(); // concurrency task limit

        app.UseHsts();
        app.UseAuthorization();
        app.MapControllers();
    }
}