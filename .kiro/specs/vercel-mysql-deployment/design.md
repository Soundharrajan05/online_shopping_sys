# Design: Vercel MySQL Deployment

## Overview
This design document outlines the technical approach to deploy the Flask online shopping system to Vercel with MySQL database and clean up Render.com-specific files.

## Architecture

### Current State
```
Flask App
├── Dual Platform Support (Render + Vercel)
├── Dual Database Support (PostgreSQL + MySQL)
├── Multiple deployment files
└── Mixed configuration
```

### Target State
```
Flask App on Vercel
├── Single Platform (Vercel only)
├── Single Database (MySQL only)
├── Clean deployment configuration
└── Streamlined codebase
```

### Deployment Architecture
```
User Request
    ↓
Vercel Edge Network
    ↓
Serverless Function (api/index.py)
    ↓
Flask Application (app/)
    ↓
MySQL Database (External Cloud)
```

### Target State
```
Flask App on Vercel
├── Single Platform (Vercel only)
├── Single Database (MySQL only)
├── Clean deployment configuration
└── Streamlined codebase
```

### Deployment Architecture on Vercel
```
User Request
    ↓
Vercel Edge Network
    ↓
Serverless Function (api/index.py)
    ↓
Flask Application
    ↓
MySQL Database (External)
```

## Component Design

### 1. Vercel Entry Point (api/index.py)

**Current Implementation:**
- Supports both PostgreSQL and MySQL
- Checks for DATABASE_URL
- Error handling for missing environment variables

**Required Changes:**
- Update error messages to reflect MySQL requirement
- Remove PostgreSQL-specific references
- Optimize for MySQL connection string format

**MySQL Connection String Format:**
```
DATABASE_URL=mysql://username:password@host:port/database
```

### 2. Database Configuration (config.py)

**Current Implementation:**
- Supports DATABASE_URL (for Render PostgreSQL)
- Supports individual variables (DB_HOST, DB_USER, etc.)
- Has ProductionConfig class

**Required Changes:**
- Remove DATABASE_URL parsing for PostgreSQL
- Ensure MySQL connection string parsing
- Update documentation to reflect MySQL only

**Configuration Priority:**
1. DATABASE_URL (if provided) → Parse as MySQL connection string
2. Individual variables (DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)

### 3. Database Abstraction (app/database/db_universal.py)

**Current Implementation:**
- Already supports MySQL through mysql-connector-python
- Connection pooling
- Universal interface

**Required Changes:**
- Verify MySQL connection works in Vercel serverless environment
- Ensure connection pooling is appropriate for serverless
- Optimize connection management for cold starts

**Serverless Considerations:**
- Each function invocation may be a cold start
- Connection pooling may need adjustment
- Consider connection reuse strategies

### 4. Dependencies (requirements.txt)

**Current Dependencies:**
```
Flask==3.0.0
mysql-connector-python==8.2.0
psycopg2-binary==2.9.10          # TO REMOVE
werkzeug==3.0.1
gunicorn==21.2.0
python-dotenv==1.0.0
pytest==7.4.3
hypothesis==6.92.1
pytest-cov==4.1.0
```

**Target Dependencies:**
```
Flask==3.0.0
mysql-connector-python==8.2.0
werkzeug==3.0.1
python-dotenv==1.0.0
```

**Notes:**
- Remove psycopg2-binary (PostgreSQL driver)
- Keep gunicorn for local development (optional)
- Keep testing dependencies if used in CI/CD

### 5. Vercel Configuration (vercel.json)

**Current Configuration:**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ]
}
```

**Recommended Enhancements:**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ],
  "env": {
    "FLASK_CONFIG": "production"
  }
}
```

### 6. Static Files Strategy

**Current Structure:**
```
app/static/
├── css/
├── images/
└── js/
```

**Vercel Handling:**
- Vercel serves static files through the Flask app
- All requests route through api/index.py
- Flask's send_static_file handles delivery

**Optimization Considerations:**
- Consider moving static files to Vercel's edge network
- Current approach works but may have cold start latency

## Files to Remove

### Render.com-Specific Files
1. **render.yaml** - Render platform configuration
2. **render_init.py** - PostgreSQL database initialization script
3. **build.sh** - Render build script
4. **Procfile** - Process file for Heroku/Render
5. **runtime.txt** - Python runtime specification
6. **schema_postgresql.sql** - PostgreSQL-specific schema

### Files to Keep
1. **vercel.json** - Vercel configuration
2. **api/index.py** - Vercel entry point
3. **.vercelignore** - Vercel ignore rules
4. **requirements.txt** - Python dependencies (updated)
5. **config.py** - Application configuration
6. **schema.sql** - MySQL schema
7. **.env.example** - Environment variables template

## Environment Variables

