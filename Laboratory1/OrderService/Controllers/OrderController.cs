using Microsoft.AspNetCore.Mvc;
using OrderService.Entities;
using OrderService.Services;

namespace OrderService.Controllers;

[ApiController]
[Route("[controller]")]
public class OrderController : ControllerBase
{
    private readonly IOrderService _orderService;

    public OrderController(IOrderService orderService)
    {
        _orderService = orderService;
    }

    [HttpGet]
    public ActionResult<IEnumerable<Order>> Get()
    {
        return Ok(_orderService.GetAllOrders());
    }

    [HttpGet("{id}")]
    public ActionResult<Order> Get(int id)
    {
        var order = _orderService.GetOrderById(id);
        if (order == null) return NotFound();
        return order;
    }

    [HttpPost]
    public ActionResult<Order> Post(Order order)
    {
        _orderService.AddOrder(order);
        _orderService.Save();

        return CreatedAtAction(nameof(Get), new { id = order.Id }, order);
    }

    [HttpPut("{id}")]
    public IActionResult Put(int id, Order order)
    {
        if (id != order.Id) return BadRequest();

        _orderService.UpdateOrder(order);
        _orderService.Save();

        return NoContent();
    }

    [HttpDelete("{id}")]
    public IActionResult Delete(int id)
    {
        _orderService.DeleteOrder(id);
        _orderService.Save();

        return NoContent();
    }
    
    [HttpPost("process")]
    public async Task<IActionResult> ProcessOrder([FromBody] Order order)
    {
        try
        {
            await _orderService.ProcessOrder(order);
            return Ok("Order processed successfully.");
        }
        catch (Exception ex)
        {
            return BadRequest($"Error processing order: {ex.Message}");
        }
    }
}
