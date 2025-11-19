# -*- coding: utf-8 -*-
"""
utils.py
Utility functions για Dr. PLATI
"""

import re
import secrets
import string
from datetime import datetime, date, timedelta
from cryptography.fernet import Fernet
import base64
import hashlib
import json


def validate_amka(amka):
    """
    Validate Greek AMKA (Social Security Number)
    AMKA πρέπει να έχει 11 ψηφία
    """
    if not amka:
        return False, "Το AMKA είναι υποχρεωτικό"
    
    # Remove any non-digit characters
    amka_clean = re.sub(r'[^0-9]', '', str(amka))
    
    if len(amka_clean) != 11:
        return False, "Το AMKA πρέπει να έχει 11 ψηφία"
    
    if not amka_clean.isdigit():
        return False, "Το AMKA πρέπει να περιέχει μόνο αριθμούς"
    
    # Additional AMKA validation algorithm (simplified)
    try:
        # The last digit is a check digit
        check_sum = sum(int(amka_clean[i]) * (11 - i) for i in range(10))
        check_digit = check_sum % 11
        
        if check_digit >= 10:
            check_digit = 0
        
        if int(amka_clean[10]) != check_digit:
            return False, "Μη έγκυρο AMKA (λάθος ψηφίο ελέγχου)"
        
    except (ValueError, IndexError):
        return False, "Μη έγκυρο AMKA"
    
    return True, "Έγκυρο AMKA"


def validate_email(email):
    """Validate email address"""
    if not email:
        return True, "Email είναι προαιρετικό"  # Email is optional
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, "Έγκυρο email"
    else:
        return False, "Μη έγκυρη διεύθυνση email"


def validate_phone(phone):
    """Validate Greek phone number"""
    if not phone:
        return True, "Τηλέφωνο είναι προαιρετικό"
    
    # Remove spaces, dashes, parentheses
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Greek phone patterns
    patterns = [
        r'^2\d{9}$',        # Landline (10 digits starting with 2)
        r'^69\d{8}$',       # Mobile (10 digits starting with 69)
        r'^(\+30)?2\d{9}$', # Landline with country code
        r'^(\+30)?69\d{8}$' # Mobile with country code
    ]
    
    for pattern in patterns:
        if re.match(pattern, phone_clean):
            return True, "Έγκυρο τηλέφωνο"
    
    return False, "Μη έγκυρο τηλέφωνο (πρέπει να είναι ελληνικό)"


def calculate_age(birth_date):
    """
    Calculate age from birth date
    Returns dict with years, months, days
    """
    if not isinstance(birth_date, date):
        return None
    
    today = date.today()
    
    years = today.year - birth_date.year
    months = today.month - birth_date.month
    days = today.day - birth_date.day
    
    # Adjust for negative days
    if days < 0:
        months -= 1
        # Get days in previous month
        if today.month == 1:
            prev_month = 12
            prev_year = today.year - 1
        else:
            prev_month = today.month - 1
            prev_year = today.year
        
        # Simple calculation - assume 30 days per month for simplicity
        days += 30
    
    # Adjust for negative months
    if months < 0:
        years -= 1
        months += 12
    
    return {
        'years': years,
        'months': months,
        'days': days,
        'total_days': (today - birth_date).days
    }


def format_age(birth_date):
    """Format age as string"""
    age = calculate_age(birth_date)
    if not age:
        return "Άγνωστη ηλικία"
    
    if age['years'] >= 2:
        return f"{age['years']} ετών"
    elif age['years'] == 1:
        return f"1 έτους και {age['months']} μηνών"
    elif age['months'] > 0:
        return f"{age['months']} μηνών"
    else:
        return f"{age['days']} ημερών"


def generate_invoice_number():
    """Generate unique invoice number"""
    today = datetime.now()
    year = today.year
    month = today.month
    
    # Format: YYYYMM-XXXXXX (random 6 digits)
    random_part = ''.join(secrets.choice(string.digits) for _ in range(6))
    return f"{year}{month:02d}-{random_part}"


def generate_certificate_number():
    """Generate unique certificate number"""
    today = datetime.now()
    year = today.year
    
    # Format: CERT-YYYY-XXXXXX
    random_part = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"CERT-{year}-{random_part}"


def format_currency(amount, currency="€"):
    """Format amount as currency"""
    if amount is None:
        return f"0,00 {currency}"
    
    # Convert to float if it's Decimal
    amount_float = float(amount)
    
    # Format with Greek locale style (comma for decimal)
    return f"{amount_float:,.2f} {currency}".replace(',', 'TEMP').replace('.', ',').replace('TEMP', '.')


def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\s\-_\.]', '', filename)
    filename = re.sub(r'[\s]+', '_', filename)
    return filename[:255]  # Limit length


def generate_secure_token(length=32):
    """Generate secure random token"""
    return secrets.token_urlsafe(length)