### Required for Vercel Deployment

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions | `your-secret-key-here` |
| `DATABASE_URL` | MySQL connection string | `mysql://user:pass@host:3306/db` |
| `FLASK_CONFIG` | Configuration environment | `production` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | MySQL host (if not using DATABASE_URL) | `localhost` |
| `DB_USER` | MySQL user | `root` |
| `DB_PASSWORD` | MySQL password | `""` |
| `DB_NAME` | MySQL database name | `shopping_system` |

## Database Connection Strategy

### Connection String Parsing

```python
# Parse DATABASE_URL if provided
if DATABASE_URL:
    # Format: mysql://username:password@host:port/database
    parsed = parse_database_url(DATABASE_URL)
    DB_HOST = parsed.host
    DB_USER = parsed.username
    DB_PASSWORD = parsed.password
    DB_NAME = parsed.database
    DB_PORT = parsed.port or 3306
```

### Connection Pooling for Serverless

**Challenge:** Traditional connection pooling doesn't work well in serverless

**Solution Options:**

1. **Single Connection per Request** (Simplest)
   - Create connection at request start
   - Close connection at request end
   - Works for low traffic

2. **Connection Reuse** (Recommended)
   - Store connection in global scope
   - Reuse if container is warm
   - Create new if cold start

3. **External Connection Pooler** (Advanced)
   - Use PgBouncer-like service for MySQL
   - Not implemented in this phase

**Implementation:**
```python
# Global connection variable
_db_connection = None

def get_connection():
    global _db_connection
    if _db_connection is None or not _db_connection.is_connected():
        _db_connection = mysql.connector.connect(...)
    return _db_connection
```

## Deployment Workflow

### Step 1: Prepare Codebase
1. Remove Render.com files
2. Update requirements.txt
3. Update .vercelignore
4. Update api/index.py error messages
5. Commit changes to Git

### Step 2: Setup MySQL Database
1. Create MySQL database (local, cloud, or Vercel)
2. Run schema.sql to create tables
3. Run seed_data.py to populate initial data
4. Note connection credentials

### Step 3: Configure Vercel Project
1. Import Git repository to Vercel
2. Set environment variables:
   - SECRET_KEY
   - DATABASE_URL
   - FLASK_CONFIG=production
3. Configure build settings (auto-detected)

### Step 4: Deploy
1. Push to Git repository
2. Vercel auto-deploys
3. Verify deployment success
4. Test application functionality

### Step 5: Verify
1. Test user registration/login
2. Test product browsing
3. Test cart operations
4. Test checkout process
5. Test admin functions

## Testing Strategy

### Local Testing
1. Set up local MySQL database
2. Configure .env file with local credentials
3. Run application locally: `python run.py`
4. Test all major features

### Vercel Preview Testing
1. Push to feature branch
2. Vercel creates preview deployment
3. Test on preview URL
4. Verify database connectivity

### Production Testing
1. Deploy to production
2. Run smoke tests on production URL
3. Monitor logs for errors
4. Verify performance

## Rollback Strategy

### If Deployment Fails
1. Vercel automatically keeps previous deployment active
2. Roll back through Vercel dashboard
3. Fix issues locally
4. Redeploy

### If Database Issues
1. Keep database backup before migration
2. Restore from backup if needed
3. Verify connection string format
4. Check firewall/security group rules

## Security Considerations

### Environment Variables
- Never commit .env file
- Use Vercel's encrypted environment variables
- Rotate SECRET_KEY regularly

### Database Security
- Use strong passwords
- Restrict database access to Vercel IPs
- Enable SSL for database connections
- Use least privilege principle for database user

### Application Security
- Keep dependencies updated
- Enable CSRF protection
- Validate all user inputs
- Use secure session configuration

## Performance Considerations

### Cold Start Optimization
- Minimize import statements in api/index.py
- Lazy load heavy modules
- Use lightweight database connections

### Database Query Optimization
- Use connection reuse
- Implement query caching where appropriate
- Use database indexes effectively
- Monitor slow query logs

### Static Asset Delivery
- Current: Through Flask app (works but slower)
- Future: Consider Vercel CDN for static files
- Optimize image sizes
- Enable browser caching

## Monitoring and Logging

### Vercel Logs
- Access through Vercel dashboard
- Real-time log streaming
- Error tracking
- Performance metrics

### Application Logging
- Use Python logging module
- Log levels: INFO, WARNING, ERROR
- Structured logging for better searchability

### Database Monitoring
- Monitor connection counts
- Track query performance
- Set up alerts for errors

## Documentation Updates

### Files to Create/Update
1. **README.md** - Update deployment section
2. **DEPLOYMENT.md** - Detailed Vercel deployment guide
3. **.env.example** - Update with MySQL variables
4. **docs/VERCEL_DEPLOYMENT.md** - New file with step-by-step guide

### Documentation Content
- Prerequisites
- Environment setup
- Deployment steps
- Troubleshooting common issues
- Environment variables reference

## Success Criteria

### Technical Success
- ✅ Application deploys successfully to Vercel
- ✅ All routes respond correctly
- ✅ Database operations work
- ✅ No Render.com files remain
- ✅ No PostgreSQL dependencies remain

