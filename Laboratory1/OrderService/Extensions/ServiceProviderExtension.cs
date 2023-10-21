﻿using Microsoft.EntityFrameworkCore;
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
}