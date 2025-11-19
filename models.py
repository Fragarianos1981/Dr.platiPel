# -*- coding: utf-8 -*-
"""
models.py
Database Models για Dr. PLATI - DATABASE COMPATIBLE VERSION
Pediatric Practice Management System
"""

from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Index
from datetime import datetime, date, timedelta
import secrets


class User(UserMixin, db.Model):
    """User model για authentication - COMPATIBLE με existing database"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password1_hash = db.Column(db.String(255), nullable=False)  # CORRECT FIELD NAME
    password2 = db.Column(db.String(255), nullable=False)      # CORRECT FIELD NAME
    
    # Profile Information - EXISTING DATABASE SCHEMA
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    
    # Role & Status
    role = db.Column(db.Enum('topuser', 'doctor', 'secretary'), nullable=False, default='secretary')
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Password Reset
    reset_token = db.Column(db.String(100))
    reset_token_expires = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Set primary password - USES CORRECT FIELD NAME"""
        self.password1_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check primary password - USES CORRECT FIELD NAME"""
        return check_password_hash(self.password1_hash, password)
    
    def set_password2(self, password2):
        """Set secondary password - STORES AS PLAINTEXT"""
        self.password2 = password2
    
    def check_password2(self, password2):
        """Check secondary password - DIRECT COMPARISON"""
        return self.password2 == password2
    
    def generate_reset_token(self):
        """Generate password reset token"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expires = datetime.utcnow() + timedelta(hours=24)
    
    @property
    def full_name(self):
        """Computed full name από first_name + last_name - COMPATIBLE με init code"""
        return f"{self.first_name} {self.last_name}".strip()

    @full_name.setter 
    def full_name(self, value):
        """Set full name και split σε first_name/last_name - COMPATIBLE με init code"""
        if value:
            parts = value.strip().split(' ', 1)
            self.first_name = parts[0]
            self.last_name = parts[1] if len(parts) > 1 else ""
        else:
            self.first_name = ""
            self.last_name = ""
    
    def set_names(self, first_name, last_name):
        """Set names από separate first/last names"""
        self.first_name = first_name
        self.last_name = last_name
    
    @property
    def is_topuser(self):
        return self.role == 'topuser'
    
    @property
    def is_doctor(self):
        return self.role in ['topuser', 'doctor']
    
    @property
    def is_secretary(self):
        return self.role in ['topuser', 'doctor', 'secretary']
    
    @property
    def role_display(self):
        """Display name για role"""
        role_names = {
            'topuser': 'Super Admin',
            'doctor': 'Γιατρός',
            'secretary': 'Γραμματέας'
        }
        return role_names.get(self.role, self.role)
    
    def can_access_patients(self):
        """Check if user can access patients"""
        return self.role in ['topuser', 'doctor', 'secretary']
    
    def can_modify_users(self):
        """Check if user can modify users"""
        return self.role in ['topuser']
    
    def can_access_billing(self):
        """Check if user can access billing"""
        return self.role in ['topuser', 'doctor', 'secretary']
    
    def can_issue_certificates(self):
        """Check if user can issue certificates"""
        return self.role in ['topuser', 'doctor']
    
    def get_display_info(self):
        """Get formatted user info for display"""
        return {
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role_display,
            'email': self.email or 'Δεν έχει οριστεί',
            'phone': self.phone or 'Δεν έχει οριστεί',
            'created_at': self.created_at.strftime('%d/%m/%Y') if self.created_at else 'Άγνωστο',
            'is_active': 'Ενεργός' if self.is_active else 'Ανενεργός'
        }
    
    def to_dict(self):
        """Convert user to dictionary (safe for JSON)"""
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'role_display': self.role_display,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
    
    def __str__(self):
        return f"{self.full_name} ({self.username})"


