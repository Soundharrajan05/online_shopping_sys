# GitHub Upload Guide - Step by Step

## Current Structure (Already Correct!)

Your project structure is already correct for Render deployment:

```
online_shopping_sys/
├── run.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── build.sh
├── render.yaml
├── config.py
├── schema_postgresql.sql
├── render_init.py
├── seed_data.py
├── README.md
├── .gitignore
└── app/
    ├── __init__.py
    ├── admin/
    │   └── __init__.py
    ├── auth/
    │   ├── __init__.py
    │   └── decorators.py
    ├── database/
    │   ├── __init__.py
    │   ├── db_universal.py
    │   └── db.py
    ├── models/
    │   ├── __init__.py
    │   ├── user.py
    │   ├── product.py
    │   ├── category.py
    │   ├── cart.py
    │   └── order.py
    ├── static/
    │   ├── css/
    │   ├── js/
    │   └── images/
    ├── templates/
    │   ├── base.html
    │   ├── admin/
    │   ├── auth/
    │   └── user/
    ├── user/
    │   └── __init__.py
    └── utils/
        ├── __init__.py
        ├── error_handler.py
        └── validation.py
```

## Method 1: Using Git Command Line (Recommended)

### Step 1: Initialize Git (if not already done)

Open PowerShell in your project folder and run:

```powershell
# Check if git is initialized
git status

# If you see "not a git repository", initialize it:
git init
```

### Step 2: Add All Files

```powershell
# Add all files to git
git add .

# Check what will be committed
git status
```

### Step 3: Commit Files

```powershell
git commit -m "Initial commit - Online Shopping System"
```

### Step 4: Create GitHub Repository

1. Go to https://github.com/
2. Click the **+** icon (top right) → **New repository**
3. Settings:
   - Repository name: `online-shopping-system`
   - Description: `Flask-based e-commerce system`
   - Visibility: **Public** (or Private)
   - **DO NOT** check "Initialize with README" (you already have one)
4. Click **Create repository**

### Step 5: Connect to GitHub

GitHub will show you commands. Use these:

```powershell
# Add GitHub as remote
git remote add origin https://github.com/YOUR_USERNAME/online-shopping-system.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

### Step 6: Verify Upload

1. Refresh your GitHub repository page
2. You should see all your files uploaded
3. Verify the structure matches the tree above

---

## Method 2: Using GitHub Desktop (Easier for Beginners)

### Step 1: Download GitHub Desktop

1. Go to https://desktop.github.com/
2. Download and install GitHub Desktop
3. Sign in with your GitHub account

### Step 2: Add Your Project

1. Open GitHub Desktop
2. Click **File** → **Add Local Repository**
3. Click **Choose...** and select your project folder: `D:\online_shopping_sys`
4. If it says "not a git repository", click **Create a repository**

### Step 3: Create Repository

1. Name: `online-shopping-system`
2. Description: `Flask-based e-commerce system`
3. Keep "Git Ignore" as **None** (you already have .gitignore)
4. Click **Create Repository**

### Step 4: Commit Files

1. You'll see all your files in the left panel
2. In the bottom left:
   - Summary: `Initial commit`
   - Description: `Online Shopping System - Ready for Render deployment`
3. Click **Commit to main**

### Step 5: Publish to GitHub

1. Click **Publish repository** (top bar)
2. Settings:
   - Name: `online-shopping-system`
   - Description: `Flask-based e-commerce system`
   - Keep code **public** (or choose private)
3. Click **Publish Repository**

### Step 6: Verify

1. Click **View on GitHub** (top bar)
2. Your repository should open in browser
3. Verify all files are there

---

## Method 3: Using GitHub Web Interface (Upload Manually)

### Step 1: Create Repository

1. Go to https://github.com/
2. Click **+** → **New repository**
3. Name: `online-shopping-system`
4. Click **Create repository**

### Step 2: Upload Files

1. Click **uploading an existing file**
2. Drag and drop your entire project folder
3. **IMPORTANT**: Make sure to maintain the folder structure
4. Commit message: `Initial commit`
5. Click **Commit changes**

**Note**: This method is NOT recommended because it's harder to maintain the correct structure.

---

## What Files to Upload (Checklist)

Make sure these files are in your GitHub repository:

### Root Level Files:
- [ ] run.py
- [ ] requirements.txt
- [ ] Procfile
- [ ] runtime.txt
- [ ] build.sh
- [ ] render.yaml
- [ ] config.py
- [ ] schema_postgresql.sql
- [ ] render_init.py
- [ ] seed_data.py
- [ ] README.md
- [ ] .gitignore
- [ ] .env.example (NOT .env - keep secrets private!)

### app/ Directory:
- [ ] app/__init__.py
- [ ] app/admin/__init__.py
- [ ] app/auth/__init__.py
- [ ] app/auth/decorators.py
- [ ] app/database/__init__.py
- [ ] app/database/db_universal.py
- [ ] app/database/db.py
- [ ] app/models/__init__.py
- [ ] app/models/user.py
- [ ] app/models/product.py
- [ ] app/models/category.py
- [ ] app/models/cart.py
- [ ] app/models/order.py
- [ ] app/static/css/style.css
- [ ] app/static/js/main.js
- [ ] app/templates/base.html
- [ ] app/templates/admin/ (all files)
- [ ] app/templates/auth/ (all files)
- [ ] app/templates/user/ (all files)
- [ ] app/user/__init__.py
- [ ] app/utils/__init__.py
- [ ] app/utils/error_handler.py
- [ ] app/utils/validation.py

---

## Files to EXCLUDE (Already in .gitignore)

These should NOT be uploaded:
- ❌ .env (contains secrets!)
- ❌ __pycache__/ folders
- ❌ *.pyc files
- ❌ .vscode/ folder
- ❌ app_errors.log
- ❌ .coverage
- ❌ .hypothesis/
- ❌ htmlcov/
- ❌ .pytest_cache/

Your .gitignore file already excludes these.

---

## Verify Your Upload

After uploading, check your GitHub repository has this structure:

```
online-shopping-system/
├── run.py                    ✓
├── requirements.txt          ✓
├── Procfile                  ✓
├── runtime.txt              ✓
├── build.sh                 ✓
├── render.yaml              ✓
└── app/                     ✓
    ├── __init__.py          ✓
    └── (all other files)    ✓
```

---

## Common Issues

### Issue 1: "Permission denied" when pushing

**Solution**: 
```powershell
# Use HTTPS with personal access token
# Or set up SSH keys
```

### Issue 2: Files not showing correct structure

**Solution**: Make sure you're in the project root when running git commands:
```powershell
cd D:\online_shopping_sys
git add .
```

### Issue 3: .env file uploaded (SECURITY RISK!)

**Solution**: 
```powershell
# Remove .env from git
git rm --cached .env
git commit -m "Remove .env file"
git push
```

---

## After Upload - Deploy to Render

Once your code is on GitHub:

1. Go to https://dashboard.render.com/
2. Follow **QUICK_START_RENDER.md**
3. Connect your GitHub repository
4. Deploy!

---

## Need Help?

If you're stuck, tell me:
1. Which method you're using (Git CLI, GitHub Desktop, or Web)
2. What error message you're seeing
3. What step you're on

I'll help you fix it!
