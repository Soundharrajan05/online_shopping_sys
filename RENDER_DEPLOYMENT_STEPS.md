# Render.com Deployment Guide - Step by Step

## Prerequisites
- GitHub account
- Render.com account (free tier available)
- Your project pushed to GitHub

## Project Structure (Already Correct ✓)
```
online_shopping_sys/
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── Procfile                  # Process file for Render
├── runtime.txt              # Python version
├── build.sh                 # Build script
├── render.yaml              # Render configuration
├── config.py                # App configuration
├── schema_postgresql.sql    # PostgreSQL schema
├── render_init.py           # Database initialization script
├── seed_data.py             # Sample data script
└── app/                     # Application package
    ├── __init__.py          # App factory
    ├── admin/               # Admin routes
    ├── auth/                # Authentication
    ├── database/            # Database modules
    ├── models/              # Data models
    ├── static/              # CSS, JS, images
    ├── templates/           # HTML templates
    ├── user/                # User routes
    └── utils/               # Utilities
```

## Step 1: Push to GitHub

1. Initialize git (if not already done):
```bash
git init
git add .
git commit -m "Initial commit for Render deployment"
```

2. Create a new repository on GitHub

3. Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

## Step 2: Create PostgreSQL Database on Render

1. Go to https://dashboard.render.com/
2. Click "New +" → "PostgreSQL"
3. Configure:
   - **Name**: `shopping-db`
   - **Database**: `shopping_system`
   - **User**: `shopping_user`
   - **Region**: Choose closest to you
   - **Plan**: Free
4. Click "Create Database"
5. Wait for database to be created (takes 1-2 minutes)
6. **IMPORTANT**: Copy the "Internal Database URL" - you'll need this

## Step 3: Create Web Service on Render

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the web service:

### Basic Settings
- **Name**: `online-shopping-system`
- **Region**: Same as your database
- **Branch**: `main`
- **Root Directory**: (leave empty)
- **Runtime**: `Python 3`

### Build & Deploy Settings
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn run:app --bind 0.0.0.0:$PORT`

### Environment Variables
Click "Add Environment Variable" for each:

| Key | Value |
|-----|-------|
| `PYTHON_VERSION` | `3.11.0` |
| `FLASK_CONFIG` | `production` |
| `SECRET_KEY` | (Click "Generate" button) |
| `DATABASE_URL` | (Paste the Internal Database URL from Step 2) |

### Advanced Settings
- **Plan**: Free
- **Auto-Deploy**: Yes

4. Click "Create Web Service"

## Step 4: Wait for Initial Deployment

- Render will now build and deploy your app
- This takes 5-10 minutes for the first deployment
- Watch the logs for any errors
- Once you see "Build successful" and "Deploy live", proceed to Step 5

## Step 5: Initialize Database

1. In your web service dashboard, click "Shell" (top right)
2. Run these commands one by one:

```bash
# Initialize database schema
python render_init.py

# Add sample data (optional but recommended)
python seed_data.py
```

3. You should see success messages for both commands

## Step 6: Test Your Application

1. Click on your app URL (e.g., `https://online-shopping-system.onrender.com`)
2. You should see the login page
3. Test with these credentials:
   - **Customer**: customer@test.com / customer123
   - **Admin**: admin@shop.com / admin123

## Common Issues & Solutions

### Issue 1: "gunicorn: command not found"
**Solution**: Make sure `gunicorn==21.2.0` is in requirements.txt

### Issue 2: "Database pool not initialized"
**Solution**: Make sure DATABASE_URL environment variable is set correctly

### Issue 3: "Build failed"
**Solution**: 
- Check that build.sh has execute permissions
- Verify all files are committed to GitHub
- Check build logs for specific error

### Issue 4: "Application Error" or 500 Error
**Solution**:
- Check the logs in Render dashboard
- Make sure you ran `python render_init.py` in the Shell
- Verify DATABASE_URL is correct

### Issue 5: "No module named 'app'"
**Solution**: Make sure your project structure matches the one shown above

## Updating Your Deployment

After making changes:

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

Render will automatically redeploy (if Auto-Deploy is enabled).

## Manual Redeploy

1. Go to your web service dashboard
2. Click "Manual Deploy" → "Deploy latest commit"

## Viewing Logs

1. Go to your web service dashboard
2. Click "Logs" tab
3. View real-time logs to debug issues

## Database Management

To access your database:
1. Go to your PostgreSQL dashboard on Render
2. Click "Connect" → "External Connection"
3. Use the provided connection details with a PostgreSQL client

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `SECRET_KEY` | Flask session encryption | (auto-generated) |
| `FLASK_CONFIG` | Configuration environment | `production` |
| `PYTHON_VERSION` | Python runtime version | `3.11.0` |

## Support

If you encounter issues:
1. Check Render logs first
2. Verify all environment variables are set
3. Ensure database initialization was successful
4. Check that your GitHub repo is up to date

## Success Checklist

- [ ] Code pushed to GitHub
- [ ] PostgreSQL database created on Render
- [ ] Web service created and deployed
- [ ] All environment variables set
- [ ] Database initialized with `render_init.py`
- [ ] Sample data loaded with `seed_data.py`
- [ ] Application accessible via Render URL
- [ ] Login works with test credentials
- [ ] Products display correctly
- [ ] Cart and checkout work

---

**Your app should now be live at**: `https://your-app-name.onrender.com`
