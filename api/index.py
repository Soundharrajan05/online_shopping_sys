import os
import sys

# ------------------------------------------------------------------ #
# Path setup — MUST happen before any local imports
# Vercel runs the function from the repo root, but sys.path may not
# include it. Add both the repo root and the api/ directory explicitly.
# ------------------------------------------------------------------ #
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from flask import Flask, render_template_string
from dotenv import load_dotenv

# Load .env for local development (silently ignored on Vercel)
load_dotenv(os.path.join(ROOT_DIR, '.env'))

config_name = os.environ.get('FLASK_CONFIG') or 'production'

# ------------------------------------------------------------------ #
# Placeholder app — Vercel needs an `app` object at module load time
# It will be replaced below if initialisation succeeds.
# ------------------------------------------------------------------ #
app = Flask(__name__)

# ------------------------------------------------------------------ #
# Helpful error page template
# ------------------------------------------------------------------ #
_ERROR_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Configuration Required</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 700px; margin: 3rem auto; padding: 0 1rem; color: #222; }
    h1   { color: #c0392b; }
    code, pre { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-size: 0.9em; }
    pre  { padding: 1rem; overflow-x: auto; }
    .box { border-left: 4px solid #c0392b; background: #fdf3f3; padding: 1rem; margin: 1rem 0; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>&#9888; Application Initialization Error</h1>
  <div class="box"><strong>{{ error }}</strong></div>

  <h2>How to fix this on Vercel</h2>
  <p>Go to <strong>Vercel Dashboard → Project → Settings → Environment Variables</strong>
     and add these variables, then click <strong>Redeploy</strong>:</p>
  <pre>SECRET_KEY   = &lt;random 32-char string&gt;
DATABASE_URL = mysql://username:password@host:3306/database
FLASK_CONFIG = production</pre>

  <h3>Generate a SECRET_KEY</h3>
  <pre>python -c "import secrets; print(secrets.token_hex(32))"</pre>

  <h3>DATABASE_URL examples</h3>
  <pre># PlanetScale
mysql://user:pass@host.aws.connect.psdb.cloud/shopping_system?ssl-mode=VERIFY_IDENTITY

# Railway / Aiven / other
mysql://user:pass@host:3306/shopping_system</pre>

  <p style="margin-top:2rem;color:#888;font-size:0.85em;">
    See <code>docs/VERCEL_DEPLOYMENT.md</code> in the repo for the full guide.
  </p>
</body>
</html>'''


def make_error_app(message):
    """Return a minimal Flask app that displays a helpful error page."""
    error_app = Flask(__name__)

    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_page(path):
        return render_template_string(_ERROR_TEMPLATE, error=message), 500

    return error_app


# ------------------------------------------------------------------ #
# Application bootstrap
# ------------------------------------------------------------------ #
try:
    # On Vercel production, validate env vars BEFORE attempting DB connect
    if os.environ.get('VERCEL') and config_name == 'production':
        missing = []
        if not os.environ.get('SECRET_KEY'):
            missing.append('SECRET_KEY')
        if not os.environ.get('DATABASE_URL'):
            missing.append('DATABASE_URL')
        if missing:
            raise RuntimeError(
                f"Missing required environment variables: {', '.join(missing)}. "
                "Set them in Vercel → Settings → Environment Variables and redeploy."
            )

    from app import create_app
    app = create_app(config_name)

except Exception as exc:
    app = make_error_app(str(exc))

# WSGI aliases expected by some platforms
application = app
handler = app

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False),
    )
