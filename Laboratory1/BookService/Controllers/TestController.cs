using Microsoft.AspNetCore.Mvc;

namespace BookService.Controllers;

[ApiController]
[Route("book/test")]
public class TestController : ControllerBase
{
    [HttpGet("reroute")]
    public ActionResult Reroute()
    {
        Console.WriteLine("Simulating service failure. Returning 500 status code.");
        return StatusCode(500); // Simulate service failure
    }
}