using AspNetCoreRateLimit;
using BookService.Context;
using BookService.Infrastructure;
using BookService.Middleware;
using Microsoft.EntityFrameworkCore;

namespace BookService;

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
        services.AddDbContext<BookContext>(options =>
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
        app.UseIpRateLimiting();

        app.UseHsts();
        app.UseAuthorization();
        app.MapControllers();
    }
}