class Patient(db.Model):
    """Patient model"""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic Information
    amka = db.Column(db.String(11), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum('M', 'F'), nullable=False)
    place_of_birth = db.Column(db.String(100))
    
    # Contact Information
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # Parent/Guardian Information
    father_name = db.Column(db.String(100))
    father_surname = db.Column(db.String(100))
    father_phone = db.Column(db.String(20))
    father_email = db.Column(db.String(120))
    
    mother_name = db.Column(db.String(100))
    mother_surname = db.Column(db.String(100))
    mother_phone = db.Column(db.String(20))
    mother_email = db.Column(db.String(120))
    
    guardian_name = db.Column(db.String(100))
    guardian_surname = db.Column(db.String(100))
    guardian_phone = db.Column(db.String(20))
    guardian_email = db.Column(db.String(120))
    guardian_relation = db.Column(db.String(50))
    
    # Medical Information
    insurance = db.Column(db.String(100))
    insurance_number = db.Column(db.String(50))
    allergies = db.Column(db.Text)
    chronic_conditions = db.Column(db.Text)
    medications = db.Column(db.Text)
    blood_type = db.Column(db.String(5))
    
    # Birth Information
    birth_weight = db.Column(db.Float)  # σε kg
    birth_height = db.Column(db.Float)  # σε cm
    gestational_age = db.Column(db.Integer)  # σε εβδομάδες
    delivery_type = db.Column(db.String(50))
    apgar_1min = db.Column(db.Integer)
    apgar_5min = db.Column(db.Integer)
    
    # Growth Tracking
    current_weight = db.Column(db.Float)
    current_height = db.Column(db.Float)
    head_circumference = db.Column(db.Float)
    
    # Notes
    notes = db.Column(db.Text)
    family_history = db.Column(db.Text)
    
    # Status & Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    visits = db.relationship('Visit', backref='patient', lazy=True, cascade='all, delete-orphan')
    vaccines = db.relationship('Vaccine', backref='patient', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='patient', lazy=True, cascade='all, delete-orphan')
    certificates = db.relationship('CertificateLog', backref='patient', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_patients')
    
    def calculate_age(self):
        """Calculate patient age in years, months, days"""
        today = date.today()
        born = self.date_of_birth
        
        years = today.year - born.year
        months = today.month - born.month
        days = today.day - born.day
        
        if days < 0:
            months -= 1
            days += 30  # Approximate
        if months < 0:
            years -= 1
            months += 12
            
        return {
            'years': years,
            'months': months,
            'days': days,
            'total_days': (today - born).days
        }
    
    @property
    def age_string(self):
        """Format age as string"""
        age = self.calculate_age()
        if age['years'] >= 2:
            return f"{age['years']} ετών"
        elif age['years'] == 1:
            return f"1 έτους και {age['months']} μηνών"
        else:
            return f"{age['months']} μηνών"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<Patient {self.full_name} ({self.amka})>'


class Visit(db.Model):
    """Visit/Appointment model"""
    __tablename__ = 'visits'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    visit_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    visit_type = db.Column(db.Enum('checkup', 'sick', 'followup', 'vaccination', 'emergency'), 
                          nullable=False, default='checkup')
    
    # Chief Complaint & History
    chief_complaint = db.Column(db.Text)
    history_present_illness = db.Column(db.Text)
    
    # Vital Signs
    weight = db.Column(db.Float)  # kg
    height = db.Column(db.Float)  # cm
    head_circumference = db.Column(db.Float)  # cm
    temperature = db.Column(db.Float)  # Celsius
    heart_rate = db.Column(db.Integer)  # bpm
    respiratory_rate = db.Column(db.Integer)  # per minute
    blood_pressure_systolic = db.Column(db.Integer)  # mmHg
    blood_pressure_diastolic = db.Column(db.Integer)  # mmHg
    oxygen_saturation = db.Column(db.Float)  # percentage
    
    # Physical Examination
    general_appearance = db.Column(db.Text)
    skin = db.Column(db.Text)
    head_neck = db.Column(db.Text)
    cardiovascular = db.Column(db.Text)
    respiratory = db.Column(db.Text)
    abdomen = db.Column(db.Text)
    neurological = db.Column(db.Text)
    musculoskeletal = db.Column(db.Text)
    
    # Assessment & Plan
    assessment = db.Column(db.Text)
    plan = db.Column(db.Text)
    medications = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    follow_up = db.Column(db.Text)
    
    # Administrative
    notes = db.Column(db.Text)
    next_visit_date = db.Column(db.Date)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    doctor = db.relationship('User', backref='visits')
    
    def __repr__(self):
        return f'<Visit {self.id} for {self.patient.full_name} on {self.visit_date}>'


class Vaccine(db.Model):
    """Vaccination records"""
    __tablename__ = 'vaccines'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    administered_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Vaccine Details
    vaccine_name = db.Column(db.String(100), nullable=False)
    vaccine_type = db.Column(db.String(50))  # MMR, DTaP, etc.
    manufacturer = db.Column(db.String(100))
    batch_number = db.Column(db.String(50))
    lot_number = db.Column(db.String(50))
    expiration_date = db.Column(db.Date)
    
    # Administration Details
    date_administered = db.Column(db.Date, nullable=False, default=date.today)
    dose_number = db.Column(db.Integer)  # 1st dose, 2nd dose, etc.
    dose_amount = db.Column(db.String(20))  # e.g., '0.5ml'
    route = db.Column(db.String(50))  # IM, SC, Oral, etc.
    site = db.Column(db.String(50))  # Left deltoid, Right thigh, etc.
    
    # Age at administration
    age_at_administration = db.Column(db.String(50))  # Calculated from patient DOB
    
    # Reaction & Notes
    adverse_reactions = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Next dose information
    next_dose_due = db.Column(db.Date)
    next_dose_notes = db.Column(db.String(200))
    
    # Status
    is_valid = db.Column(db.Boolean, default=True)  # Valid vaccination
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    administrator = db.relationship('User', backref='administered_vaccines')
    
    def __repr__(self):
        return f'<Vaccine {self.vaccine_name} for {self.patient.full_name} on {self.date_administered}>'


class Service(db.Model):
    """Medical services and pricing"""
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Decimal(10, 2), nullable=False)
    category = db.Column(db.String(50))  # checkup, vaccination, consultation, etc.
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Service {self.name} - €{self.price}>'


