# 🚀 Deployment Guide - Online Shopping System

This guide will help you deploy your Online Shopping System to **Render.com** (FREE tier).

---

## 📋 Prerequisites

1. **GitHub Account** - Create one at https://github.com if you don't have one
2. **Render.com Account** - Sign up at https://render.com (free)
3. **Git installed** on your computer

---

## 🔧 Step 1: Prepare Your Project

### 1.1 Initialize Git Repository (if not already done)

```bash
git init
git add .
git commit -m "Initial commit - Online Shopping System"
```

### 1.2 Create .gitignore file

Make sure you have a `.gitignore` file with:

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
.venv
*.db
*.sqlite3
.hypothesis/
.pytest_cache/
.coverage
htmlcov/
```

### 1.3 Push to GitHub

```bash
# Create a new repository on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

---

## 🌐 Step 2: Deploy to Render.com

### 2.1 Sign Up / Log In to Render

1. Go to https://render.com
2. Sign up with GitHub (recommended) or email
3. Authorize Render to access your GitHub repositories

### 2.2 Create a New Web Service

1. Click **"New +"** button in the top right
2. Select **"Web Service"**
3. Connect your GitHub repository
4. Select your **online-shopping-system** repository

### 2.3 Configure Web Service

Fill in the following settings:

**Basic Settings:**
- **Name**: `online-shopping-system` (or your preferred name)
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn run:app`

**Instance Type:**
- Select **"Free"** tier

### 2.4 Add Environment Variables

Click **"Advanced"** and add these environment variables:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Generate a random string (click "Generate" button) |
| `PYTHON_VERSION` | `3.11.0` |

### 2.5 Create PostgreSQL Database

1. Go back to Render Dashboard
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `shopping-db`
   - **Database**: `shopping_system`
   - **User**: `shopping_user`
   - **Region**: Same as your web service
   - **Instance Type**: **Free**
4. Click **"Create Database"**

### 2.6 Link Database to Web Service

1. Go to your web service settings
2. In **Environment** section, add:
   - **Key**: `DATABASE_URL`
   - **Value**: Click "Add from Database" → Select `shopping-db` → Select "Internal Database URL"

### 2.7 Deploy!

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start your application
3. Wait 2-5 minutes for deployment to complete

---

## 🗄️ Step 3: Initialize Database

### 3.1 Access Render Shell

1. Go to your web service dashboard
2. Click **"Shell"** tab
3. A terminal will open

### 3.2 Run Database Setup

In the Render shell, run:

```bash
# Create tables
python -c "
from app import create_app
from app.database.db_universal import Database
import psycopg2

app = create_app('production')
with app.app_context():
    # Read and execute PostgreSQL schema
    with open('schema_postgresql.sql', 'r') as f:
        schema = f.read()
    
    conn = Database.get_connection()
    cursor = conn.cursor()
    cursor.execute(schema)
    conn.commit()
    cursor.close()
    Database.release_connection(conn)
    print('Database initialized!')
"

# Seed data
python seed_data.py
```

---

## ✅ Step 4: Test Your Deployment

1. Render will provide you with a URL like: `https://online-shopping-system.onrender.com`
2. Open the URL in your browser
3. You should see the login page!

### Default Credentials:

**Admin Account:**
- Email: `admin@shop.com`
- Password: `admin123`

**Test Customer:**
- Email: `customer@test.com`
- Password: `customer123`

---

## 🔧 Troubleshooting

### Issue: "Application failed to start"

**Solution:**
1. Check the **Logs** tab in Render dashboard
2. Look for error messages
3. Common issues:
   - Missing environment variables
   - Database connection errors
   - Python version mismatch

### Issue: "Database connection failed"

**Solution:**
1. Verify `DATABASE_URL` is set correctly
2. Make sure PostgreSQL database is running
3. Check database is in the same region as web service

### Issue: "502 Bad Gateway"

**Solution:**
1. Check if the app is still deploying (wait a few minutes)
2. Check logs for startup errors
3. Verify `gunicorn run:app` command is correct

---

## 🔄 Updating Your Deployment

To update your deployed application:

```bash
# Make your changes locally
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically detect the push and redeploy!

---

## 💰 Cost Information

**Render.com Free Tier Includes:**
- ✅ 750 hours/month of web service runtime
- ✅ Free PostgreSQL database (90 days, then $7/month)
- ✅ Automatic HTTPS
- ✅ Automatic deployments from GitHub
- ⚠️ Services spin down after 15 minutes of inactivity (first request may be slow)

**To keep service always running:**
- Upgrade to paid plan ($7/month)

---

## 📚 Additional Resources

- **Render Documentation**: https://render.com/docs
- **Flask Deployment Guide**: https://flask.palletsprojects.com/en/latest/deploying/
- **PostgreSQL on Render**: https://render.com/docs/databases

---

## 🎉 Success!

Your Online Shopping System is now live and accessible to anyone with the URL!

**Next Steps:**
1. Share your URL with others
2. Register new customer accounts
3. Test the shopping flow
4. Customize products and categories via admin panel

**Need Help?**
- Check Render logs for errors
- Review this guide
- Check Render community forums

---

## 🔐 Security Notes for Production

Before going live with real users:

1. **Change default passwords** for admin and test accounts
2. **Use strong SECRET_KEY** (Render generates this automatically)
3. **Enable HTTPS** (Render provides this automatically)
4. **Set up database backups** (available in Render dashboard)
5. **Monitor application logs** regularly
6. **Keep dependencies updated** (`pip list --outdated`)

---

**Congratulations! Your e-commerce platform is now deployed! 🎊**
