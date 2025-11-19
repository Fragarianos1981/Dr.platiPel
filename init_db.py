# -*- coding: utf-8 -*-
"""
init_db.py
Database initialization script για Dr. PLATI
"""

from app_original import create_app
from extensions import db
from models.user import User
from models.patient import Patient
from models.visit import Visit
from models.vaccine import Vaccine
from models.transaction import Transaction
from models.certificate import Certificate
from werkzeug.security import generate_password_hash
from datetime import datetime


def init_database():
    """Initialize database with tables and default data"""
    app = create_app()
    
    with app.app_context():
        print("🏥 Initializing Dr. PLATI Database...")
        
        # Drop and create all tables
        print("📊 Creating database tables...")
        db.drop_all()
        db.create_all()
        
        # Create default users
        print("👥 Creating default users...")
        create_default_users()
        
        # Create default services
        print("🏥 Creating default services...")
        create_default_services()
        
        # Commit all changes
        db.session.commit()
        
        print("✅ Database initialized successfully!")
        print_default_credentials()


def create_default_users():
    """Create default user accounts"""
    secondary_password = "kp020716"  # Shared secondary password
    
    default_users = [
        {
            'username': 'admin',
            'email': 'admin@drplati.gr',
            'first_name': 'Διαχειριστής',
            'last_name': 'Συστήματος',
            'password': 'admin123',
            'role': 'topuser',
            'phone': '2101234567'
        },
        {
            'username': 'platipelagia',
            'email': 'dr.pelagia@drplati.gr',
            'first_name': 'Πελαγία',
            'last_name': 'Πλάτη',
            'password': 'm8a9g6p1',
            'role': 'doctor',
            'phone': '6944123456'
        },
        {
            'username': 'secretary',
            'email': 'secretary@drplati.gr',
            'first_name': 'Γραμματέας',
            'last_name': 'Ιατρείου',
            'password': '2841023830',
            'role': 'secretary',
            'phone': '2109876543'
        }
    ]
    
    for user_data in default_users:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if existing_user:
            print(f"   ⚠️  User {user_data['username']} already exists, skipping...")
            continue
        
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone=user_data['phone'],
            role=user_data['role'],
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        # Set passwords
        user.set_password(user_data['password'])
        user.set_password2(secondary_password)
        
        db.session.add(user)
        print(f"   ✓ Created user: {user.username} ({user.role})")


def create_default_services():
    """Create default medical services"""
    default_services = [
        # Checkups
        {
            'name': 'Γενικός Παιδιατρικός Έλεγχος',
            'description': 'Τακτικός έλεγχος παιδιού',
            'price': 45.00,
            'category': 'checkup'
        },
        {
            'name': 'Έλεγχος Νεογνού',
            'description': 'Εξέταση νεογνού (0-28 ημερών)',
            'price': 55.00,
            'category': 'checkup'
        },
        {
            'name': 'Έλεγχος Βρέφους',
            'description': 'Εξέταση βρέφους (1-12 μηνών)',
            'price': 50.00,
            'category': 'checkup'
        },
        
        # Sick visits
        {
            'name': 'Επίσκεψη Ασθενείας',
            'description': 'Εξέταση για οξύ νόσημα',
            'price': 40.00,
            'category': 'sick'
        },
        {
            'name': 'Επείγουσα Εξέταση',
            'description': 'Επείγουσα παιδιατρική εξέταση',
            'price': 60.00,
            'category': 'emergency'
        },
        
        # Vaccinations
        {
            'name': 'Εμβολιασμός',
            'description': 'Χορήγηση εμβολίου (χωρίς το κόστος εμβολίου)',
            'price': 15.00,
            'category': 'vaccination'
        },
        {
            'name': 'Εμβολιασμός + Εξέταση',
            'description': 'Εμβολιασμός με συνοδό εξέταση',
            'price': 35.00,
            'category': 'vaccination'
        },
        
        # Consultations
        {
            'name': 'Συμβουλευτική Διατροφής',
            'description': 'Διατροφικές συμβουλές για παιδιά',
            'price': 50.00,
            'category': 'consultation'
        },
        {
            'name': 'Συμβουλευτική Ανάπτυξης',
            'description': 'Αξιολόγηση ψυχοκινητικής ανάπτυξης',
            'price': 60.00,
            'category': 'consultation'
        },
        {
            'name': 'Προσχολική Εξέταση',
            'description': 'Ιατρική εξέταση για εισαγωγή σε σχολείο',
            'price': 40.00,
            'category': 'consultation'
        },
        
        # Certificates
        {
            'name': 'Ιατρική Βεβαίωση',
            'description': 'Έκδοση ιατρικής βεβαίωσης',
            'price': 10.00,
            'category': 'certificate'
        },
        {
            'name': 'Βεβαίωση Υγείας (Αθλητισμός)',
            'description': 'Βεβαίωση καταλληλότητας για αθλητικές δραστηριότητες',
            'price': 25.00,
            'category': 'certificate'
        },
        
        # Tests
        {
            'name': 'Δερματικές Δοκιμασίες',
            'description': 'Αλλεργιολογικές δερματικές δοκιμασίες',
            'price': 80.00,
            'category': 'test'
        },
        {
            'name': 'Σπιρομέτρηση',
            'description': 'Εξέταση αναπνευστικής λειτουργίας',
            'price': 35.00,
            'category': 'test'
        }
    ]
    
    for service_data in default_services:
        # Check if service already exists
        existing_service = Service.query.filter_by(name=service_data['name']).first()
        if existing_service:
            print(f"   ⚠️  Service '{service_data['name']}' already exists, skipping...")
            continue
        
        service = Service(
            name=service_data['name'],
            description=service_data['description'],
            price=service_data['price'],
            category=service_data['category'],
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(service)
        print(f"   ✓ Created service: {service.name} (€{service.price})")


def print_default_credentials():
    """Print default login credentials"""
    secondary_password = "kp020716"
    
    default_users = [
        {
            'username': 'admin',
            'password': 'admin123',
            'role': 'Διαχειριστής'
        },
        {
            'username': 'platipelagia',
            'password': 'm8a9g6p1',
            'role': 'Γιατρός'
        },
        {
            'username': 'secretary',
            'password': '2841023830',
            'role': 'Γραμματέας'
        }
    ]
    
    print("\n" + "="*80)
    print("🔐 ΠΡΟΕΠΙΛΕΓΜΕΝΑ ΣΤΟΙΧΕΙΑ ΣΥΝΔΕΣΗΣ:")
    print("="*80)
    print("\nURL: http://localhost:8080")
    print("Όλοι οι λογαριασμοί χρησιμοποιούν dual-password authentication:\n")
    
    for user_data in default_users:
        print(f"👤 {user_data['role']}:")
        print(f"   Username: {user_data['username']}")
        print(f"   Password 1: {user_data['password']}")
        print(f"   Password 2: {secondary_password}")
        print()
    
    print("⚠️  ΣΗΜΑΝΤΙΚΟ: Αλλάξτε τους προεπιλεγμένους κωδικούς στο production!")
    print("="*80 + "\n")


if __name__ == '__main__':
    init_database()
