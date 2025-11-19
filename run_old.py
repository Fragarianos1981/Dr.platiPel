# -*- coding: utf-8 -*-
"""
run.py - Dr. PLATI Entry Point
Modular Flask Application Startup - FIXED VERSION
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection before startup"""
    try:
        from app_original import create_app
        from extensions import db
        
        app = create_app()
        with app.app_context():
            db.session.execute('SELECT 1')
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("🔧 Troubleshooting steps:")
        print("   1. Check XAMPP MySQL is running")
        print("   2. Verify database 'dr_plati' exists in phpMyAdmin")
        print("   3. Check .env DATABASE_URL setting")
        return False

def create_default_admin():
    """Create default admin user"""
    from models import User
    from werkzeug.security import generate_password_hash
    from extensions import db
    
    try:
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        
        if not admin:
            admin = User(
                username='admin',
                # password1_hash=generate_password_hash(  # Use set_password() instead'admin123'),
                # password2='kp020716'  # Use set_password2() instead,
                full_name='System Administrator',
                email='admin@drplati.gr',
                phone='210-1234567',
                role='topuser',
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Admin user created:")
            print("   Username: admin")
            print("   Password1: admin123")
            print("   Password2: kp020716")
            return True
        else:
            print("✅ Admin user already exists")
            return True
            
    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")
        return False

def create_default_doctors():
    """Create default doctor users"""
    from models import User
    from werkzeug.security import generate_password_hash
    from extensions import db
    
    default_doctors = [
        {
            'username': 'platipelagia',
            'password': 'm8a9g6p1',
            'full_name': 'Πελαγία Πλάτη',
            'email': 'dr.pelagia@drplati.gr',
            'phone': '6944123456',
            'role': 'doctor'
        },
        {
            'username': 'secretary',
            'password': '2841023830',
            'full_name': 'Γραμματέας Ιατρείου',
            'email': 'secretary@drplati.gr',
            'phone': '2109876543',
            'role': 'secretary'
        }
    ]
    
    try:
        for doctor_data in default_doctors:
            existing = User.query.filter_by(username=doctor_data['username']).first()
            if not existing:
                doctor = User(
                    username=doctor_data['username'],
                    # password1_hash=generate_password_hash(  # Use set_password() insteaddoctor_data['password']),
                    # password2='kp020716'  # Use set_password2() instead,
                    full_name=doctor_data['full_name'],
                    email=doctor_data['email'],
                    phone=doctor_data['phone'],
                    role=doctor_data['role'],
                    is_active=True
                )
                db.session.add(doctor)
        
        db.session.commit()
        print("✅ Default users created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create default users: {e}")
        return False

def initialize_database():
    """Initialize database and create default data"""
    from app_original import create_app
    from extensions import db
    
    try:
        app = create_app()
        with app.app_context():
            # Import models from the monolithic models.py file
            from models import User, Patient, Visit, Vaccine, Transaction, Certificate
            
            # Create all tables
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ Database tables created")
            
            # Create default users
            print("👥 Creating default users...")
            if not create_default_admin():
                return False
            
            if not create_default_doctors():
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def display_startup_info():
    """Display startup information"""
    print("🏥 Dr. PLATI - Παιδιατρικό Σύστημα Διαχείρισης")
    print("=" * 60)
    print("📋 Modular Flask Application")
    print("🔧 Version: 1.0.0 Production Ready")
    print("🌐 Architecture: Models + Services + Routes")
    print("")

def display_access_info():
    """Display access information"""
    print("")
    print("🚀 Application started successfully!")
    print("=" * 40)
    print("🌐 Access URL: http://localhost:8080")
    print("")
    print("👥 DEFAULT ACCOUNTS:")
    print("   👤 Admin: admin / admin123 / kp020716")
    print("   👩‍⚕️ Doctor: platipelagia / m8a9g6p1 / kp020716") 
    print("   📋 Secretary: secretary / 2841023830 / kp020716")
    print("")
    print("⚠️  Change passwords after first login!")
    print("=" * 40)

def main():
    """Main application entry point"""
    display_startup_info()
    
    # Test database connection
    print("🔍 Testing database connection...")
    if not test_database_connection():
        print("❌ Startup failed - database connection error")
        return False
    
    # Initialize database
    print("🔧 Initializing database...")
    if not initialize_database():
        print("❌ Startup failed - database initialization error")
        return False
    
    # Create Flask app
    try:
        from app_original import create_app
        app = create_app()
        
        # Display access information
        display_access_info()
        
        # Start application
        app.run(
            host='0.0.0.0',
            port=8080,
            debug=True,
            use_reloader=False  # Disabled to prevent double initialization
        )
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    if not success:
        print("\n💡 Quick troubleshooting:")
        print("   1. Start XAMPP (Apache + MySQL)")
        print("   2. Create database 'dr_plati' in phpMyAdmin")
        print("   3. Check .env configuration")
        print("   4. Verify virtual environment is active")
        sys.exit(1)