using BookService;
using BookService.Extensions;

var builder = WebApplication.CreateBuilder(args);

// Register services and configure the application using the Startup class
var startup = new Startup(builder.Environment);
startup.ConfigureServices(builder.Services);

var app = builder.Build();
startup.Configure(app);
app.Services.ApplyMigrations();
await app.Services.RegisterToServiceDiscovery(builder.Configuration);
app.Run();