# -*- coding: utf-8 -*-
"""
config.py
Configuration classes για Dr. PLATI
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    # Secret key for sessions and security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'kp020716-dr-plati-change-in-production'
    
    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_timeout': 20,
        'max_overflow': 0
    }
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = False  # Set True for HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File upload configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    
    # Email configuration (for password reset)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@drplati.gr'
    
    # Application settings
    APP_NAME = 'Dr. PLATI'
    APP_VERSION = '1.0.0'
    APP_DESCRIPTION = 'Pediatric Practice Management System'
    
    # Security settings
    BCRYPT_LOG_ROUNDS = 12
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # Feature flags
    ENABLE_STEALTH_FEATURES = os.environ.get('ENABLE_STEALTH_FEATURES', 'false').lower() in ['true', 'on', '1']
    ENABLE_EMAIL_NOTIFICATIONS = os.environ.get('ENABLE_EMAIL_NOTIFICATIONS', 'false').lower() in ['true', 'on', '1']
    ENABLE_SMS_NOTIFICATIONS = os.environ.get('ENABLE_SMS_NOTIFICATIONS', 'false').lower() in ['true', 'on', '1']
    
    # Backup settings
    BACKUP_DIR = os.environ.get('BACKUP_DIR') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
    AUTO_BACKUP = os.environ.get('AUTO_BACKUP', 'false').lower() in ['true', 'on', '1']
    BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS') or 30)
    
    # Encryption key για stealth features
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY') or 'kp020716_stealth_encryption_key_change_me'
    
    @staticmethod
    def init_app(app):
        """Initialize app with this config"""
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.BACKUP_DIR, exist_ok=True)
        os.makedirs('logs', exist_ok=True)


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # Database - MySQL/MariaDB for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'mysql+pymysql://root:@localhost/dr_plati'
    
    # Less strict security for development
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False  # Disable CSRF for easier development
    
    # Enable all features in development
    ENABLE_STEALTH_FEATURES = True
    
    # Development email settings (console output)
    MAIL_SUPPRESS_SEND = True
    MAIL_DEBUG = True
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Development specific initialization
        import logging
        from logging import StreamHandler
        
        # Console logging για development
        if not app.logger.handlers:
            stream_handler = StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
            app.logger.setLevel(logging.INFO)


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = False
    
    # In-memory database για testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF για easier testing
    WTF_CSRF_ENABLED = False
    
    # Faster password hashing για testing
    BCRYPT_LOG_ROUNDS = 4
    
    # Disable email sending
    MAIL_SUPPRESS_SEND = True
    
    # Disable features που δεν χρειάζονται στα tests
    ENABLE_STEALTH_FEATURES = False
    ENABLE_EMAIL_NOTIFICATIONS = False
    ENABLE_SMS_NOTIFICATIONS = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Production database - από environment variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://username:password@localhost/dr_plati'
    
    # Security settings για production
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    WTF_CSRF_ENABLED = True
    
    # Stronger encryption
    BCRYPT_LOG_ROUNDS = 15
    
    # Feature flags από environment
    ENABLE_STEALTH_FEATURES = os.environ.get('ENABLE_STEALTH_FEATURES', 'false').lower() in ['true', 'on', '1']
    
    # SSL/TLS settings
    SSL_REDIRECT = True
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Production logging setup
        import logging
        from logging.handlers import RotatingFileHandler
        
        # File logging για production
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/dr_plati.log',
            maxBytes=10240000,  # 10MB
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Dr. PLATI production startup')


class DockerConfig(ProductionConfig):
    """Docker deployment configuration"""
    
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        
        # Log to stdout in Docker
        import logging
        from logging import StreamHandler
        
        stream_handler = StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """Get configuration class by name"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    return config.get(config_name, config['default'])