# Encryption utilities (για stealth features)
class EncryptionHelper:
    """Helper class for encryption/decryption of stealth data"""
    
    def __init__(self, key=None):
        if key:
            self.cipher = Fernet(key.encode())
        else:
            # Generate a key from a master password
            self.cipher = Fernet(self._generate_key_from_password('kp020716_stealth'))
    
    def _generate_key_from_password(self, password):
        """Generate Fernet key from password"""
        # Use PBKDF2 to derive key from password
        import hashlib
        key = hashlib.pbkdf2_hmac('sha256', 
                                 password.encode('utf-8'), 
                                 b'dr_plati_salt', 
                                 100000)
        return base64.urlsafe_b64encode(key)
    
    def encrypt(self, plaintext):
        """Encrypt plaintext string"""
        if not plaintext:
            return ""
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, encrypted_text):
        """Decrypt encrypted string"""
        if not encrypted_text:
            return ""
        try:
            return self.cipher.decrypt(encrypted_text.encode()).decode()
        except:
            return "DECRYPTION_ERROR"


# Date formatting utilities
def format_date_gr(date_obj):
    """Format date in Greek style (DD/MM/YYYY)"""
    if not date_obj:
        return ""
    
    if isinstance(date_obj, str):
        return date_obj
    
    return date_obj.strftime("%d/%m/%Y")


def format_datetime_gr(datetime_obj):
    """Format datetime in Greek style (DD/MM/YYYY HH:MM)"""
    if not datetime_obj:
        return ""
    
    if isinstance(datetime_obj, str):
        return datetime_obj
    
    return datetime_obj.strftime("%d/%m/%Y %H:%M")


def parse_date_gr(date_string):
    """Parse Greek format date string (DD/MM/YYYY)"""
    if not date_string:
        return None
    
    try:
        return datetime.strptime(date_string, "%d/%m/%Y").date()
    except ValueError:
        try:
            return datetime.strptime(date_string, "%Y-%m-%d").date()
        except ValueError:
            return None


# BMI and Growth utilities
def calculate_bmi(weight_kg, height_cm):
    """Calculate BMI from weight (kg) and height (cm)"""
    if not weight_kg or not height_cm or height_cm == 0:
        return None
    
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 1)


def classify_bmi_pediatric(bmi, age_months):
    """
    Classify pediatric BMI (simplified)
    This is a basic implementation - proper pediatric BMI requires CDC growth charts
    """
    if not bmi or not age_months:
        return "Δεν είναι δυνατή η κατηγοριοποίηση"
    
    # Simplified classification for demonstration
    if bmi < 14:
        return "Υποβάρος"
    elif bmi < 18:
        return "Κανονικό βάρος"
    elif bmi < 22:
        return "Υπέρβαρος"
    else:
        return "Παχύσαρκος"


# Search utilities
def normalize_search_term(term):
    """Normalize search term for better matching"""
    if not term:
        return ""
    
    # Convert to lowercase and remove extra spaces
    term = term.lower().strip()
    
    # Remove Greek accents for better searching
    accent_map = {
        'ά': 'α', 'έ': 'ε', 'ή': 'η', 'ί': 'ι', 'ό': 'ο', 'ύ': 'υ', 'ώ': 'ω',
        'ΐ': 'ι', 'ΰ': 'υ'
    }
    
    for accented, plain in accent_map.items():
        term = term.replace(accented, plain)
    
    return term


# Form validation utilities
def validate_required_fields(data, required_fields):
    """
    Validate required fields in form data
    Returns (is_valid, errors_dict)
    """
    errors = {}
    
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            errors[field] = f"Το πεδίο είναι υποχρεωτικό"
    
    return len(errors) == 0, errors


def clean_form_data(data):
    """Clean form data by stripping whitespace and converting empty strings to None"""
    cleaned = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            value = value.strip()
            if value == '':
                value = None
        cleaned[key] = value
    
    return cleaned


# JSON utilities for complex data storage
def serialize_for_db(data):
    """Serialize data for database storage"""
    if data is None:
        return None
    return json.dumps(data, ensure_ascii=False, default=str)


def deserialize_from_db(data_str):
    """Deserialize data from database"""
    if not data_str:
        return {}
    try:
        return json.loads(data_str)
    except (json.JSONDecodeError, TypeError):
        return {}


# Logging utilities
def log_user_action(user, action, details=""):
    """Log user action (could be extended to save to database)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] User {user.username} ({user.role}): {action}"
    if details:
        log_message += f" - {details}"
    
    # For now, just print. In production, save to log file or database
    print(log_message)


# Template filters (to be registered with Flask app)
def register_template_filters(app):
    """Register custom template filters with Flask app"""
    
    @app.template_filter('format_date_gr')
    def format_date_gr_filter(date_obj):
        return format_date_gr(date_obj)
    
    @app.template_filter('format_datetime_gr')
    def format_datetime_gr_filter(datetime_obj):
        return format_datetime_gr(datetime_obj)
    
    @app.template_filter('format_currency')
    def format_currency_filter(amount):
        return format_currency(amount)
    
    @app.template_filter('format_age')
    def format_age_filter(birth_date):
        return format_age(birth_date)
    
    @app.template_filter('calculate_bmi')
    def calculate_bmi_filter(weight_height_tuple):
        """Template filter for BMI calculation"""
        if isinstance(weight_height_tuple, (list, tuple)) and len(weight_height_tuple) == 2:
            weight, height = weight_height_tuple
            return calculate_bmi(weight, height)
        return None
