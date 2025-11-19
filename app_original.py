# -*- coding: utf-8 -*-
"""
app_original.py
Main Flask Application για Dr. PLATI - FIXED VERSION
Pediatric Practice Management System
"""

from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from extensions import db
import logging
import os
from datetime import timedelta

def create_app():
    """Application Factory Pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'kp020716-dr-plati-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'mysql+pymysql://root:@localhost/dr_plati')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Session Configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)
    app.config['SESSION_COOKIE_SECURE'] = False  # Set True for HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Initialize Extensions
    db.init_app(app)
    
    # Import models AFTER db initialization
    from models import User, Patient, Visit, Vaccine, Transaction, Certificate
    
    # Flask-Login Configuration
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Παρακαλώ συνδεθείτε για να συνεχίσετε.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Basic Routes - Integrated into app
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
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard"""
        # Basic statistics
        total_patients = Patient.query.filter_by(is_active=True).count()
        total_visits = Visit.query.count()
        total_vaccines = Vaccine.query.count()
        
        # Recent visits
        recent_visits = Visit.query.order_by(Visit.created_at.desc()).limit(5).all()
        
        stats = {
            'total_patients': total_patients,
            'total_visits': total_visits,
            'total_vaccines': total_vaccines,
            'recent_visits': recent_visits
        }
        
        return render_template('dashboard.html', stats=stats)
    
    @app.route('/patients')
    @login_required
    def patients():
        """Patients list"""
        page = request.args.get('page', 1, type=int)
        patients = Patient.query.filter_by(is_active=True).paginate(
            page=page, per_page=20, error_out=False
        )
        return render_template('patient_list.html', patients=patients)
    
    @app.route('/patients/add', methods=['GET', 'POST'])
    @login_required
    def patient_add():
        """Add new patient"""
        if request.method == 'POST':
            try:
                patient = Patient(
                    amka=request.form.get('amka'),
                    first_name=request.form.get('first_name'),
                    last_name=request.form.get('last_name'),
                    date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date(),
                    gender=request.form.get('gender'),
                    phone=request.form.get('phone'),
                    created_by=current_user.id
                )
                db.session.add(patient)
                db.session.commit()
                flash('Ο ασθενής προστέθηκε επιτυχώς!', 'success')
                return redirect(url_for('patients'))
            except Exception as e:
                db.session.rollback()
                flash('Σφάλμα προσθήκης ασθενή', 'danger')
        
        return render_template('patient_add.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout"""
        user_name = current_user.full_name
        logout_user()
        flash(f'Αντίο {user_name}! Αποσυνδεθήκατε επιτυχώς.', 'info')
        return redirect(url_for('login'))
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        try:
            db.session.execute('SELECT 1')
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0',
                'database': 'connected'
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    
    # Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    # Context Processors για templates
    @app.context_processor
    def inject_global_vars():
        return {
            'app_name': 'Dr. PLATI',
            'app_version': '1.0.0'
        }
    
    # Before Request Handlers
    @app.before_request
    def before_request():
        """Εκτελείται πριν από κάθε request"""
        session.permanent = True
        
        # Log user activity (excluding static files)
        if not request.endpoint or not request.endpoint.startswith('static'):
            if current_user.is_authenticated:
                app.logger.info(f'User {current_user.username} accessed {request.endpoint}')
    
    # Logging Configuration
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/dr_plati.log', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Dr. PLATI startup')
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    from datetime import datetime
    with app.app_context():
        # Δημιουργία πινάκων αν δεν υπάρχουν
        db.create_all()
        print("🏥 Dr. PLATI - Pediatric Practice Management System")
        print("📱 Running on http://localhost:8080")
        print("🔐 Default login: admin / admin123 / kp020716")
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
        use_reloader=True
    )