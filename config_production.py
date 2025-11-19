"""
Production Configuration για Dr. PLATI
Ρυθμίσεις για production environment
"""

import os
from datetime import timedelta


class ProductionConfig:
    """Production configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-production-key-here'
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://drplati:password@localhost/drplati'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # Security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Mail settings (for password reset)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    
    # Cache (Redis)
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
    RATELIMIT_DEFAULT = "100 per hour"
    
    # SSL/TLS
    PREFERRED_URL_SCHEME = 'https'
    
    # Dr. PLATI specific settings
    CLINIC_NAME = os.environ.get('CLINIC_NAME', 'Dr. PLATI')
    CLINIC_ADDRESS = os.environ.get('CLINIC_ADDRESS', '')
    CLINIC_PHONE = os.environ.get('CLINIC_PHONE', '')
    CLINIC_EMAIL = os.environ.get('CLINIC_EMAIL', '')
    
    # Backup settings
    BACKUP_ENABLED = os.environ.get('BACKUP_ENABLED', 'true').lower() in ['true', '1', 'on']
    BACKUP_FREQUENCY = os.environ.get('BACKUP_FREQUENCY', 'daily')  # daily, weekly, monthly
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', '30'))
    BACKUP_STORAGE_PATH = os.environ.get('BACKUP_STORAGE_PATH', '/backups')
    
    # Security settings
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', '5'))
    LOCKOUT_DURATION = int(os.environ.get('LOCKOUT_DURATION', '15'))  # minutes
    PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', '6'))
    
    # Feature flags
    ENABLE_REGISTRATION = os.environ.get('ENABLE_REGISTRATION', 'false').lower() in ['true', '1', 'on']
    ENABLE_PASSWORD_RESET = os.environ.get('ENABLE_PASSWORD_RESET', 'true').lower() in ['true', '1', 'on']
    ENABLE_AUDIT_LOG = os.environ.get('ENABLE_AUDIT_LOG', 'true').lower() in ['true', '1', 'on']
    
    # Monitoring
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    HEALTH_CHECK_ENABLED = True
    
    @staticmethod
    def init_app(app):
        """Initialize production-specific settings"""
        
        # Setup logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        file_handler = RotatingFileHandler(
            ProductionConfig.LOG_FILE,
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(getattr(logging, ProductionConfig.LOG_LEVEL))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, ProductionConfig.LOG_LEVEL))
        app.logger.info('Dr. PLATI production startup')
        
        # Setup Sentry for error tracking
        if ProductionConfig.SENTRY_DSN:
            try:
                import sentry_sdk
                from sentry_sdk.integrations.flask import FlaskIntegration
                
                sentry_sdk.init(
                    dsn=ProductionConfig.SENTRY_DSN,
                    integrations=[FlaskIntegration()],
                    traces_sample_rate=0.1
                )
            except ImportError:
                app.logger.warning('Sentry SDK not installed')
