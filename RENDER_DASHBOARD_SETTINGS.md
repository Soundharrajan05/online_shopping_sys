# Render Dashboard Settings - Copy & Paste Guide

## When Creating Web Service on Render

### Basic Info
```
Name: online-shopping-system
Region: (Choose closest to you)
Branch: main
Root Directory: (leave empty)
```

### Build & Deploy
```
Runtime: Python 3
Build Command: ./build.sh
Start Command: gunicorn run:app --bind 0.0.0.0:$PORT
```

### Environment Variables
Add these one by one:

#### 1. PYTHON_VERSION
```
Key: PYTHON_VERSION
Value: 3.11.0
```

#### 2. FLASK_CONFIG
```
Key: FLASK_CONFIG
Value: production
```

#### 3. SECRET_KEY
```
Key: SECRET_KEY
Value: (Click "Generate" button - Render will create a secure random key)
```

#### 4. DATABASE_URL
```
Key: DATABASE_URL
Value: (Copy from your PostgreSQL database "Internal Database URL")
Example: postgresql://shopping_user:xxxxx@dpg-xxxxx.oregon-postgres.render.com/shopping_system
```

### Plan
```
Instance Type: Free
```

### Auto Deploy
```
Auto-Deploy: Yes (Enable)
```

---

## PostgreSQL Database Settings

### When Creating Database
```
Name: shopping-db
Database: shopping_system
User: shopping_user
Region: (Same as web service)
Plan: Free
```

### After Database is Created
1. Go to database dashboard
2. Find "Internal Database URL" 
3. Copy it (looks like: postgresql://user:pass@host/db)
4. Use this URL for the DATABASE_URL environment variable in your web service

---

## After Deployment - Shell Commands

Once your web service is deployed, click "Shell" and run:

```bash
# Initialize database
python render_init.py

# Load sample data
python seed_data.py
```

---

## Test Credentials

After deployment, test with:

**Customer Account:**
- Email: customer@test.com
- Password: customer123

**Admin Account:**
- Email: admin@shop.com
- Password: admin123

---

## Troubleshooting

### If build fails:
1. Check logs in Render dashboard
2. Verify all files are pushed to GitHub
3. Make sure build.sh has correct permissions

### If app crashes:
1. Check logs for errors
2. Verify DATABASE_URL is set correctly
3. Make sure you ran `python render_init.py`

### If database connection fails:
1. Verify DATABASE_URL matches your PostgreSQL "Internal Database URL"
2. Make sure web service and database are in the same region
3. Check that database is fully created (not still initializing)

---

## Your Project Structure is Correct ✓

```
online_shopping_sys/
├── run.py                    ✓ Entry point
├── requirements.txt          ✓ Dependencies
├── Procfile                  ✓ Start command
├── runtime.txt              ✓ Python version
├── build.sh                 ✓ Build script
├── render.yaml              ✓ Configuration
└── app/                     ✓ Application code
    ├── __init__.py
    ├── admin/
    ├── auth/
    ├── database/
    ├── models/
    ├── static/
    ├── templates/
    ├── user/
    └── utils/
```

All files are in the correct structure for Render deployment!
