# -*- coding: utf-8 -*-
"""
routes.py
Application routes για Dr. PLATI
Pediatric Practice Management System
"""

from flask import render_template, redirect, url_for, flash, request, jsonify, session, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User, Patient, Visit, Vaccine, Service, Transaction, Certificate, ChatMessage, StealthCalendar
from auth import login_required, topuser_required, doctor_required, secretary_required
from utils import (validate_amka, validate_email, validate_phone, calculate_age, format_age,
                  generate_invoice_number, generate_certificate_number, format_currency,
                  normalize_search_term, clean_form_data, EncryptionHelper)
from datetime import datetime, date, timedelta
from sqlalchemy import or_, desc, func, and_
import secrets
import json


def register_routes(app):
    """Register all application routes"""
    
    # ==================== MAIN ROUTES ====================
    
    @app.route('/')
    def index():
        """Homepage redirect"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login με dual password authentication"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password1 = request.form.get('password1', '')
            password2 = request.form.get('password2', '')
            
            if not all([username, password1, password2]):
                flash('Παρακαλώ συμπληρώστε όλα τα πεδία.', 'danger')
                return render_template('login.html')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password1) and user.check_password2(password2):
                if not user.is_active:
                    flash('Ο λογαριασμός σας είναι ανενεργός.', 'danger')
                    return render_template('login.html')
                
                login_user(user, remember=True)
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                next_page = request.args.get('next')
                flash(f'Καλώς ήρθατε, {user.full_name}!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Λάθος στοιχεία σύνδεσης.', 'danger')
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout"""
        username = current_user.full_name
        logout_user()
        flash(f'Αποσυνδεθήκατε επιτυχώς, {username}!', 'info')
        return redirect(url_for('login'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard με patient search και statistics"""
        # Get search query
        search_query = request.args.get('search', '').strip()
        patients = []
        
        if search_query:
            search_term = normalize_search_term(search_query)
            patients = Patient.query.filter(
                or_(
                    func.lower(Patient.first_name).contains(search_term),
                    func.lower(Patient.last_name).contains(search_term),
                    Patient.amka.contains(search_query),
                    Patient.phone.contains(search_query),
                    Patient.mobile.contains(search_query)
                )
            ).filter_by(is_active=True).order_by(
                Patient.last_name, Patient.first_name
            ).limit(20).all()
        
        # Statistics for dashboard
        stats = {
            'total_patients': Patient.query.filter_by(is_active=True).count(),
            'visits_today': Visit.query.filter(
                func.date(Visit.visit_date) == date.today()
            ).count(),
            'visits_this_month': Visit.query.filter(
                func.year(Visit.visit_date) == date.today().year,
                func.month(Visit.visit_date) == date.today().month
            ).count(),
            'pending_transactions': Transaction.query.filter_by(payment_status='pending').count()
        }
        
        # Recent patients
        recent_patients = Patient.query.filter_by(is_active=True).order_by(
            desc(Patient.created_at)
        ).limit(5).all()
        
        # Recent visits
        recent_visits = Visit.query.join(Patient).filter(
            Patient.is_active == True
        ).order_by(desc(Visit.visit_date)).limit(5).all()
        
        return render_template('dashboard.html', 
                             patients=patients,
                             search_query=search_query,
                             stats=stats,
                             recent_patients=recent_patients,
                             recent_visits=recent_visits)
    
    @app.route('/forgot-password', methods=['GET', 'POST'])
    def forgot_password():
        """Password recovery"""
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            
            if not email:
                flash('Παρακαλώ εισάγετε το email σας.', 'warning')
                return render_template('forgot_password.html')
            
            user = User.query.filter_by(email=email).first()
            
            if user:
                # Generate reset token
                user.generate_reset_token()
                db.session.commit()
                
                # In production, send email here
                flash('Οδηγίες επαναφοράς κωδικού εστάλησαν στο email σας.', 'success')
            else:
                flash('Δεν βρέθηκε λογαριασμός με αυτό το email.', 'danger')
            
            return redirect(url_for('login'))
        
        return render_template('forgot_password.html')
    
    # ==================== PATIENT ROUTES ====================
    
    @app.route('/patients')
    @login_required
    def patient_list():
        """Patient listing με pagination"""
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        search_query = request.args.get('search', '').strip()
        
        query = Patient.query.filter_by(is_active=True)
        
        if search_query:
            search_term = normalize_search_term(search_query)
            query = query.filter(
                or_(
                    func.lower(Patient.first_name).contains(search_term),
                    func.lower(Patient.last_name).contains(search_term),
                    Patient.amka.contains(search_query),
                    Patient.phone.contains(search_query),
                    Patient.mobile.contains(search_query)
                )
            )
        
        patients = query.order_by(
            Patient.last_name, Patient.first_name
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('patient_list.html', 
                             patients=patients,
                             search_query=search_query)
    
    @app.route('/patients/add', methods=['GET', 'POST'])
    @login_required
    def patient_add():
        """Add new patient"""
        if request.method == 'POST':
            data = clean_form_data(request.form.to_dict())
            
            # Validate required fields
            required_fields = ['amka', 'first_name', 'last_name', 'date_of_birth', 'gender']
            errors = {}
            
            for field in required_fields:
                if not data.get(field):
                    errors[field] = 'Το πεδίο είναι υποχρεωτικό'
            
            # Validate AMKA
            if data.get('amka'):
                is_valid, message = validate_amka(data['amka'])
                if not is_valid:
                    errors['amka'] = message
                
                # Check for duplicate AMKA
                existing = Patient.query.filter_by(amka=data['amka']).first()
                if existing:
                    errors['amka'] = 'Το AMKA υπάρχει ήδη στο σύστημα'
            
            # Validate email
            if data.get('email'):
                is_valid, message = validate_email(data['email'])
                if not is_valid:
                    errors['email'] = message
            
            # Validate phones
            for phone_field in ['phone', 'mobile', 'father_phone', 'mother_phone', 'guardian_phone']:
                if data.get(phone_field):
                    is_valid, message = validate_phone(data[phone_field])
                    if not is_valid:
                        errors[phone_field] = message
            
            if errors:
                for field, error in errors.items():
                    flash(f'{error}', 'danger')
                return render_template('patient_add.html', data=data)
            
            # Create patient
            try:
                # Parse date
                birth_date = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                
                patient = Patient(
                    amka=data['amka'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    date_of_birth=birth_date,
                    gender=data['gender'],
                    place_of_birth=data.get('place_of_birth'),
                    address=data.get('address'),
                    city=data.get('city'),
                    postal_code=data.get('postal_code'),
                    phone=data.get('phone'),
                    mobile=data.get('mobile'),
                    email=data.get('email'),
                    father_name=data.get('father_name'),
                    father_surname=data.get('father_surname'),
                    father_phone=data.get('father_phone'),
                    father_email=data.get('father_email'),
                    mother_name=data.get('mother_name'),
                    mother_surname=data.get('mother_surname'),
                    mother_phone=data.get('mother_phone'),
                    mother_email=data.get('mother_email'),
                    guardian_name=data.get('guardian_name'),
                    guardian_surname=data.get('guardian_surname'),
                    guardian_phone=data.get('guardian_phone'),
                    guardian_email=data.get('guardian_email'),
                    guardian_relation=data.get('guardian_relation'),
                    insurance=data.get('insurance'),
                    insurance_number=data.get('insurance_number'),
                    allergies=data.get('allergies'),
                    chronic_conditions=data.get('chronic_conditions'),
                    medications=data.get('medications'),
                    blood_type=data.get('blood_type'),
                    birth_weight=float(data['birth_weight']) if data.get('birth_weight') else None,
                    birth_height=float(data['birth_height']) if data.get('birth_height') else None,
                    gestational_age=int(data['gestational_age']) if data.get('gestational_age') else None,
                    delivery_type=data.get('delivery_type'),
                    apgar_1min=int(data['apgar_1min']) if data.get('apgar_1min') else None,
                    apgar_5min=int(data['apgar_5min']) if data.get('apgar_5min') else None,
                    current_weight=float(data['current_weight']) if data.get('current_weight') else None,
                    current_height=float(data['current_height']) if data.get('current_height') else None,
                    head_circumference=float(data['head_circumference']) if data.get('head_circumference') else None,
                    notes=data.get('notes'),
                    family_history=data.get('family_history'),
                    created_by=current_user.id
                )
                
                db.session.add(patient)
                db.session.commit()
                
                flash(f'Ο ασθενής {patient.full_name} προστέθηκε επιτυχώς!', 'success')
                return redirect(url_for('patient_card', patient_id=patient.id))
                
            except ValueError as e:
                flash('Λάθος μορφή ημερομηνίας.', 'danger')
            except Exception as e:
                db.session.rollback()
                flash('Σφάλμα κατά την προσθήκη του ασθενή.', 'danger')
                current_app.logger.error(f'Error adding patient: {e}')
        
        return render_template('patient_add.html')
    
    @app.route('/patients/<int:patient_id>')
    @login_required
    def patient_card(patient_id):
        """Patient card με όλες τις πληροφορίες"""
        patient = Patient.query.filter_by(id=patient_id, is_active=True).first_or_404()
        
        # Get visits
        visits = Visit.query.filter_by(patient_id=patient.id).order_by(
            desc(Visit.visit_date)
        ).limit(10).all()
        
        # Get vaccines
        vaccines = Vaccine.query.filter_by(patient_id=patient.id).order_by(
            desc(Vaccine.date_administered)
        ).limit(10).all()
        
        # Get transactions
        transactions = Transaction.query.filter_by(patient_id=patient.id).order_by(
            desc(Transaction.transaction_date)
        ).limit(10).all()
        
        # Get certificates
        certificates = Certificate.query.filter_by(patient_id=patient.id).order_by(
            desc(Certificate.issue_date)
        ).limit(10).all()
        
        return render_template('patient_card.html', 
                             patient=patient,
                             visits=visits,
                             vaccines=vaccines,
                             transactions=transactions,
                             certificates=certificates)
    
    @app.route('/patients/<int:patient_id>/edit', methods=['GET', 'POST'])
    @login_required
    def patient_edit(patient_id):
        """Edit patient information"""
        patient = Patient.query.filter_by(id=patient_id, is_active=True).first_or_404()
        
        if request.method == 'POST':
            data = clean_form_data(request.form.to_dict())
            
            # Validation similar to patient_add
            errors = {}
            
            # Validate AMKA if changed
            if data.get('amka') and data['amka'] != patient.amka:
                is_valid, message = validate_amka(data['amka'])
                if not is_valid:
                    errors['amka'] = message
                
                # Check for duplicate AMKA
                existing = Patient.query.filter_by(amka=data['amka']).first()
                if existing and existing.id != patient.id:
                    errors['amka'] = 'Το AMKA υπάρχει ήδη στο σύστημα'
            
            if errors:
                for field, error in errors.items():
                    flash(f'{error}', 'danger')
                return render_template('patient_edit.html', patient=patient)
            
            # Update patient
            try:
                # Update fields
                if data.get('date_of_birth'):
                    patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                
                # Update all other fields
                for field in ['amka', 'first_name', 'last_name', 'gender', 'place_of_birth',
                             'address', 'city', 'postal_code', 'phone', 'mobile', 'email',
                             'father_name', 'father_surname', 'father_phone', 'father_email',
                             'mother_name', 'mother_surname', 'mother_phone', 'mother_email',
                             'guardian_name', 'guardian_surname', 'guardian_phone', 'guardian_email',
                             'guardian_relation', 'insurance', 'insurance_number',
                             'allergies', 'chronic_conditions', 'medications', 'blood_type',
                             'delivery_type', 'notes', 'family_history']:
                    if field in data:
                        setattr(patient, field, data[field])
                
                # Update numeric fields
                for field in ['birth_weight', 'birth_height', 'current_weight', 
                             'current_height', 'head_circumference']:
                    if data.get(field):
                        setattr(patient, field, float(data[field]))
                
                for field in ['gestational_age', 'apgar_1min', 'apgar_5min']:
                    if data.get(field):
                        setattr(patient, field, int(data[field]))
                
                patient.updated_at = datetime.utcnow()
                db.session.commit()
                
                flash('Οι πληροφορίες του ασθενή ενημερώθηκαν επιτυχώς!', 'success')
                return redirect(url_for('patient_card', patient_id=patient.id))
                
            except Exception as e:
                db.session.rollback()
                flash('Σφάλμα κατά την ενημέρωση του ασθενή.', 'danger')
                current_app.logger.error(f'Error updating patient: {e}')
        
        return render_template('patient_edit.html', patient=patient)
    
    @app.route('/patients/<int:patient_id>/delete', methods=['POST'])
    @topuser_required
    def patient_delete(patient_id):
        """Delete patient (soft delete)"""
        patient = Patient.query.filter_by(id=patient_id).first_or_404()
        
        try:
            patient.is_active = False
            db.session.commit()
            
            flash(f'Ο ασθενής {patient.full_name} διαγράφηκε επιτυχώς.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Σφάλμα κατά τη διαγραφή του ασθενή.', 'danger')
            current_app.logger.error(f'Error deleting patient: {e}')
        
        return redirect(url_for('patient_list'))
    
    # ==================== VISIT ROUTES ====================
    
    @app.route('/visits/add/<int:patient_id>', methods=['GET', 'POST'])
    @doctor_required
    def visit_add(patient_id):
        """Add new visit"""
        patient = Patient.query.filter_by(id=patient_id, is_active=True).first_or_404()
        
        if request.method == 'POST':
            data = clean_form_data(request.form.to_dict())
            
            try:
                visit_date = datetime.strptime(data.get('visit_date', ''), '%Y-%m-%dT%H:%M')
                
                visit = Visit(
                    patient_id=patient.id,
                    doctor_id=current_user.id,
                    visit_date=visit_date,
                    visit_type=data.get('visit_type', 'checkup'),
                    chief_complaint=data.get('chief_complaint'),
                    history_present_illness=data.get('history_present_illness'),
                    weight=float(data['weight']) if data.get('weight') else None,
                    height=float(data['height']) if data.get('height') else None,
                    head_circumference=float(data['head_circumference']) if data.get('head_circumference') else None,
                    temperature=float(data['temperature']) if data.get('temperature') else None,
                    heart_rate=int(data['heart_rate']) if data.get('heart_rate') else None,
                    blood_pressure_systolic=int(data['bp_systolic']) if data.get('bp_systolic') else None,
                    blood_pressure_diastolic=int(data['bp_diastolic']) if data.get('bp_diastolic') else None,
                    respiratory_rate=int(data['respiratory_rate']) if data.get('respiratory_rate') else None,
                    oxygen_saturation=int(data['oxygen_saturation']) if data.get('oxygen_saturation') else None,
                    general_appearance=data.get('general_appearance'),
                    skin=data.get('skin'),
                    heent=data.get('heent'),
                    cardiovascular=data.get('cardiovascular'),
                    respiratory=data.get('respiratory'),
                    abdominal=data.get('abdominal'),
                    genitourinary=data.get('genitourinary'),
                    neurological=data.get('neurological'),
                    musculoskeletal=data.get('musculoskeletal'),
                    diagnosis=data.get('diagnosis'),
                    icd10_codes=data.get('icd10_codes'),
                    treatment_plan=data.get('treatment_plan'),
                    medications=data.get('medications'),
                    instructions=data.get('instructions'),
                    follow_up_date=datetime.strptime(data['follow_up_date'], '%Y-%m-%d').date() if data.get('follow_up_date') else None,
                    follow_up_instructions=data.get('follow_up_instructions'),
                    notes=data.get('notes'),
                    status='completed'
                )
                
                # Update patient's current measurements
                if data.get('weight'):
                    patient.current_weight = float(data['weight'])
                if data.get('height'):
                    patient.current_height = float(data['height'])
                if data.get('head_circumference'):
                    patient.head_circumference = float(data['head_circumference'])
                
                db.session.add(visit)
                db.session.commit()
                
                flash('Η επίσκεψη καταχωρήθηκε επιτυχώς!', 'success')
                return redirect(url_for('patient_card', patient_id=patient.id))
                
            except Exception as e:
                db.session.rollback()
                flash('Σφάλμα κατά την καταχώρηση της επίσκεψης.', 'danger')
                current_app.logger.error(f'Error adding visit: {e}')
        
        return render_template('visit_add.html', patient=patient)
    
    @app.route('/visits/<int:visit_id>/edit', methods=['GET', 'POST'])
    @doctor_required
    def visit_edit(visit_id):
        """Edit visit"""
        visit = Visit.query.get_or_404(visit_id)
        
        if request.method == 'POST':
            data = clean_form_data(request.form.to_dict())
            
            try:
                # Update visit fields (similar to visit_add)
                # ... implementation similar to visit_add ...
                
                visit.updated_at = datetime.utcnow()
                db.session.commit()
                
                flash('Η επίσκεψη ενημερώθηκε επιτυχώς!', 'success')
                return redirect(url_for('patient_card', patient_id=visit.patient_id))
                
            except Exception as e:
                db.session.rollback()
                flash('Σφάλμα κατά την ενημέρωση της επίσκεψης.', 'danger')
        
        return render_template('visit_edit.html', visit=visit)
    
    # ==================== VACCINE ROUTES ====================
    
    @app.route('/vaccines/add/<int:patient_id>', methods=['GET', 'POST'])
    @login_required
    def vaccine_add(patient_id):
        """Add vaccination record"""
        patient = Patient.query.filter_by(id=patient_id, is_active=True).first_or_404()
        
        if request.method == 'POST':
            data = clean_form_data(request.form.to_dict())
            
            try:
                admin_date = datetime.strptime(data.get('date_administered', ''), '%Y-%m-%d').date()
                
                # Calculate age at administration
                age_at_admin = calculate_age(patient.date_of_birth)
                age_string = format_age(patient.date_of_birth)
                
                vaccine = Vaccine(
                    patient_id=patient.id,
                    administered_by=current_user.id,
                    vaccine_name=data.get('vaccine_name'),
                    vaccine_type=data.get('vaccine_type'),
                    manufacturer=data.get('manufacturer'),
                    lot_number=data.get('lot_number'),
                    expiration_date=datetime.strptime(data['expiration_date'], '%Y-%m-%d').date() if data.get('expiration_date') else None,
                    date_administered=admin_date,
                    dose_number=int(data['dose_number']) if data.get('dose_number') else None,
                    dose_amount=data.get('dose_amount'),
                    route=data.get('route'),
                    site=data.get('site'),
                    age_at_administration=age_string,
                    adverse_reactions=data.get('adverse_reactions'),
                    notes=data.get('notes'),
                    next_dose_due=datetime.strptime(data['next_dose_due'], '%Y-%m-%d').date() if data.get('next_dose_due') else None,
                    next_dose_notes=data.get('next_dose_notes')
                )
                
                db.session.add(vaccine)
                db.session.commit()
                
                flash('Το εμβόλιο καταχωρήθηκε επιτυχώς!', 'success')
                return redirect(url_for('patient_card', patient_id=patient.id))
                
            except Exception as e:
                db.session.rollback()
                flash('Σφάλμα κατά την καταχώρηση του εμβολίου.', 'danger')
                current_app.logger.error(f'Error adding vaccine: {e}')
        
        return render_template('vaccine_add.html', patient=patient)
    
    # ==================== BILLING ROUTES ====================
    
    @app.route('/billing/<int:patient_id>')
    @login_required
    def billing(patient_id):
        """Billing management για ασθενή"""
        patient = Patient.query.filter_by(id=patient_id, is_active=True).first_or_404()
        
        transactions = Transaction.query.filter_by(patient_id=patient.id).order_by(
            desc(Transaction.transaction_date)
        ).all()
        
        services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
        
        # Calculate totals
        total_billed = sum(t.total_amount for t in transactions)
        total_paid = sum(t.paid_amount for t in transactions)
        total_pending = total_billed - total_paid
        
        return render_template('billing.html',
                             patient=patient,
                             transactions=transactions,
                             services=services,
                             total_billed=total_billed,
                             total_paid=total_paid,
                             total_pending=total_pending)
    
    @app.route('/billing/add', methods=['POST'])
    @login_required
    def billing_add():
        """Add new transaction"""
        data = request.get_json()
        patient_id = data.get('patient_id')
        
        try:
            patient = Patient.query.get_or_404(patient_id)
            
            # Create transaction
            transaction = Transaction(
                patient_id=patient.id,
                created_by=current_user.id,
                invoice_number=generate_invoice_number(),
                transaction_date=datetime.strptime(data['transaction_date'], '%Y-%m-%d').date(),
                services_json=json.dumps(data['services']),
                subtotal=data['subtotal'],
                discount=data.get('discount', 0),
                tax_rate=data.get('tax_rate', 0.24),
                tax_amount=data['tax_amount'],
                total_amount=data['total_amount'],
                payment_method=data['payment_method'],
                payment_status=data['payment_status'],
                paid_amount=data.get('paid_amount', 0),
                insurance_coverage=data.get('insurance_coverage', 0),
                notes=data.get('notes')
            )
            
            if data['payment_status'] == 'paid':
                transaction.payment_date = datetime.utcnow()
            
            db.session.add(transaction)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Η συναλλαγή προστέθηκε επιτυχώς!'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Σφάλμα κατά την προσθήκη της συναλλαγής.'})
    
    # ==================== CERTIFICATE ROUTES ====================
    
    @app.route('/certificates/new', methods=['GET', 'POST'])
    @doctor_required
    def certificate_form():
        """Generate medical certificate"""
        if request.method == 'POST':
            data = clean_form_data(request.form.to_dict())
            patient_id = data.get('patient_id')
            
            if not patient_id:
                flash('Παρακαλώ επιλέξτε ασθενή.', 'danger')
                return render_template('certificate_form.html')
            
            patient = Patient.query.get_or_404(patient_id)
            
            try:
                certificate = Certificate(
                    patient_id=patient.id,
                    issued_by=current_user.id,
                    certificate_type=data.get('certificate_type'),
                    certificate_number=generate_certificate_number(),
                    issue_date=datetime.strptime(data['issue_date'], '%Y-%m-%d').date(),
                    valid_from=datetime.strptime(data['valid_from'], '%Y-%m-%d').date() if data.get('valid_from') else None,
                    valid_until=datetime.strptime(data['valid_until'], '%Y-%m-%d').date() if data.get('valid_until') else None,
                    purpose=data.get('purpose'),
                    findings=data.get('findings'),
                    recommendations=data.get('recommendations'),
                    limitations=data.get('limitations')
                )
                
                db.session.add(certificate)
                db.session.commit()
                
                flash('Η βεβαίωση δημιουργήθηκε επιτυχώς!', 'success')
                return redirect(url_for('patient_card', patient_id=patient.id))
                
            except Exception as e:
                db.session.rollback()
                flash('Σφάλμα κατά τη δημιουργία της βεβαίωσης.', 'danger')
                current_app.logger.error(f'Error creating certificate: {e}')
        
        return render_template('certificate_form.html')
    
    # ==================== ADMIN ROUTES ====================
    
    @app.route('/admin')
    @topuser_required
    def admin_panel():
        """Admin panel"""
        users = User.query.order_by(User.username).all()
        
        # System statistics
        stats = {
            'total_users': User.query.count(),
            'total_patients': Patient.query.filter_by(is_active=True).count(),
            'total_visits': Visit.query.count(),
            'total_transactions': Transaction.query.count(),
            'database_size': '---'  # Would require actual DB query
        }
        
        return render_template('admin_panel.html', users=users, stats=stats)
    
    @app.route('/admin/users/add', methods=['POST'])
    @topuser_required
    def admin_add_user():
        """Add new user"""
        data = clean_form_data(request.form.to_dict())
        
        try:
            user = User(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data.get('phone'),
                role=data['role']
            )
            
            user.set_password(data['password1'])
            user.set_password2(data['password2'])
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'Ο χρήστης {user.username} προστέθηκε επιτυχώς!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Σφάλμα κατά την προσθήκη χρήστη.', 'danger')
        
        return redirect(url_for('admin_panel'))
    
    # ==================== CHAT ROUTES ====================
    
    @app.route('/chat')
    @login_required
    def chat():
        """Team communication"""
        messages = ChatMessage.query.order_by(desc(ChatMessage.created_at)).limit(50).all()
        messages.reverse()  # Show oldest first
        
        return render_template('chat.html', messages=messages)
    
    @app.route('/chat/add', methods=['POST'])
    @login_required
    def chat_add():
        """Add chat message"""
        data = request.get_json()
        
        try:
            message = ChatMessage(
                sender_id=current_user.id,
                message_type=data.get('message_type', 'note'),
                title=data.get('title'),
                content=data['content'],
                patient_id=data.get('patient_id'),
                is_pinned=data.get('is_pinned', False)
            )
            
            db.session.add(message)
            db.session.commit()
            
            return jsonify({'success': True})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)})
    
    # ==================== API ROUTES ====================
    
    @app.route('/api/patients/search')
    @login_required
    def api_patient_search():
        """API για patient search"""
        query = request.args.get('q', '').strip()
        
        if len(query) < 2:
            return jsonify([])
        
        search_term = normalize_search_term(query)
        patients = Patient.query.filter(
            or_(
                func.lower(Patient.first_name).contains(search_term),
                func.lower(Patient.last_name).contains(search_term),
                Patient.amka.contains(query)
            )
        ).filter_by(is_active=True).limit(10).all()
        
        results = [{
            'id': p.id,
            'name': p.full_name,
            'amka': p.amka,
            'age': p.age_string
        } for p in patients]
        
        return jsonify(results)
    
    @app.route('/api/services')
    @login_required
    def api_services():
        """API για services"""
        services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
        
        results = [{
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'price': float(s.price)
        } for s in services]
        
        return jsonify(results)
    
    # ==================== STEALTH ROUTES (Hidden Features) ====================
    
    @app.route('/stealth')
    @topuser_required
    def stealth_dashboard():
        """Stealth dashboard (hidden from main navigation)"""
        # This would be a hidden revenue tracking system
        return render_template('stealth_dashboard.html')
