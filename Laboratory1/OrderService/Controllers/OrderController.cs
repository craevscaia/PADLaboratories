using Microsoft.AspNetCore.Mvc;
using OrderService.Entities;
using OrderService.Metric;
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
        MetricsRegistry.OrderGetCounter.Inc();

        return Ok(_orderService.GetAllOrders());
    }

    [HttpGet("{id}")]
    public ActionResult<Order> Get(int id)
    {
        MetricsRegistry.OrderGetByIdCounter.Inc();

        var order = _orderService.GetOrderById(id);
        if (order == null) return NotFound("Not found");
        return order;
    }

    [HttpPost]
    public ActionResult<Order> Post(Order order)
    {
        MetricsRegistry.OrderPostCounter.Inc();

        _orderService.AddOrder(order);
        _orderService.Save();

        return CreatedAtAction(nameof(Get), new { id = order.Id }, order);
    }

    [HttpPut("{id}")]
    public IActionResult Put(int id, Order order)
    {
        MetricsRegistry.OrderPutCounter.Inc();
        
        if (id != order.Id) return BadRequest();

        _orderService.UpdateOrder(order);
        _orderService.Save();

        return NoContent();
    }

    [HttpDelete("{id}")]
    public IActionResult Delete(int id)
    {
        MetricsRegistry.OrderDeleteCounter.Inc();

        _orderService.DeleteOrder(id);
        _orderService.Save();

        return NoContent();
    }
    
    [HttpPost("process")]
    public async Task<IActionResult> ProcessOrder([FromBody] Order order)
    {
        try
        {
            MetricsRegistry.OrderProcess.Inc();

            await _orderService.ProcessOrder(order);
            return Ok("Order processed successfully.");
        }
        catch (Exception ex)
        {
            return BadRequest($"Error processing order: {ex.Message}");
        }
    }
}
