﻿// <auto-generated />
using BookService.Context;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

#nullable disable

namespace BookService.Migrations
{
    [DbContext(typeof(BookContext))]
    partial class BookContextModelSnapshot : ModelSnapshot
    {
        protected override void BuildModel(ModelBuilder modelBuilder)
        {
#pragma warning disable 612, 618
            modelBuilder
                .HasAnnotation("ProductVersion", "7.0.12")
                .HasAnnotation("Relational:MaxIdentifierLength", 63);

            NpgsqlModelBuilderExtensions.UseIdentityByDefaultColumns(modelBuilder);

            modelBuilder.Entity("BookService.Entities.Book", b =>
                {
                    b.Property<int>("Id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("integer");

                    NpgsqlPropertyBuilderExtensions.UseIdentityByDefaultColumn(b.Property<int>("Id"));

                    b.Property<string>("Author")
                        .IsRequired()
                        .HasColumnType("text");

                    b.Property<decimal>("Price")
                        .HasColumnType("numeric");

                    b.Property<int>("Quantity")
                        .HasColumnType("integer");

                    b.Property<string>("Title")
                        .IsRequired()
                        .HasColumnType("text");

                    b.HasKey("Id");

                    b.ToTable("Books");

                    b.HasData(
                        new
                        {
                            Id = 1,
                            Author = "F. Scott Fitzgerald",
                            Price = 10.99m,
                            Quantity = 5,
                            Title = "The Great Gatsby"
                        },
                        new
                        {
                            Id = 2,
                            Author = "Herman Melville",
                            Price = 12.99m,
                            Quantity = 3,
                            Title = "Moby Dick"
                        },
                        new
                        {
                            Id = 3,
                            Author = "George Orwell",
                            Price = 14.99m,
                            Quantity = 7,
                            Title = "1984"
                        },
                        new
                        {
                            Id = 4,
                            Author = "Harper Lee",
                            Price = 9.99m,
                            Quantity = 10,
                            Title = "To Kill a Mockingbird"
                        },
                        new
                        {
                            Id = 5,
                            Author = "Jane Austen",
                            Price = 11.99m,
                            Quantity = 2,
                            Title = "Pride and Prejudice"
                        });
                });
#pragma warning restore 612, 618
        }
    }
}
