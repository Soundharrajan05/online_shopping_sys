# Debug Guide for Render Deployment Issues

## Current Issues
1. Login not working
2. Registration not working  
3. No products displaying

## New Debug Endpoints Added

I've added three powerful debug endpoints to help diagnose and fix issues:

### 1. `/test-db` - Enhanced Database Status
Shows:
- All users (not just 5)
- Categories count
- Products count
- Quick links to fix issues

### 2. `/debug-login` - Login Diagnostics
Shows:
- All users in database
- Tests common passwords against each user
- Reveals which password works for each account
- Helps identify password hash issues

### 3. `/debug-register` - Registration Testing
- Test registration with any email
- Shows detailed error messages
- Bypasses validation to test database directly
- Creates users and shows success/failure

## Step-by-Step Fix Process

### Step 1: Push Changes to GitHub
```bash
git add app/__init__.py
git commit -m "Add debug endpoints for login and registration issues"
git push origin main
```

### Step 2: Wait for Render Redeploy
- Go to your Render dashboard
- Wait 5-10 minutes for automatic redeploy
- Check logs for "Database connection pool initialized (postgresql)"

### Step 3: Run Diagnostics

#### A. Check Database Status
Visit: `https://online-shopping-sys.onrender.com/test-db`

Expected output:
```
✓ Database connected: PostgreSQL 18.3...
✓ Found 6 tables: cart, categories, order_items, orders, products, users
✓ Users table has 10 users

All users:
  1. soundharrajan151@gmail.com (customer) - [name]
  2. soundharrajank129@gmail.com (customer) - [name]
  ...
  
✓ Categories: 0
  Click to add categories and products
  
✓ Products: 0
  Click to add products
```

#### B. Test Login Passwords
Visit: `https://online-shopping-sys.onrender.com/debug-login`

This will show:
- All users with their emails
- Which password works for each user
- If passwords are correctly hashed

**Expected Result:**
- Should find users with passwords: `customer123`, `admin123`, etc.
- If NO passwords match, there's a password hashing issue

#### C. Test Registration
Visit: `https://online-shopping-sys.onrender.com/debug-register`

Try registering with:
- Email: `testuser@example.com`
- Name: `Test User`
- Password: `test123`

**Expected Result:**
- Should create user successfully
- Should show "User created successfully! User ID: [number]"
- If it fails, will show detailed error message

### Step 4: Add Categories and Products
Visit: `https://online-shopping-sys.onrender.com/add-products`

This will:
1. Add 3 categories (Electronics, Books, Clothing)
2. Add 10 products with images
3. Show success message

### Step 5: Test Normal Login
Visit: `https://online-shopping-sys.onrender.com/auth/login`

Try logging in with credentials found in `/debug-login`

## Common Issues and Solutions

### Issue 1: "10 users but only 5 shown"
**Cause:** Old `/test-db` used `LIMIT 5`
**Solution:** New version shows ALL users

### Issue 2: Login fails with correct password
**Possible Causes:**
1. Password hash algorithm mismatch
2. Passwords were created with different method
3. Database was reset but passwords weren't

**Solution:** Use `/debug-login` to find working passwords

### Issue 3: Registration fails silently
**Possible Causes:**
1. Email already exists (duplicate)
2. Database constraint violation
3. Password hashing error

**Solution:** Use `/debug-register` to see exact error

### Issue 4: No products display
**Cause:** Categories table is empty
**Solution:** Visit `/add-products` to populate

## What Each Debug Endpoint Does

### `/test-db`
- **Purpose:** Quick health check
- **Shows:** Database connection, tables, users, categories, products
- **Use when:** You want to see overall status

### `/debug-login`
- **Purpose:** Diagnose login issues
- **Shows:** All users and tests passwords
- **Use when:** Login fails with "correct" credentials

### `/debug-register`
- **Purpose:** Test registration directly
- **Shows:** Detailed error messages
- **Use when:** Registration fails with generic error

## Security Note

⚠️ **IMPORTANT:** These debug endpoints expose sensitive information!

After fixing issues, you should:
1. Remove or disable these endpoints in production
2. Or add authentication to protect them

To disable, comment out these routes in `app/__init__.py`:
```python
# @app.route('/debug-login')
# @app.route('/debug-register', methods=['GET', 'POST'])
```

## Next Steps After Debugging

Once you identify the issue:

1. **If passwords don't work:** Database needs to be reseeded with correct password hashes
2. **If registration fails:** Check error message from `/debug-register`
3. **If products missing:** Run `/add-products`
4. **If all works:** Remove debug endpoints for security

## Quick Reference

| Endpoint | Purpose | Method |
|----------|---------|--------|
| `/test-db` | Database status | GET |
| `/debug-login` | Test login passwords | GET |
| `/debug-register` | Test registration | GET/POST |
| `/add-products` | Add categories & products | GET |
| `/init-db` | Initialize database | GET |

## Contact Points

If issues persist after using debug endpoints:
1. Check Render logs for errors
2. Verify DATABASE_URL is set correctly
3. Ensure PostgreSQL database is running
4. Check if database has enough storage space (free tier limit)
