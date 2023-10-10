# Use the official Microsoft .NET SDK image as the base image
FROM mcr.microsoft.com/dotnet/aspnet:7.0 AS base
WORKDIR /app
EXPOSE 80

# Use the SDK image to build the app
FROM mcr.microsoft.com/dotnet/sdk:7.0 AS build
WORKDIR /src
COPY BookService.csproj .
RUN dotnet restore "BookService.csproj"
COPY . .
WORKDIR "/src/BookService"
RUN dotnet build "BookService.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "BookService.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "BookService.dll"]
