using Prometheus;

namespace OrderService.Metric;

public static class MetricsRegistry
{
    public static readonly Counter OrderGetCounter = Metrics
        .CreateCounter("order_get_total", "Counts requests to the GET /order endpoint");

    public static readonly Counter OrderGetByIdCounter = Metrics
        .CreateCounter("order_get_by_id_total", "Counts requests to the GET /order/{id} endpoint");

    public static readonly Counter OrderPostCounter = Metrics
        .CreateCounter("order_post_total", "Counts requests to the POST /order endpoint");

    public static readonly Counter OrderPutCounter = Metrics
        .CreateCounter("order_put_total", "Counts requests to the PUT /order/{id} endpoint");

    public static readonly Counter OrderDeleteCounter = Metrics
        .CreateCounter("order_delete_total", "Counts requests to the DELETE /order/{id} endpoint");

    public static readonly Counter OrderProcess = Metrics
        .CreateCounter("order_process_total", "Counts requests to the ProcessOrder endpoint");
}