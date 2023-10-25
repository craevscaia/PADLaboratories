using BookService.Context;
using Microsoft.EntityFrameworkCore;

namespace BookService.Tests;

public class DatabaseTests
{
    [Fact]
    public void CanConnectToDatabase()
    {
        var options = new DbContextOptionsBuilder<BookContext>()
            .UseInMemoryDatabase(databaseName: "TestDatabase")
            .Options;

        using (var context = new BookContext(options))
        {
            Assert.True(context.Database.CanConnect());
        }
    }
}