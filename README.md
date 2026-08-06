# Online Shopping System

A web-based shopping platform built with Flask and MySQL. Users can browse products, add them to cart, and place orders. Admins can manage products, categories, users and orders from a dashboard.

## What it does

- Customers can register, login, browse products, manage their cart, checkout and view order history
- Admins can add/edit/delete products and categories, view all users and update order statuses
- Passwords are hashed, all queries are parameterized, sessions are secure

## Tech stack

- **Backend**: Python / Flask
- **Database**: MySQL
- **Frontend**: HTML, Bootstrap 5, Jinja2
- **Deployment**: Vercel (serverless) + Railway MySQL

## Project structure

```
online_shopping_sys/
├── app/
│   ├── __init__.py          # app factory
│   ├── auth/                # login, register, logout
│   ├── user/                # product browsing, cart, orders
│   ├── admin/               # admin dashboard and management
│   ├── models/              # User, Product, Category, Cart, Order
│   ├── database/            # MySQL connection handler
│   ├── utils/               # validation, error handling
│   ├── templates/           # HTML templates
│   └── static/              # CSS, JS, images
├── api/
│   └── index.py             # Vercel serverless entry point
├── tests/                   # unit and integration tests
├── config.py                # dev/prod/test config
├── run.py                   # local server entry point
├── schema.sql               # database tables
├── seed_data.py             # sample data (admin + products)
├── requirements.txt
└── .env                     # environment variables (not committed)
```

## Running locally

**1. Clone and set up virtualenv**
```bash
git clone <repo-url>
cd online_shopping_sys
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

**2. Set up database**

You need a MySQL database. Update `.env` with your credentials:
```
SECRET_KEY=your-secret-key
DATABASE_URL=mysql://user:password@host:port/dbname
FLASK_CONFIG=development
```

Then run the schema and seed data:
```bash
python init_db.py
python seed_data.py
```

**3. Start the app**
```bash
python run.py
```

Open http://127.0.0.1:8080

## Default login

After running `seed_data.py`:

- Admin: `admin@shop.com` / `admin123`
- Customer: register a new account at `/auth/register`

## Deploying to Vercel

1. Push to GitHub
2. Import the repo on [vercel.com](https://vercel.com)
3. Add these environment variables in Vercel → Settings → Environment Variables:

```
SECRET_KEY=<random string>
DATABASE_URL=mysql://user:pass@host:port/dbname
FLASK_CONFIG=production
```

4. Redeploy

The `api/index.py` file is the serverless entry point Vercel uses.

## Database

Six tables: `users`, `categories`, `products`, `cart`, `orders`, `order_items`

See `schema.sql` for the full definition.

## Tests

```bash
pytest
pytest -v              # verbose
pytest --cov=app       # with coverage
```
