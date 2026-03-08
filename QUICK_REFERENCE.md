# 🚀 Quick Reference Card

## 📝 PostgreSQL Connection String Format

```
DATABASE_URL=postgresql://username:password@host:5432/database
```

---

## 🔧 Environment Variables (.env file)

```env
# PostgreSQL Connection
DATABASE_URL=postgresql://username:password@host:5432/database

# Flask Config
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

---

## 🎯 Common Connection Strings

### Local PostgreSQL:
```
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/shopping_system
```

### Render.com (provided automatically):
```
DATABASE_URL=postgresql://user:pass@dpg-xxxxx.oregon-postgres.render.com/dbname
```

### ElephantSQL:
```
DATABASE_URL=postgresql://user:pass@jelani.db.elephantsql.com:5432/dbname
```

---

## ⚡ Quick Commands

### Setup Database:
```bash
python render_init.py
python seed_data.py
```

### Run Application:
```bash
python run.py
```

### Test Connection:
```bash
python -c "from app import create_app; from app.database.db_universal import Database; app = create_app(); app.app_context().push(); conn = Database.get_connection(); print('✅ Connected!')"
```

---

## 🔑 Default Login Credentials

**Admin:**
- Email: `admin@shop.com`
- Password: `admin123`

**Customer:**
- Email: `customer@test.com`
- Password: `customer123`

---

## 📂 Important Files

- `.env` - Your environment variables (create from .env.example)
- `POSTGRESQL_SETUP.md` - Full PostgreSQL setup guide
- `DEPLOYMENT_GUIDE.md` - Render.com deployment guide
- `schema_postgresql.sql` - Database schema

---

## 🐛 Troubleshooting

### Can't connect to database?
1. Check DATABASE_URL format
2. Verify PostgreSQL is running
3. Check username/password
4. Verify database exists

### Import errors?
```bash
pip install -r requirements.txt
```

### Database not initialized?
```bash
python render_init.py
```

---

## 📞 Quick Help

- PostgreSQL Setup: See `POSTGRESQL_SETUP.md`
- Deployment: See `DEPLOYMENT_GUIDE.md`
- Checklist: See `DEPLOYMENT_CHECKLIST.md`

---

**Keep this file handy for quick reference!** 📌
