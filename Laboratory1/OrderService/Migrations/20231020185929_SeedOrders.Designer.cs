﻿// <auto-generated />
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Migrations;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;
using OrderService.Context;

#nullable disable

namespace OrderService.Migrations
{
    [DbContext(typeof(OrderContext))]
    [Migration("20231020185929_SeedOrders")]
    partial class SeedOrders
    {
        /// <inheritdoc />
        protected override void BuildTargetModel(ModelBuilder modelBuilder)
        {
#pragma warning disable 612, 618
            modelBuilder
                .HasAnnotation("ProductVersion", "7.0.12")
                .HasAnnotation("Relational:MaxIdentifierLength", 63);

            NpgsqlModelBuilderExtensions.UseIdentityByDefaultColumns(modelBuilder);

            modelBuilder.Entity("OrderService.Entities.Order", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("integer");

                    NpgsqlPropertyBuilderExtensions.UseIdentityByDefaultColumn(b.Property<int>("Id"));

                    b.Property<int>("BookId")
                        .HasColumnType("integer");

                    b.Property<int>("Quantity")
                        .HasColumnType("integer");

                    b.Property<decimal>("TotalPrice")
                        .HasColumnType("numeric");

                    b.HasKey("Id");

                    b.ToTable("Orders");

                    b.HasData(
                        new
                        {
                            Id = 1,
                            BookId = 1,
                            Quantity = 2,
                            TotalPrice = 21.98m
                        },
                        new
                        {
                            Id = 2,
                            BookId = 2,
                            Quantity = 1,
                            TotalPrice = 12.99m
                        },
                        new
                        {
                            Id = 3,
                            BookId = 3,
                            Quantity = 3,
                            TotalPrice = 44.97m
                        },
                        new
                        {
                            Id = 4,
                            BookId = 4,
                            Quantity = 1,
                            TotalPrice = 9.99m
                        },
                        new
                        {
                            Id = 5,
                            BookId = 5,
                            Quantity = 2,
                            TotalPrice = 23.98m
                        });
                });
#pragma warning restore 612, 618
        }
    }
}
