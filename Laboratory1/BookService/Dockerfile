FROM mcr.microsoft.com/dotnet/aspnet:6.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /src
COPY ["BookService.csproj", "BookService/"]
RUN dotnet restore "BookService/BookService.csproj"
COPY . BookService
WORKDIR "/src/BookService"
RUN dotnet build "BookService.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "BookService.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "BookService.dll"]