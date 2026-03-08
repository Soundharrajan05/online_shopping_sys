# Fix Login & Signup Issues on Render

## Common Causes

1. Database not initialized (tables don't exist)
2. SECRET_KEY not set properly
3. Database connection issues
4. Missing sample data

---

## ✅ Step-by-Step Fix

### Step 1: Check if Database is Initialized

The most common issue is that the database tables haven't been created yet.

#### In Render Dashboard:

1. Go to your web service
2. Click **"Shell"** (top right corner)
3. Wait for shell to open
4. Run this command:

```bash
python render_init.py
```

**Expected Output:**
```
======================================================================
Initializing Database for Render.com
======================================================================

1. Reading schema file...
2. Creating tables...
   ✓ Executed: CREATE TABLE users...
   ✓ Executed: CREATE TABLE categories...
   ✓ Executed: CREATE TABLE products...
   ✓ Executed: CREATE TABLE cart...
   ✓ Executed: CREATE TABLE orders...
   ✓ Executed: CREATE TABLE order_items...

======================================================================
Database initialized successfully!
======================================================================
```

If you see errors, tell me what they are!

### Step 2: Add Sample Data

After initializing the database, add sample users and products:

```bash
python seed_data.py
```

**Expected Output:**
```
======================================================================
Seeding Database with Sample Data
======================================================================

1. Creating categories...
   ✓ Electronics
   ✓ Books
   ✓ Clothing

2. Creating admin user...
   ✓ Admin: admin@shop.com

3. Creating customer user...
   ✓ Customer: customer@test.com

4. Creating products...
   ✓ 15 products created

======================================================================
Database seeded successfully!
======================================================================
```

### Step 3: Test Login

Now try logging in with these credentials:

**Customer Account:**
- Email: `customer@test.com`
- Password: `customer123`

**Admin Account:**
- Email: `admin@shop.com`
- Password: `admin123`

---

## If Still Not Working - Check Environment Variables

### Step 1: Verify Environment Variables

In Render Dashboard → Your Web Service → Environment:

Make sure these are set:

| Variable | Value | Status |
|----------|-------|--------|
| `DATABASE_URL` | `postgresql://...` | ✓ Must be set |
| `SECRET_KEY` | (random string) | ✓ Must be set |
| `FLASK_CONFIG` | `production` | ✓ Must be set |
| `PYTHON_VERSION` | `3.11.9` | ✓ Must be set |

### Step 2: Check SECRET_KEY

If SECRET_KEY is missing or wrong:

1. Go to Environment tab
2. Find `SECRET_KEY`
3. If missing, click "Add Environment Variable"
4. Key: `SECRET_KEY`
5. Value: Click "Generate" button
6. Save

**Important**: After changing environment variables, Render will redeploy automatically.

---

## Specific Error Messages

### Error: "Invalid credentials" or "User not found"

**Cause**: Database not initialized or no users exist

**Fix**:
```bash
# In Render Shell
python render_init.py
python seed_data.py
```

### Error: "Internal Server Error" or 500 Error

**Cause**: Database connection issue or SECRET_KEY missing

**Fix**:
1. Check DATABASE_URL is set correctly
2. Check SECRET_KEY is set
3. Check logs for specific error

### Error: "Cannot connect to database"

**Cause**: DATABASE_URL is wrong or database not created

**Fix**:
1. Go to PostgreSQL database dashboard
2. Copy "Internal Database URL"
3. Update DATABASE_URL in web service environment variables
4. Make sure web service and database are in same region

### Error: Signup form doesn't submit

**Cause**: Email validation or password requirements

**Fix**: Make sure:
- Email is valid format (e.g., user@example.com)
- Password is at least 8 characters
- All required fields are filled

### Error: "Session expired" or keeps logging out

**Cause**: SECRET_KEY changes between deployments

**Fix**:
1. Set SECRET_KEY as environment variable (don't use default)
2. Use "Generate" button in Render to create a stable key
3. Don't change SECRET_KEY after setting it

---

## Check Render Logs

### How to View Logs:

1. Go to your web service dashboard
2. Click "Logs" tab
3. Look for errors

### Common Log Errors:

#### "Table 'users' doesn't exist"
**Fix**: Run `python render_init.py`

#### "Database pool not initialized"
**Fix**: Check DATABASE_URL is set

#### "Invalid password hash"
**Fix**: Run `python seed_data.py` to recreate users

#### "Connection refused"
**Fix**: Check DATABASE_URL uses "Internal Database URL"

---

## Manual Database Check

### Verify Tables Exist:

In Render Shell:

```bash
python
```

Then in Python:

```python
from app import create_app
from app.database.db_universal import Database

app = create_app('production')
with app.app_context():
    conn = Database.get_connection()
    cursor = conn.cursor()
    
    # Check if users table exists
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"Users in database: {count}")
    
    cursor.close()
    Database.release_connection(conn)
```

**Expected Output:**
```
Users in database: 2
```

If you get an error, the tables don't exist. Run `python render_init.py`.

---

## Complete Reset (If Nothing Works)

### Option 1: Reinitialize Database

```bash
# In Render Shell
python render_init.py
python seed_data.py
```

### Option 2: Recreate Database

1. Delete the PostgreSQL database on Render
2. Create a new one
3. Copy the new DATABASE_URL
4. Update web service environment variable
5. Run `python render_init.py`
6. Run `python seed_data.py`

---

## Test Checklist

After fixing, verify these work:

- [ ] Can access the website
- [ ] Login page loads
- [ ] Can login with customer@test.com / customer123
- [ ] Can login with admin@shop.com / admin123
- [ ] Can signup with new email
- [ ] Can browse products after login
- [ ] Can logout
- [ ] Can login again

---

## Quick Fix Commands

Run these in Render Shell (in order):

```bash
# 1. Initialize database
python render_init.py

# 2. Add sample data
python seed_data.py

# 3. Verify users exist
python -c "from app import create_app; from app.database.db_universal import Database; app = create_app('production'); app.app_context().push(); conn = Database.get_connection(); cursor = conn.cursor(); cursor.execute('SELECT email FROM users'); print([row[0] for row in cursor.fetchall()])"
```

**Expected Output:**
```
['admin@shop.com', 'customer@test.com']
```

---

## Still Having Issues?

Tell me:

1. **What error message do you see?**
   - On the website
   - In Render logs

2. **What happens when you try to login?**
   - Page refreshes but nothing happens?
   - Error message appears?
   - Redirects somewhere?

3. **Did you run these commands?**
   - `python render_init.py` - Yes/No
   - `python seed_data.py` - Yes/No

4. **Environment variables set?**
   - DATABASE_URL - Yes/No
   - SECRET_KEY - Yes/No

I'll help you debug further!

---

## Most Likely Solution

**90% of the time, the issue is:**

Database tables don't exist because you didn't run:

```bash
python render_init.py
python seed_data.py
```

**Run these commands in Render Shell now!**
