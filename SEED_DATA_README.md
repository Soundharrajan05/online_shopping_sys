# Seed Data Script

This document explains how to use the seed data script for the Online Shopping System.

## Overview

The `seed_data.py` script populates the database with initial data including:
- **Admin user**: email: `admin@shop.com`, password: `admin123`
- **Categories**: Electronics, Clothing, Books
- **Sample products**: 15 products (5 per category)

## Prerequisites

1. Database must be initialized (run `python init_db.py` first)
2. Environment variables must be configured in `.env` file
3. Required Python packages must be installed (see `requirements.txt`)

## Usage

### Basic Usage

```bash
python seed_data.py
```

The script will:
1. Connect to the database using credentials from `.env`
2. Check if data already exists to avoid duplicates
3. Create admin user, categories, and products
4. Display progress and summary

### Environment Variables

The script uses the following environment variables from `.env`:
- `DB_HOST`: MySQL host (default: localhost)
- `DB_USER`: MySQL user (default: root)
- `DB_PASSWORD`: MySQL password
- `DB_NAME`: Database name (default: shopping_system)

### Running Multiple Times

The script is **idempotent** - it can be run multiple times safely. It checks if data already exists before inserting:
- If admin user exists, it skips creation
- If categories exist, it skips creation
- If products exist, it skips creation

## Seed Data Details

### Admin User
- **Name**: Admin User
- **Email**: admin@shop.com
- **Password**: admin123 (hashed using pbkdf2:sha256)
- **Role**: admin

### Categories
1. Electronics
2. Clothing
3. Books

### Sample Products

#### Electronics (5 products)
- Laptop - Dell XPS 15 ($1,299.99, Stock: 15)
- Wireless Mouse - Logitech MX Master 3 ($99.99, Stock: 50)
- Smartphone - Samsung Galaxy S23 ($799.99, Stock: 25)
- Wireless Headphones - Sony WH-1000XM5 ($399.99, Stock: 30)
- 4K Monitor - LG UltraFine 27" ($549.99, Stock: 20)

#### Clothing (5 products)
- Men's Cotton T-Shirt - Navy Blue ($24.99, Stock: 100)
- Women's Denim Jeans - Slim Fit ($59.99, Stock: 75)
- Unisex Hoodie - Gray ($44.99, Stock: 60)
- Running Shoes - Nike Air Zoom ($129.99, Stock: 40)
- Winter Jacket - Waterproof ($149.99, Stock: 35)

#### Books (5 products)
- The Pragmatic Programmer ($49.99, Stock: 45)
- Clean Code by Robert Martin ($44.99, Stock: 50)
- Design Patterns: Elements of Reusable Object-Oriented Software ($54.99, Stock: 30)
- Introduction to Algorithms ($89.99, Stock: 25)
- Python Crash Course ($39.99, Stock: 55)

## Verification

To verify the seed data was created successfully, run:

```bash
python verify_seed_data.py
```

This will display:
- Admin user details
- All categories
- All products grouped by category
- Summary counts

## Troubleshooting

### Error: Access denied for user
- Check that `.env` file exists and contains correct database credentials
- Verify MySQL server is running
- Ensure the database user has appropriate permissions

### Error: Unknown database
- Run `python init_db.py` first to create the database and schema

### Error: Duplicate entry
- This should not occur as the script checks for existing data
- If it does, the script will skip that entry and continue

## Security Notes

- The admin password is hardcoded as `admin123` for development purposes
- **IMPORTANT**: Change the admin password in production environments
- The password is properly hashed using werkzeug's `generate_password_hash` with pbkdf2:sha256

## Integration with Application

After running the seed script, you can:
1. Start the application: `python run.py`
2. Login as admin: email `admin@shop.com`, password `admin123`
3. Browse products as a customer (register a new account)
4. Manage products, categories, and orders as admin

## Customization

To customize the seed data:
1. Edit the `products` list in the `create_sample_products()` function
2. Modify the `categories` list in the `create_categories()` function
3. Update admin credentials in the `create_admin_user()` function

## Related Scripts

- `init_db.py`: Initialize database and create schema
- `verify_seed_data.py`: Verify seed data was created correctly
- `schema.sql`: Database schema definition
