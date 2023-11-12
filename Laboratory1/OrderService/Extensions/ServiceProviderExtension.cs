using System.Text;
using Microsoft.EntityFrameworkCore;
using Newtonsoft.Json;
using OrderService.Configurations;
using OrderService.Context;
using Polly;

namespace OrderService.Extensions;

public static class ServiceProviderExtension
{
    public static void ApplyMigrations(this IServiceProvider serviceProvider)
    {
        using var scope = serviceProvider.CreateScope();
        var services = scope.ServiceProvider;

        try
        {
            var policy = Policy.Handle<Exception>()
                .WaitAndRetry(new[]
                {
                    TimeSpan.FromSeconds(5),
                    TimeSpan.FromSeconds(10),
                    TimeSpan.FromSeconds(15),
                });

            policy.Execute(() =>
            {
                var context = services.GetRequiredService<OrderContext>();
                context.Database.Migrate();
            });

            Console.WriteLine("Migrated book db");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"An error occurred while migrating the inventory database {ex}");
        }
    }
    
    public static async Task RegisterToServiceDiscovery(this IServiceProvider serviceProvider,
        IConfiguration configuration)
    {
        var serviceConfig = new ServiceConfiguration(configuration);

        var httpClientFactory = serviceProvider.GetRequiredService<IHttpClientFactory>();
        var client = httpClientFactory.CreateClient();
        client.BaseAddress = new Uri(serviceConfig.DiscoveryUrl);

        Console.WriteLine($"Attempting to register with Service Discovery at URL: {client.BaseAddress}");

        var retryPolicy = Policy
            .Handle<HttpRequestException>()
            .WaitAndRetryForeverAsync(
                retryAttempt => TimeSpan.FromSeconds(30),
                (exception, timeSpan, context) =>
                {
                    Console.WriteLine(
                        $"Failed to register with Service Discovery due to {exception.Message}. Waiting for {timeSpan} seconds before retrying...");
                });


        await retryPolicy.ExecuteAsync(async () =>
        {
            // Assuming the service listens on port 80 internally
            var internalPort = 80; 
            var serviceName = configuration.GetValue<string>("SERVICE_NAME");

            // Form the service URL using the service name and internal port
            var serviceUrl = $"http://{serviceName}:{internalPort}";
            Console.WriteLine($"Service url : {serviceUrl}");

            var payload = new
            {
                name = serviceConfig.ServiceName,
                url = serviceUrl
            };

            Console.WriteLine($"Service Name: {payload.name}");
            Console.WriteLine($"Service URL: {payload.url}");

            var response = await client.PostAsync("register",
                new StringContent(JsonConvert.SerializeObject(payload), Encoding.UTF8, "application/json"));

            if (response.IsSuccessStatusCode)
            {
                Console.WriteLine("Successfully registered with Service Discovery!");
            }
            else
            {
                throw new HttpRequestException(
                    $"Failed to register with Service Discovery. StatusCode: {response.StatusCode}");
            }
        });
    }
}