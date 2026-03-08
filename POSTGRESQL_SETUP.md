# 🐘 PostgreSQL Connection String Setup Guide

This guide explains how to configure your application to use PostgreSQL with a connection string.

---

## 📋 Connection String Format

```
postgresql://username:password@host:5432/database
```

### Components:

- **username**: Your PostgreSQL username
- **password**: Your PostgreSQL password
- **host**: Database server hostname (e.g., `localhost`, `db.example.com`)
- **5432**: PostgreSQL default port (change if using different port)
- **database**: Database name

---

## 🔧 Setup Options

### Option 1: Local PostgreSQL (Development)

#### Step 1: Install PostgreSQL

**Windows:**
- Download from: https://www.postgresql.org/download/windows/
- Run installer
- Remember the password you set for `postgres` user

**Mac:**
```bash
brew install postgresql
brew services start postgresql
```

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### Step 2: Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE shopping_system;

# Create user (optional)
CREATE USER shopping_user WITH PASSWORD 'your_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE shopping_system TO shopping_user;

# Exit
\q
```

#### Step 3: Configure .env File

Create a `.env` file in your project root:

```env
# PostgreSQL Connection String
DATABASE_URL=postgresql://shopping_user:your_password@localhost:5432/shopping_system

# Or if using default postgres user:
DATABASE_URL=postgresql://postgres:your_postgres_password@localhost:5432/shopping_system

# Flask Configuration
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
```

#### Step 4: Initialize Database

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database schema
python render_init.py

# Seed sample data
python seed_data.py

# Run application
python run.py
```

---

### Option 2: Remote PostgreSQL (Production)

#### Popular PostgreSQL Hosting Services:

1. **Render.com** (Free tier)
   - Automatic DATABASE_URL provided
   - No manual configuration needed

2. **ElephantSQL** (Free tier)
   - Go to https://www.elephantsql.com/
   - Create free instance
   - Copy connection URL

3. **Supabase** (Free tier)
   - Go to https://supabase.com/
   - Create project
   - Get connection string from settings

4. **Neon** (Free tier)
   - Go to https://neon.tech/
   - Create project
   - Copy connection string

#### Configuration:

```env
# Use the connection string provided by your hosting service
DATABASE_URL=postgresql://user:pass@host.example.com:5432/dbname

# Flask Configuration
SECRET_KEY=your-production-secret-key
FLASK_ENV=production
```

---

## 🔄 Switching Between MySQL and PostgreSQL

The application automatically detects which database to use:

### Use PostgreSQL:
```env
DATABASE_URL=postgresql://username:password@host:5432/database
```

### Use MySQL:
```env
# Comment out or remove DATABASE_URL
# DB_HOST=localhost
# DB_USER=root
# DB_PASSWORD=your_password
# DB_NAME=shopping_system
```

---

## 🧪 Testing Your Connection

Create a test file `test_db_connection.py`:

```python
import os
from dotenv import load_dotenv
from app import create_app
from app.database.db_universal import Database

load_dotenv()

app = create_app('development')

with app.app_context():
    try:
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected to PostgreSQL!")
        print(f"Version: {version[0]}")
        cursor.close()
        Database.release_connection(conn)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
```

Run it:
```bash
python test_db_connection.py
```

---

## 🔐 Security Best Practices

### 1. Never Commit .env File

Ensure `.env` is in `.gitignore`:
```
.env
.env.local
.env.*.local
```

### 2. Use Strong Passwords

```bash
# Generate a strong password
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Use Environment Variables in Production

Don't hardcode credentials. Use platform environment variables:
- Render.com: Automatically provides DATABASE_URL
- Heroku: Set via dashboard or CLI
- Other platforms: Use their environment variable system

---

## 🐛 Troubleshooting

### Error: "could not connect to server"

**Solution:**
1. Check PostgreSQL is running:
   ```bash
   # Windows
   services.msc (look for PostgreSQL)
   
   # Mac
   brew services list
   
   # Linux
   sudo systemctl status postgresql
   ```

2. Verify connection string format
3. Check firewall settings
4. Verify host/port are correct

### Error: "password authentication failed"

**Solution:**
1. Verify username and password
2. Check PostgreSQL user exists:
   ```bash
   psql -U postgres -c "\du"
   ```
3. Reset password if needed:
   ```sql
   ALTER USER username WITH PASSWORD 'newpassword';
   ```

### Error: "database does not exist"

**Solution:**
```bash
psql -U postgres -c "CREATE DATABASE shopping_system;"
```

### Error: "psycopg2 not installed"

**Solution:**
```bash
pip install psycopg2-binary
```

---

## 📊 Connection String Examples

### Local Development:
```
postgresql://postgres:admin123@localhost:5432/shopping_system
```

### Render.com (Auto-provided):
```
postgresql://user:pass@dpg-xxxxx.oregon-postgres.render.com/dbname
```

### ElephantSQL:
```
postgresql://user:pass@jelani.db.elephantsql.com:5432/dbname
```

### Supabase:
```
postgresql://postgres:pass@db.xxxxx.supabase.co:5432/postgres
```

### Custom Server:
```
postgresql://myuser:mypass@192.168.1.100:5432/shopping_db
```

---

## ✅ Quick Start Checklist

- [ ] PostgreSQL installed and running
- [ ] Database created
- [ ] User created (optional)
- [ ] `.env` file created with DATABASE_URL
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database initialized (`python render_init.py`)
- [ ] Sample data seeded (`python seed_data.py`)
- [ ] Application running (`python run.py`)
- [ ] Can access http://localhost:5000

---

## 🎯 Example: Complete Local Setup

```bash
# 1. Install PostgreSQL (if not installed)
# Download from postgresql.org

# 2. Create database
psql -U postgres
CREATE DATABASE shopping_system;
CREATE USER shop_user WITH PASSWORD 'shop_pass_123';
GRANT ALL PRIVILEGES ON DATABASE shopping_system TO shop_user;
\q

# 3. Create .env file
echo "DATABASE_URL=postgresql://shop_user:shop_pass_123@localhost:5432/shopping_system" > .env
echo "SECRET_KEY=dev-secret-key" >> .env
echo "FLASK_ENV=development" >> .env

# 4. Setup application
pip install -r requirements.txt
python render_init.py
python seed_data.py

# 5. Run application
python run.py

# 6. Open browser
# http://localhost:5000
```

---

## 🆘 Need Help?

- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Connection String Format**: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING
- **psycopg2 Documentation**: https://www.psycopg.org/docs/

---

**Your application is now configured to work with PostgreSQL!** 🎉
