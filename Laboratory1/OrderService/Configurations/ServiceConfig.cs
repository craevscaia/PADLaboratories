namespace OrderService.Configurations
{
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
                var isDocker = Environment.GetEnvironmentVariable("DOTNET_RUNNING_IN_CONTAINER") == "true";
                var host = isDocker ? Environment.MachineName : "localhost";
                var port = Environment.GetEnvironmentVariable("ASPNETCORE_URLS")?.Split(":").Last() ?? "80";
                return $"http://{host}:{port}";
            }
        }

        public string DiscoveryUrl => _configuration["ServiceConfig:DiscoveryUrl"] ?? string.Empty;
    }
}