namespace OrderService.Entities;

public class Order
{
    public int Id { get; set; }
    public int BookId { get; set; }
    public int Quantity { get; set; }
    public decimal TotalPrice { get; set; }
}