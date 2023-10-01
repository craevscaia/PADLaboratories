using BookService.Repositories;
using BookService.Services;

namespace BookService.Infrastructure;

public static class DependencyRegistrar
{
    public static void Register(IServiceCollection services)
    {
        services.AddScoped<IBookRepository, BookRepository>();
        services.AddScoped<IBookService, Services.BookService>();
    }
}