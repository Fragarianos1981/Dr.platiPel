# -*- coding: utf-8 -*-
"""
auth.py
Authentication decorators και security functions για Dr. PLATI
"""

from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user


def login_required(f):
    """Requires user to be logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Παρακαλώ συνδεθείτε για να συνεχίσετε.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def topuser_required(f):
    """Requires topuser role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Παρακαλώ συνδεθείτε για να συνεχίσετε.', 'warning')
            return redirect(url_for('login'))
        
        if not current_user.is_topuser:
            flash('Δεν έχετε δικαίωμα πρόσβασης σε αυτή τη σελίδα.', 'danger')
            return abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def doctor_required(f):
    """Requires doctor or topuser role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Παρακαλώ συνδεθείτε για να συνεχίσετε.', 'warning')
            return redirect(url_for('login'))
        
        if not current_user.is_doctor:
            flash('Δεν έχετε δικαίωμα πρόσβασης σε αυτή τη σελίδα.', 'danger')
            return abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def secretary_required(f):
    """Requires any authenticated user (secretary, doctor, or topuser)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Παρακαλώ συνδεθείτε για να συνεχίσετε.', 'warning')
            return redirect(url_for('login'))
        
        if not current_user.is_secretary:
            flash('Δεν έχετε δικαίωμα πρόσβασης σε αυτή τη σελίδα.', 'danger')
            return abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles):
    """Generic role checker decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Παρακαλώ συνδεθείτε για να συνεχίσετε.', 'warning')
                return redirect(url_for('login'))
            
            if current_user.role not in allowed_roles:
                flash('Δεν έχετε δικαίωμα πρόσβασης σε αυτή τη σελίδα.', 'danger')
                return abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def check_password_strength(password):
    """
    Check password strength
    Returns (is_valid, message)
    """
    if len(password) < 6:
        return False, "Ο κωδικός πρέπει να έχει τουλάχιστον 6 χαρακτήρες"
    
    if len(password) < 8:
        return True, "Καλός κωδικός"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if has_upper and has_lower and has_digit:
        return True, "Πολύ ισχυρός κωδικός"
    elif (has_upper and has_lower) or (has_lower and has_digit):
        return True, "Ισχυρός κωδικός"
    else:
        return True, "Μέτριος κωδικός"
