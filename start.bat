@echo off
echo =============================================
echo  Starting Online Shopping System
echo =============================================
echo.

:: Activate virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate

:: Check MySQL connection
echo [INFO] Checking MySQL connection...
python -c "import mysql.connector; mysql.connector.connect(host='localhost', user='root', password='').close(); print('[OK] MySQL is accessible')" 2>nul
if errorlevel 1 (
    echo [WARNING] Cannot connect to MySQL. Make sure it's running.
    echo Continuing anyway - you can initialize the database later.
    echo.
)

:: Initialize database if needed
python -c "import mysql.connector; c=mysql.connector.connect(host='localhost', user='root', password=''); cur=c.cursor(); cur.execute('SHOW DATABASES LIKE \"shopping_system\"'); print('[OK] Database exists' if cur.fetchone() else '[INFO] Database not found - run init_db.py'); c.close()" 2>nul

echo.
echo =============================================
echo  Starting Flask Server...
echo  Open http://localhost:5000 in your browser
echo  Press Ctrl+C to stop
echo =============================================
echo.

python run.py
