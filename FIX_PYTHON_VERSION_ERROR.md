# Fix Python Version Error on Render

## Error You're Seeing

```
undefined symbol: _PyInterpreterState_Get
```

This happens because Render is using Python 3.14 (too new), but psycopg2-binary doesn't support it yet.

---

## ✅ Solution: Force Python 3.11.9

### Step 1: Verify runtime.txt

Your `runtime.txt` file should contain:

```
python-3.11.9
```

I've already updated this file for you! ✓

### Step 2: Verify requirements.txt

Your `requirements.txt` should have:

```
psycopg2-binary==2.9.10
```

I've already updated this too! ✓

### Step 3: Push Changes to GitHub

Now you need to push these changes to GitHub so Render can rebuild:

#### Using GitHub Desktop:

1. Open GitHub Desktop
2. You'll see 2 changed files:
   - `runtime.txt`
   - `requirements.txt`
3. At the bottom left:
   - Summary: `Fix Python version for Render`
   - Description: `Force Python 3.11.9 and update psycopg2-binary`
4. Click **"Commit to main"**
5. Click **"Push origin"** (top bar)

#### Using Git Command Line:

```bash
git add runtime.txt requirements.txt
git commit -m "Fix Python version for Render"
git push origin main
```

### Step 4: Render Will Auto-Rebuild

- Render will detect the changes
- It will automatically rebuild your app
- This time it will use Python 3.11.9
- The error should be gone!

---

## Understanding the Fix

### What Changed:

**runtime.txt** (before):
```
python-3.11.0
```

**runtime.txt** (after):
```
python-3.11.9
```

**requirements.txt** (before):
```
psycopg2-binary==2.9.9
```

**requirements.txt** (after):
```
psycopg2-binary==2.9.10
```

### Why This Works:

1. **Python 3.11.9** is a stable version that psycopg2-binary fully supports
2. **psycopg2-binary 2.9.10** is the latest version with better compatibility
3. Render reads `runtime.txt` and uses the specified Python version
4. The combination of Python 3.11.9 + psycopg2-binary 2.9.10 works perfectly

---

## About Database Drivers

Your app needs BOTH database drivers:

### mysql-connector-python
- ✓ For local development (your Windows machine)
- ✓ Connects to MySQL on localhost

### psycopg2-binary
- ✓ For Render deployment (production)
- ✓ Connects to PostgreSQL on Render

### How It Works:

Your `db_universal.py` automatically detects which database to use:

```python
# If DATABASE_URL exists (Render) → Use PostgreSQL
if database_url:
    cls._db_type = 'postgresql'
    cls._init_postgresql(database_url)
else:
    # If no DATABASE_URL (local) → Use MySQL
    cls._db_type = 'mysql'
    cls._init_mysql(config)
```

**Don't remove either database driver!** Both are needed.

---

## Verification

After pushing changes and Render rebuilds:

### Check Build Logs:

You should see:
```
-----> Python app detected
-----> Using Python version specified in runtime.txt
-----> Python 3.11.9
-----> Installing dependencies
       Collecting psycopg2-binary==2.9.10
       Successfully installed psycopg2-binary-2.9.10
```

### Check App Logs:

You should see:
```
Database connection pool initialized (postgresql)
```

No more `undefined symbol` errors!

---

## If Error Persists

### Option 1: Manual Redeploy

1. Go to Render dashboard
2. Click your web service
3. Click "Manual Deploy" → "Clear build cache & deploy"

### Option 2: Check Environment Variables

Make sure these are set in Render:

| Variable | Value |
|----------|-------|
| `PYTHON_VERSION` | `3.11.9` |
| `DATABASE_URL` | `postgresql://...` |
| `FLASK_CONFIG` | `production` |
| `SECRET_KEY` | (generated) |

### Option 3: Verify runtime.txt Format

Make sure `runtime.txt` has:
- No extra spaces
- No extra lines
- Exactly: `python-3.11.9`

---

## Summary of Changes

✓ Updated `runtime.txt` to Python 3.11.9
✓ Updated `psycopg2-binary` to 2.9.10
✓ Both database drivers kept (MySQL + PostgreSQL)

**Next Step**: Push changes to GitHub and let Render rebuild!

---

## Quick Commands

### Push Changes:

**GitHub Desktop**:
1. Commit changes
2. Push origin

**Git CLI**:
```bash
git add .
git commit -m "Fix Python version for Render"
git push
```

### Monitor Rebuild:

1. Go to Render dashboard
2. Click your web service
3. Watch the "Logs" tab
4. Wait for "Deploy live" message

---

**The fix is ready! Just push to GitHub and Render will rebuild with the correct Python version.**
