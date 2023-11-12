using AspNetCoreRateLimit;
using BookService.Context;
using BookService.Infrastructure;
using BookService.Middleware;
using Microsoft.EntityFrameworkCore;
using Prometheus;

namespace BookService;

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
        using var scope = app.Services.CreateScope();
        var dbContext = scope.ServiceProvider.GetRequiredService<BookContext>();
        
        Console.WriteLine(dbContext.Database.CanConnect()
            ? "Successfully connected to the database."
            : "Unable to connect to the database.");

        if (app.Environment.IsDevelopment())
        {
            app.UseSwagger();
            app.UseSwaggerUI();
        }
        
        app.UseMiddleware<ConcurrencyLimiterMiddleware>();
        app.UseMiddleware<RequestTimeoutMiddleware>();
        
        app.UseHttpMetrics(); // This tracks metrics for HTTP requests
        app.UseMetricServer(); // This tracks metrics for HTTP requests
        
        app.MapHealthChecks("/health");
        app.UseIpRateLimiting();

        app.UseHsts();
        app.UseAuthorization();
        app.MapControllers();
    }
}