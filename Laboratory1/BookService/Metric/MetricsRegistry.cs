using Prometheus;

namespace BookService.Metric;

public static class MetricsRegistry
{
    public static readonly Counter BookGetCounter = Metrics
        .CreateCounter("book_get_total", "Counts requests to the GET /book endpoint");

    public static readonly Counter BookGetByIdCounter = Metrics
        .CreateCounter("book_get_by_id_total", "Counts requests to the GET /book/{id} endpoint");

    public static readonly Counter BookPostCounter = Metrics
        .CreateCounter("book_post_total", "Counts requests to the POST /book endpoint");

    public static readonly Counter BookPutCounter = Metrics
        .CreateCounter("book_put_total", "Counts requests to the PUT /book/{id} endpoint");

    public static readonly Counter BookDeleteCounter = Metrics
        .CreateCounter("book_delete_total", "Counts requests to the DELETE /book/{id} endpoint");
}