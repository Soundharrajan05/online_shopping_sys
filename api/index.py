import os
from flask import Flask, render_template_string
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env when running locally
load_dotenv()

config_name = os.environ.get('FLASK_CONFIG') or 'production'


def make_error_app(message):
    error_app = Flask(__name__)

    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_page(path):
        return render_template_string(
            '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Application Initialization Error</title>
            </head>
            <body style="font-family: Arial, sans-serif; margin: 2rem;">
                <h1>Application Initialization Error</h1>
                <p>{{ message }}</p>
                <p>Please verify your Vercel environment variables and database configuration.</p>
            </body>
            </html>
            ''', message=message
        ), 500

    return error_app


try:
    if os.environ.get('VERCEL') and config_name == 'production':
        missing = []
        if not os.environ.get('SECRET_KEY'):
            missing.append('SECRET_KEY')
        if not os.environ.get('DATABASE_URL'):
            missing.append('DATABASE_URL')
        if missing:
            raise RuntimeError(
                'Missing required Vercel production environment variables: '
                + ', '.join(missing)
                + '. Please set them in Vercel and redeploy.'
            )
    app = create_app(config_name)
except Exception as exc:
    error_message = str(exc)
    if os.environ.get('VERCEL') and not os.environ.get('DATABASE_URL'):
        error_message = (
            'Vercel deployment requires a managed database and DATABASE_URL environment variable. '
            'Set DATABASE_URL to a valid PostgreSQL connection string and redeploy.'
        )
    app = make_error_app(error_message)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=app.config.get('DEBUG', False))
