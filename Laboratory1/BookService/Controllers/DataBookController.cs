using Microsoft.AspNetCore.Mvc;

namespace BookService.Controllers;


[Route("api/book")]
public class DataBookController: ControllerBase
{
    // api/order/getbookById
    [HttpGet(Name = "GetBookById")]
    public void GetBookById(int bookId)
    {
        WebRequestMethods.Http.Get("api/book/getbyid")
    }
}