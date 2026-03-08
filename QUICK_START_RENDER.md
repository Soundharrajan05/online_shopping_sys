# Quick Start - Deploy to Render in 10 Minutes

## Your Structure is Already Correct ✓

```
online_shopping_sys/
├── run.py              ✓
├── requirements.txt    ✓
├── Procfile           ✓
├── runtime.txt        ✓
└── app/               ✓
    └── __init__.py    ✓
```

## Step 1: Push to GitHub (2 minutes)

```bash
git add .
git commit -m "Deploy to Render"
git push origin main
```

## Step 2: Create Database (2 minutes)

1. Go to https://dashboard.render.com/
2. Click **New +** → **PostgreSQL**
3. Settings:
   - Name: `shopping-db`
   - Database: `shopping_system`
   - Plan: **Free**
4. Click **Create Database**
5. **Copy the "Internal Database URL"** (you'll need this!)

## Step 3: Create Web Service (3 minutes)

1. Click **New +** → **Web Service**
2. Connect your GitHub repo
3. Settings:
   - Name: `online-shopping-system`
   - Build Command: `./build.sh`
   - Start Command: `gunicorn run:app --bind 0.0.0.0:$PORT`
   - Plan: **Free**

4. **Environment Variables** (click "Add Environment Variable"):
   ```
   PYTHON_VERSION = 3.11.0
   FLASK_CONFIG = production
   SECRET_KEY = (click "Generate")
   DATABASE_URL = (paste the URL from Step 2)
   ```

5. Click **Create Web Service**

## Step 4: Initialize Database (3 minutes)

Wait for deployment to complete, then:

1. Click **Shell** (top right)
2. Run:
   ```bash
   python render_init.py
   python seed_data.py
   ```

## Step 5: Test! (1 minute)

1. Click your app URL
2. Login with:
   - Email: `customer@test.com`
   - Password: `customer123`

## Done! 🎉

Your app is now live at: `https://your-app-name.onrender.com`

---

## Need Help?

- **Detailed Guide**: See RENDER_DEPLOYMENT_STEPS.md
- **Exact Settings**: See RENDER_DASHBOARD_SETTINGS.md
- **Verify Files**: Run `python verify_deployment_files.py`

## Troubleshooting

**Build fails?**
- Check that all files are pushed to GitHub
- Verify build.sh exists

**App crashes?**
- Make sure DATABASE_URL is set correctly
- Check that you ran `python render_init.py`

**Database error?**
- Verify DATABASE_URL matches your PostgreSQL "Internal Database URL"
- Make sure database is fully created (not initializing)
