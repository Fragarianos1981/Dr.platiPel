@echo off
REM Dr. PLATI Windows XAMPP Installation Script
REM Κώστας 2024 - Automated Setup

echo ========================================
echo       Dr. PLATI Windows Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.11+ first.
    echo Download from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Create virtual environment
echo [STEP 1/6] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [STEP 2/6] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo [STEP 3/6] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] Pip upgraded
echo.

REM Install dependencies (Windows compatible)
echo [STEP 4/6] Installing dependencies...
echo This may take a few minutes...
pip install -r requirements_windows.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo Trying individual installation...
    pip install Flask==3.0.0
    pip install Flask-SQLAlchemy==3.1.1
    pip install Flask-Login==0.6.3
    pip install Flask-Mail==0.9.1
    pip install Flask-WTF==1.2.1
    pip install PyMySQL==1.1.0
    pip install python-dotenv==1.0.0
    pip install bcrypt==4.1.2
    pip install reportlab==4.0.7
    pip install requests==2.31.0
)
echo [OK] Dependencies installed
echo.

REM Check if .env exists
echo [STEP 5/6] Checking configuration...
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] .env file created from template
        echo [NOTICE] Please edit .env file with your database settings
    ) else (
        echo [WARNING] No .env.example found
    )
) else (
    echo [OK] .env file already exists
)
echo.

REM Try to initialize database
echo [STEP 6/6] Initializing database...
echo [NOTICE] Make sure XAMPP MySQL is running and database 'drplati' exists
python init_db.py
if %errorlevel% equ 0 (
    echo [OK] Database initialized successfully
    echo.
    echo Creating admin user...
    python run.py admin
    echo [OK] Admin user created
) else (
    echo [WARNING] Database initialization failed
    echo Please check:
    echo 1. XAMPP MySQL service is running
    echo 2. Database 'drplati' exists in phpMyAdmin  
    echo 3. .env file has correct database settings
)
echo.

echo ========================================
echo         INSTALLATION COMPLETE!
echo ========================================
echo.
echo To start Dr. PLATI:
echo   1. Make sure XAMPP is running (Apache + MySQL)
echo   2. Run: python run.py
echo   3. Open: http://localhost:5000
echo.
echo Default login:
echo   Username: admin
echo   Password1: admin123
echo   Password2: kp020716
echo.
echo [IMPORTANT] Change default passwords before production use!
echo.
pause
