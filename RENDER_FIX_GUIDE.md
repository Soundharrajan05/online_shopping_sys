# 🔧 Render.com Deployment Fix Guide

## ❌ Error: "gunicorn: command not found"

This error happens when Render can't find Gunicorn or is using the wrong start command.

---

## ✅ Solution Steps

### Step 1: Verify requirements.txt

Your `requirements.txt` should include:

```
gunicorn==21.2.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

✅ **Already done!** These are in your requirements.txt.

---

### Step 2: Fix Render Start Command

The issue is Render is trying to run `gunicorn app:app` but should be `gunicorn run:app`.

**On Render Dashboard:**

1. Go to your web service
2. Click **"Settings"** or **"Environment"** tab
3. Find **"Start Command"** section
4. Change from: `gunicorn app:app`
5. Change to: **`gunicorn run:app`**
6. Click **"Save Changes"**
7. Render will automatically redeploy

---

### Step 3: Alternative - Update render.yaml

If you're using `render.yaml`, make sure it has:

```yaml
services:
  - type: web
    name: online-shopping-system
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn run:app"  # ← Make sure this is correct
```

---

### Step 4: Verify Procfile

Your `Procfile` should contain:

```
web: gunicorn run:app
```

✅ **Already correct!**

---

## 🎯 Why `run:app` and not `app:app`?

Your Flask application is in `run.py`:
```python
# run.py
from app import create_app

app = create_app('production')

if __name__ == '__main__':
    app.run()
```

So Gunicorn needs to:
- Import from `run` module (the file `run.py`)
- Get the `app` variable

Hence: `gunicorn run:app`

---

## 🔄 Complete Render Configuration

### In Render Dashboard:

**Build & Deploy Settings:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn run:app`
- **Python Version**: `3.11.0`

**Environment Variables:**
```
FLASK_ENV=production
SECRET_KEY=(generate random string)
DATABASE_URL=(from your PostgreSQL database)
PYTHON_VERSION=3.11.0
```

---

## 🐛 Still Getting Errors?

### Error: "No module named 'app'"

**Fix:** Make sure your project structure is:
```
your-project/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── templates/
│   └── ...
├── run.py
├── requirements.txt
└── Procfile
```

### Error: "Failed to find application object 'app'"

**Fix:** Check `run.py` has:
```python
app = create_app('production')
```

Not inside `if __name__ == '__main__':` block.

### Error: "ModuleNotFoundError: No module named 'gunicorn'"

**Fix:** 
1. Verify `gunicorn==21.2.0` is in requirements.txt
2. Push changes to GitHub
3. Render will reinstall dependencies

---

## 📋 Quick Checklist

- [ ] `gunicorn==21.2.0` in requirements.txt
- [ ] Start command is `gunicorn run:app` (not `gunicorn app:app`)
- [ ] `run.py` exists in project root
- [ ] `app/` folder exists with `__init__.py`
- [ ] Changes pushed to GitHub
- [ ] Render redeployed

---

## 🚀 After Fixing

1. Save changes
2. Push to GitHub:
   ```bash
   git add .
   git commit -m "Fix Gunicorn start command"
   git push origin main
   ```
3. Render will auto-deploy
4. Check logs for success
5. Visit your site URL

---

## 📞 Still Need Help?

Check Render logs:
1. Go to your web service
2. Click **"Logs"** tab
3. Look for the actual error message
4. Share the error here for more help

---

**Most common fix: Change start command to `gunicorn run:app` in Render settings!** ✨
