using BookService.Controllers;
using BookService.Entities;
using BookService.Services;
using Moq;

namespace BookService.Tests;

public class BookControllerTests
{
    [Fact]
    public void Get_ReturnsAllBooks()
    {
        // Arrange
        var mockService = new Mock<IBookService>();
        mockService.Setup(s => s.GetAllBooks()).Returns(GetTestBooks());
        var controller = new BookController(mockService.Object);

        // Act
        var result = controller.Get();

        // Assert
        var books = Assert.IsType<List<Book>>(result);
        Assert.Equal(3, books.Count);
    }

    private List<Book> GetTestBooks()
    {
        return new List<Book>
        {
            new Book { Id = 1, Title = "Book 1", Author = "Author 1" },
            new Book { Id = 2, Title = "Book 2", Author = "Author 2" },
            new Book { Id = 3, Title = "Book 3", Author = "Author 3" },
        };
    }
}
