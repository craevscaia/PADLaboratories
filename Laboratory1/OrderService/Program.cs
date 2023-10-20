using OrderService;
using OrderService.Extensions;

var builder = WebApplication.CreateBuilder(args);

// Register services and configure the application using the Startup class
var startup = new Startup(builder.Configuration);
startup.ConfigureServices(builder.Services);

var app = builder.Build();
startup.Configure(app);
app.Services.ApplyMigrations();
app.Run();