# ✅ Deployment Checklist

Use this checklist to ensure smooth deployment to Render.com.

---

## 📦 Pre-Deployment

- [ ] All code changes committed
- [ ] `.gitignore` file in place
- [ ] `.env` file NOT committed (should be in .gitignore)
- [ ] `requirements.txt` includes all dependencies
- [ ] Local testing completed successfully
- [ ] Database schema tested

---

## 🔐 GitHub Setup

- [ ] GitHub account created
- [ ] New repository created on GitHub
- [ ] Local git repository initialized (`git init`)
- [ ] Remote added (`git remote add origin ...`)
- [ ] Code pushed to GitHub (`git push -u origin main`)

---

## 🌐 Render.com Setup

- [ ] Render.com account created
- [ ] GitHub connected to Render
- [ ] Repository access granted to Render

---

## 🚀 Web Service Configuration

- [ ] New Web Service created
- [ ] Correct repository selected
- [ ] Build command set: `pip install -r requirements.txt`
- [ ] Start command set: `gunicorn run:app`
- [ ] Instance type: Free
- [ ] Environment variables added:
  - [ ] `FLASK_ENV` = `production`
  - [ ] `SECRET_KEY` = (generated)
  - [ ] `PYTHON_VERSION` = `3.11.0`

---

## 🗄️ Database Configuration

- [ ] PostgreSQL database created
- [ ] Database name: `shopping_system`
- [ ] Database linked to web service
- [ ] `DATABASE_URL` environment variable set

---

## 🔧 Post-Deployment

- [ ] Deployment completed successfully
- [ ] No errors in logs
- [ ] Website accessible at Render URL
- [ ] Database initialized (`python render_init.py`)
- [ ] Sample data seeded (`python seed_data.py`)
- [ ] Login page loads correctly
- [ ] Admin login works
- [ ] Customer login works
- [ ] Products display correctly
- [ ] Cart functionality works
- [ ] Order placement works

---

## 🧪 Testing

- [ ] Register new customer account
- [ ] Browse products
- [ ] Add items to cart
- [ ] Place an order
- [ ] View order history
- [ ] Login as admin
- [ ] View dashboard
- [ ] Manage products
- [ ] Manage orders

---

## 🔒 Security

- [ ] Default admin password changed
- [ ] Test customer account removed or password changed
- [ ] SECRET_KEY is strong and unique
- [ ] HTTPS enabled (automatic on Render)
- [ ] Database backups configured

---

## 📊 Monitoring

- [ ] Bookmark Render dashboard
- [ ] Check logs regularly
- [ ] Monitor database usage
- [ ] Set up uptime monitoring (optional)

---

## 🎉 Launch

- [ ] Share URL with users
- [ ] Document any custom setup
- [ ] Create user guide if needed
- [ ] Celebrate! 🎊

---

## 📝 Notes

Use this space for deployment-specific notes:

```
Deployment Date: _______________
Render URL: _______________
Database Name: _______________
Any Issues: _______________
```

---

**Once all items are checked, your application is fully deployed and ready for users!** ✨