### Functional Success
- ✅ Users can register and login
- ✅ Products display correctly
- ✅ Cart functionality works
- ✅ Checkout process completes
- ✅ Admin functions work

### Quality Success
- ✅ Clean codebase
- ✅ Clear documentation
- ✅ No broken references
- ✅ Proper error handling
- ✅ Good performance

## Future Enhancements

### Phase 2 Improvements
1. Move static files to Vercel CDN
2. Implement connection pooler for database
3. Add caching layer (Redis)
4. Set up CI/CD pipeline
5. Add monitoring and alerting
6. Implement database migrations
7. Add health check endpoint

### Not in Scope (Current Phase)
- Database migration tools
- Advanced caching
- Multi-region deployment
- Load testing
- Performance optimization beyond basics


## Components and Interfaces

### api/index.py — Vercel Entry Point
- Receives all HTTP requests via Vercel's serverless runtime
- Validates `SECRET_KEY` and `DATABASE_URL` env vars on Vercel production
- Creates Flask app via `create_app()` factory
- Returns error page if initialisation fails

### app/database/db_universal.py — MySQL Connection Manager
- `init_db(config)`: Initialises connection from `DATABASE_URL` or individual `DB_*` vars
- `get_connection()`: Returns active connection, auto-reconnects on cold start
- `execute_query(query, params, fetch)`: Runs parameterised queries safely
- `release_connection(conn)`: No-op kept for API compatibility

### app/database/db.py — Backward-Compatible Re-export
- Re-exports `UniversalDatabase` as `Database` so all legacy imports work
- No separate pool — shares the same connection as `db_universal`

### vercel.json — Vercel Router
- Routes all `/(.*)" requests to `api/index.py`
- Sets `FLASK_CONFIG=production` as default env var

### config.py — Environment Configuration
- `DevelopmentConfig`: debug=True, uses local DB vars
- `ProductionConfig`: debug=False, requires `SECRET_KEY` from env
- `TestConfig`: uses `shopping_system_test` database

## Data Models

### Environment Variables
```
SECRET_KEY      : string  — Flask session signing key (required in production)
DATABASE_URL    : string  — MySQL connection string: mysql://user:pass@host:port/db
FLASK_CONFIG    : string  — One of: development | production | test
DB_HOST         : string  — MySQL host (fallback when DATABASE_URL not set)
DB_USER         : string  — MySQL username
DB_PASSWORD     : string  — MySQL password
DB_NAME         : string  — MySQL database name
DB_PORT         : integer — MySQL port (default: 3306)
```

### Database Tables (MySQL)
```
users         : user_id, name, email, password(hash), role, created_at
categories    : category_id, category_name
products      : product_id, product_name, description, price, stock_quantity, image_url, category_id
cart          : cart_id, user_id, product_id, quantity
orders        : order_id, user_id, total_amount, order_date, order_status
order_items   : order_item_id, order_id, product_id, quantity, price
```

## Error Handling

### Missing Environment Variables
- `api/index.py` checks for `SECRET_KEY` and `DATABASE_URL` on Vercel
- If missing, renders a styled HTML error page with setup instructions
- Does not crash with a 500 — shows actionable guidance

### Database Connection Failure
- Connection errors are caught in `db_universal.py`
- Error is logged via `print()` and re-raised to Flask's error handler
- Flask returns a 500 error page to the user

### Invalid SQL / Query Errors
- All queries use parameterised statements (`%s` placeholders)
- Exceptions trigger `connection.rollback()` before re-raising
- `app/utils/error_handler.py` logs full tracebacks without exposing them to users

### Cold Start (Serverless)
- `get_connection()` checks `_is_connection_alive()` via `ping()`
- Automatically reconnects if the previous connection dropped
- `before_request` hook ensures DB is ready before every request

## Correctness Properties

### Property 1: DATABASE_URL Connection
Both `mysql://` and `mysql+mysqlconnector://` URL formats must connect successfully to MySQL.

**Validates: Requirements 2.1**

### Property 2: SQL Parameterisation
All SQL queries must use `%s` placeholders — no string interpolation allowed anywhere in the codebase.

**Validates: Requirements 2.2**

### Property 3: SECRET_KEY Required in Production
`SECRET_KEY` must never be `None` in production. `api/index.py` enforces this check before app creation.

**Validates: Requirements 3.1**

### Property 4: No-op release_connection
`release_connection()` must never close the shared connection — it must be a complete no-op.

**Validates: Requirements 2.3**

### Property 5: Lazy Database Initialisation
`create_app()` must succeed even when MySQL is unreachable. The DB connects on first request via `before_request`.

**Validates: Requirements 1.1**

### Property 6: No Render.com References
None of the deleted Render.com files (`render.yaml`, `build.sh`, `Procfile`, etc.) must be referenced anywhere in the active codebase.

**Validates: Requirements 4.1**
