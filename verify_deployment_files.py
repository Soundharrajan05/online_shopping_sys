#!/usr/bin/env python3
"""
Verify that all required files for Render deployment are present and correct
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ MISSING {description}: {filepath}")
        return False

def check_file_content(filepath, required_content, description):
    """Check if file contains required content"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if required_content in content:
                print(f"✓ {description}")
                return True
            else:
                print(f"✗ {description} - Missing: {required_content}")
                return False
    except Exception as e:
        print(f"✗ Error reading {filepath}: {e}")
        return False

def main():
    print("=" * 70)
    print("Render.com Deployment Verification")
    print("=" * 70)
    print()
    
    all_good = True
    
    # Check required files
    print("1. Checking required files...")
    all_good &= check_file_exists("run.py", "Application entry point")
    all_good &= check_file_exists("requirements.txt", "Python dependencies")
    all_good &= check_file_exists("Procfile", "Process file")
    all_good &= check_file_exists("runtime.txt", "Python version")
    all_good &= check_file_exists("build.sh", "Build script")
    all_good &= check_file_exists("render.yaml", "Render configuration")
    all_good &= check_file_exists("config.py", "App configuration")
    all_good &= check_file_exists("schema_postgresql.sql", "PostgreSQL schema")
    all_good &= check_file_exists("render_init.py", "Database init script")
    all_good &= check_file_exists("seed_data.py", "Sample data script")
    all_good &= check_file_exists("app/__init__.py", "App factory")
    print()
    
    # Check requirements.txt
    print("2. Checking requirements.txt...")
    all_good &= check_file_content("requirements.txt", "gunicorn", "Gunicorn is included")
    all_good &= check_file_content("requirements.txt", "psycopg2-binary", "PostgreSQL driver is included")
    all_good &= check_file_content("requirements.txt", "Flask", "Flask is included")
    print()
    
    # Check Procfile
    print("3. Checking Procfile...")
    all_good &= check_file_content("Procfile", "gunicorn run:app", "Correct start command")
    print()
    
    # Check runtime.txt
    print("4. Checking runtime.txt...")
    all_good &= check_file_content("runtime.txt", "python-3.11", "Python version specified")
    print()
    
    # Check config.py
    print("5. Checking config.py...")
    all_good &= check_file_content("config.py", "DATABASE_URL", "DATABASE_URL support")
    all_good &= check_file_content("config.py", "ProductionConfig", "Production config exists")
    print()
    
    # Check app structure
    print("6. Checking app structure...")
    all_good &= check_file_exists("app/__init__.py", "App factory")
    all_good &= check_file_exists("app/database/db_universal.py", "Universal database module")
    all_good &= check_file_exists("app/models/user.py", "User model")
    all_good &= check_file_exists("app/models/product.py", "Product model")
    all_good &= check_file_exists("app/models/order.py", "Order model")
    all_good &= check_file_exists("app/templates/base.html", "Base template")
    print()
    
    print("=" * 70)
    if all_good:
        print("✓ ALL CHECKS PASSED - Ready for Render deployment!")
        print()
        print("Next steps:")
        print("1. Push your code to GitHub")
        print("2. Follow the guide in RENDER_DEPLOYMENT_STEPS.md")
    else:
        print("✗ SOME CHECKS FAILED - Please fix the issues above")
        sys.exit(1)
    print("=" * 70)

if __name__ == '__main__':
    main()
