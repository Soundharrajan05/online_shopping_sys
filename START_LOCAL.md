# Quick Start — Run Locally

## Prerequisites

1. **Python 3.8+** installed
2. **MySQL 5.7+** installed and running
3. Git (optional, for version control)

---

## Step 1: Install MySQL (if not installed)

### Windows
Download from: https://dev.mysql.com/downloads/installer/

OR install via Chocolatey:
```cmd
choco install mysql
```

### Verify MySQL is running
```cmd
mysql --version
```

---

## Step 2: Create Virtual Environment

```cmd
cd d:\online_shopping_sys
python -m venv venv
venv\Scripts\activate
```

---

## Step 3: Install Dependencies

```cmd
pip install -r requirements.txt
```

---

## Step 4: Setup MySQL Database

Open MySQL command line:
```cmd
mysql -u root -p
```

Run these commands:
```sql
CREATE DATABASE shopping_system;
USE shopping_system;
SOURCE d:\online_shopping_sys\schema.sql;
EXIT;
```

OR use init_db.py:
```cmd
python init_db.py
```

---

## Step 5: (Optional) Add Sample Data

```cmd
python seed_data.py
```

This creates:
- Admin user: `admin@shop.com` / `admin123`
- Sample products and categories

---

## Step 6: Update .env File

The `.env` file is already configured for localhost. Just verify these values:

```env
FLASK_CONFIG=development
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=          # Your MySQL root password (leave empty if none)
DB_NAME=shopping_system
```

---

## Step 7: Run the App

```cmd
python run.py
```

You should see:
```
MySQL database connection initialised.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

Open **http://localhost:5000** in your browser.

---

## Default Login Credentials (after running seed_data.py)

**Admin:**
- Email: `admin@shop.com`
- Password: `admin123`

**Test Customer:**
- Register a new account at http://localhost:5000/auth/register

---

## Common Issues

### "Can't connect to MySQL server"
- Make sure MySQL is running: `mysql --version`
- Check `.env` has correct `DB_PASSWORD`

### "Database 'shopping_system' doesn't exist"
- Run: `python init_db.py` OR `mysql -u root -p -e "CREATE DATABASE shopping_system;"`

### "Module not found" errors
- Activate venv: `venv\Scripts\activate`
- Install deps: `pip install -r requirements.txt`

### Port 5000 already in use
- Change port in `run.py`: `app.run(port=5001)`

---

## Stop the Server

Press `Ctrl+C` in the terminal.
