# Vercel Deployment Guide – Online Shopping System

This guide covers deploying the Flask online shopping system to Vercel with a MySQL database.

---

## Prerequisites

- [Vercel account](https://vercel.com/signup) (free tier works)
- A MySQL database accessible from the internet (see options below)
- Git repository (GitHub, GitLab, or Bitbucket)
- Python 3.11+

---

## 1. MySQL Database Options

You need a cloud-hosted MySQL database. Recommended free/low-cost options:

| Provider | Free Tier | Notes |
|----------|-----------|-------|
| [PlanetScale](https://planetscale.com) | Yes | Serverless MySQL, great for Vercel |
| [Aiven](https://aiven.io) | Trial | Managed MySQL |
| [Railway](https://railway.app) | Yes | Easy setup |
| [FreeMySQLHosting](https://www.freemysqlhosting.net) | Yes | Simple option |

### Set up your database

1. Create a MySQL database on your chosen provider.
2. Run the schema to create tables:
   ```bash
   mysql -h HOST -u USER -p DATABASE_NAME < schema.sql
   ```
3. (Optional) Seed sample data:
   ```bash
   python seed_data.py
   ```
4. Note your connection credentials for the next step.

---

## 2. Environment Variables

Set these in the Vercel dashboard under **Project → Settings → Environment Variables**:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `SECRET_KEY` | ✅ | Flask session signing key | `a3f8...` (32+ random chars) |
| `DATABASE_URL` | ✅ | MySQL connection string | `mysql://user:pass@host:3306/db` |
| `FLASK_CONFIG` | ✅ | Config profile | `production` |

### Generate a SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### DATABASE_URL format

```
mysql://username:password@hostname:3306/database_name
```

PlanetScale example (with SSL):
```
mysql://user:pass@host.aws.connect.psdb.cloud/shopping_system?ssl-mode=VERIFY_IDENTITY
```

---

## 3. Deploy to Vercel

### Option A: Vercel Dashboard (recommended)

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. Vercel auto-detects the Python project via `vercel.json`
4. Add the environment variables from step 2
5. Click **Deploy**

### Option B: Vercel CLI

```bash
# Install CLI
npm i -g vercel

# Login
vercel login

# Deploy from project root
vercel

# Set environment variables
vercel env add SECRET_KEY
vercel env add DATABASE_URL
vercel env add FLASK_CONFIG

# Deploy to production
vercel --prod
```

---

## 4. Verify Deployment

After deployment, test the following:

| Feature | URL | Expected |
|---------|-----|----------|
| Home / product list | `/` | Product grid loads |
| Registration | `/auth/register` | Form submits successfully |
| Login | `/auth/login` | Session created |
| Cart | `/user/cart` | Cart page loads |
| Admin | `/admin/dashboard` | Dashboard visible (admin only) |

---

## 5. Project Structure (Vercel-relevant files)

```
online_shopping_sys/
├── api/
│   └── index.py          # Vercel entry point
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── database/
│   │   └── db_universal.py  # MySQL connection layer
│   ├── static/            # CSS, JS, images
│   └── templates/         # Jinja2 HTML templates
├── vercel.json            # Vercel configuration
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
└── schema.sql             # MySQL schema
```

---

## 6. Troubleshooting

### "Missing SECRET_KEY or DATABASE_URL"
- Confirm both variables are set in Vercel → Settings → Environment Variables.
- Redeploy after adding variables.

### "Can't connect to MySQL"
- Verify `DATABASE_URL` is correct (copy-paste from provider dashboard).
- Ensure the database allows connections from external IPs (whitelist `0.0.0.0/0` or Vercel IPs).
- Test locally: `mysql -h HOST -u USER -p`

### 500 errors / blank page
- Check Vercel deployment logs: Dashboard → Deployment → Functions tab.
- Look for import errors or missing modules.

### Static files not loading
- Static files are served through Flask via `api/index.py`.
- Ensure the `app/static/` directory is not excluded in `.vercelignore`.

### Cold start is slow
- This is normal for serverless Python.
- First request after inactivity takes 1–3 seconds; subsequent requests are fast.

---

## 7. Local Development

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd online_shopping_sys

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up .env
cp .env.example .env
# Edit .env with your local MySQL credentials

# 5. Create local database and schema
mysql -u root -p -e "CREATE DATABASE shopping_system;"
mysql -u root -p shopping_system < schema.sql

# 6. Run the app
python run.py
```

Visit `http://localhost:5000`

---

## 8. Re-deploying

Every push to the connected Git branch triggers an automatic redeploy on Vercel.

To deploy manually:
```bash
vercel --prod
```