class Transaction(db.Model):
    """Financial transactions/billing"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    visit_id = db.Column(db.Integer, db.ForeignKey('visits.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Transaction Details
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    transaction_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    
    # Services & Pricing
    services_json = db.Column(db.Text)  # JSON string of services
    subtotal = db.Column(db.Decimal(10, 2), nullable=False)
    discount = db.Column(db.Decimal(10, 2), default=0)
    tax_rate = db.Column(db.Decimal(5, 4), default=0.24)  # 24% ΦΠΑ
    tax_amount = db.Column(db.Decimal(10, 2), default=0)
    total_amount = db.Column(db.Decimal(10, 2), nullable=False)
    
    # Payment Information
    payment_method = db.Column(db.Enum('cash', 'card', 'transfer', 'insurance'), 
                              nullable=False, default='cash')
    payment_status = db.Column(db.Enum('pending', 'paid', 'partial', 'cancelled'), 
                              nullable=False, default='pending')
    paid_amount = db.Column(db.Decimal(10, 2), default=0)
    
    # Insurance
    insurance_coverage = db.Column(db.Decimal(10, 2), default=0)
    insurance_claim_number = db.Column(db.String(50))
    
    # Notes
    notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_date = db.Column(db.DateTime)
    
    # Relationships
    visit = db.relationship('Visit', backref='transactions')
    creator = db.relationship('User', backref='created_transactions')
    
    @property
    def balance_due(self):
        """Remaining amount to be paid"""
        return self.total_amount - self.paid_amount - self.insurance_coverage
    
    @property
    def is_fully_paid(self):
        """Check if transaction is fully paid"""
        return self.balance_due <= 0
    
    def __repr__(self):
        return f'<Transaction {self.invoice_number} - €{self.total_amount}>'


class CertificateLog(db.Model):
    """Medical certificates issued"""
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    issued_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Certificate Details
    certificate_type = db.Column(db.String(100), nullable=False)  # Health Certificate, Absence, etc.
    certificate_number = db.Column(db.String(50), unique=True, nullable=False)
    issue_date = db.Column(db.Date, nullable=False, default=date.today)
    valid_from = db.Column(db.Date)
    valid_until = db.Column(db.Date)
    
    # Content
    purpose = db.Column(db.String(200))  # School, Sports, Travel, etc.
    findings = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    limitations = db.Column(db.Text)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # File path (if PDF generated)
    file_path = db.Column(db.String(255))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    issuer = db.relationship('User', backref='issued_certificates')
    
    def __repr__(self):
        return f'<Certificate {self.certificate_number} for {self.patient.full_name}>'


class ChatMessage(db.Model):
    """Team communication/chat messages"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Message Details
    message_type = db.Column(db.Enum('note', 'reminder', 'urgent', 'info'), 
                           nullable=False, default='note')
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    
    # Targeting (optional - for patient-specific messages)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_pinned = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    
    # Relationships
    sender = db.relationship('User', backref='sent_messages')
    related_patient = db.relationship('Patient', backref='related_messages')
    
    def __repr__(self):
        return f'<ChatMessage {self.id} by {self.sender.username}>'


class StealthCalendar(db.Model):
    """Stealth feature - Private calendar entries (encrypted)"""
    __tablename__ = 'stealth_calendar'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Encrypted fields
    encrypted_title = db.Column(db.Text, nullable=False)
    encrypted_description = db.Column(db.Text)
    encrypted_amount = db.Column(db.Text)  # For revenue tracking
    
    # Date/Time (not encrypted for querying)
    event_date = db.Column(db.Date, nullable=False, index=True)
    event_time = db.Column(db.Time)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='stealth_entries')
    
    def __repr__(self):
        return f'<StealthCalendar {self.id} for {self.user.username}>'


# Database Indexes για Performance
Index('idx_patient_amka', Patient.amka)
Index('idx_patient_name', Patient.last_name, Patient.first_name)
Index('idx_patient_phone', Patient.phone)
Index('idx_patient_dob', Patient.date_of_birth)
Index('idx_visit_date', Visit.visit_date)
Index('idx_visit_patient', Visit.patient_id, Visit.visit_date)
Index('idx_transaction_date', Transaction.transaction_date)
Index('idx_transaction_patient', Transaction.patient_id)
Index('idx_vaccine_patient', Vaccine.patient_id, Vaccine.date_administered)
Index('idx_certificate_patient', CertificateLog.patient_id, CertificateLog.issue_date)
Index('idx_chat_created', ChatMessage.created_at)
Index('idx_stealth_date', StealthCalendar.event_date, StealthCalendar.user_id)