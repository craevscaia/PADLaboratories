namespace BookService.Configurations;

public class ServiceConfig
{
    private readonly IConfiguration _configuration;

    public ServiceConfig(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    public string ServiceName => _configuration["ServiceConfig:ServiceName"] ?? string.Empty;

    public string ServiceUrl
    {
        get
        {
            var host = new Uri(_configuration["ServiceConfig:ServiceUrl"] ?? string.Empty).Host;
            var port = Environment.GetEnvironmentVariable("ASPNETCORE_URLS")?.Split(":").Last();
            return $"http://{host}:{port}";
        }
    }

    public string DiscoveryUrl => _configuration["ServiceConfig:DiscoveryUrl"] ?? string.Empty;
}