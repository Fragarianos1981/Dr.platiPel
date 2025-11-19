#!/bin/bash

# Dr. PLATI Deployment Script
# Αυτόματη εγκατάσταση και deployment σε production

set -e  # Exit on any error

# Colors για output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="drplati"
APP_USER="www-data"
APP_DIR="/opt/drplati"
SERVICE_FILE="/etc/systemd/system/drplati.service"
NGINX_SITE="/etc/nginx/sites-available/drplati"
DOMAIN="${1:-localhost}"

echo -e "${BLUE}🏥 Dr. PLATI Deployment Script${NC}"
echo -e "${BLUE}================================${NC}"

# Function για logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root (use sudo)"
fi

# System update
log "Updating system packages..."
apt-get update && apt-get upgrade -y

# Install dependencies
log "Installing system dependencies..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    mysql-server \
    redis-server \
    supervisor \
    certbot \
    python3-certbot-nginx \
    fail2ban \
    ufw

# Create application user if not exists
if ! id "$APP_USER" &>/dev/null; then
    log "Creating application user: $APP_USER"
    useradd -r -s /bin/false $APP_USER
fi

# Create application directory
log "Setting up application directory: $APP_DIR"
mkdir -p $APP_DIR
mkdir -p $APP_DIR/{logs,backups,ssl}
chown -R $APP_USER:$APP_USER $APP_DIR

# Copy application files
log "Copying application files..."
cp -r * $APP_DIR/
chown -R $APP_USER:$APP_USER $APP_DIR

# Setup Python virtual environment
log "Setting up Python virtual environment..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn supervisor

# Setup database
log "Configuring MySQL database..."
mysql -e "CREATE DATABASE IF NOT EXISTS drplati CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER IF NOT EXISTS 'drplati'@'localhost' IDENTIFIED BY 'DrPlati2024!';"
mysql -e "GRANT ALL PRIVILEGES ON drplati.* TO 'drplati'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

# Setup environment file
log "Creating environment configuration..."
cat > $APP_DIR/.env << EOF
# Dr. PLATI Production Environment
FLASK_ENV=production
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DATABASE_URL=mysql+pymysql://drplati:DrPlati2024!@localhost/drplati

# Security
WTF_CSRF_ENABLED=true
SESSION_COOKIE_SECURE=true

# Mail configuration (update with your settings)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Clinic settings
CLINIC_NAME=Dr. PLATI
CLINIC_ADDRESS=Your Clinic Address
CLINIC_PHONE=+30 210 1234567
CLINIC_EMAIL=info@drplati.gr

# Feature flags
ENABLE_BACKUP=true
ENABLE_AUDIT_LOG=true
ENABLE_REGISTRATION=false
EOF

chown $APP_USER:$APP_USER $APP_DIR/.env
chmod 600 $APP_DIR/.env

# Initialize database
log "Initializing database..."
sudo -u $APP_USER bash -c "cd $APP_DIR && source venv/bin/activate && python init_db.py"

# Create systemd service
log "Creating systemd service..."
cat > $SERVICE_FILE << EOF
[Unit]
Description=Dr. PLATI Gunicorn instance
After=network.target mysql.service

[Service]
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --timeout 120 app:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Start and enable service
systemctl daemon-reload
systemctl enable drplati
systemctl start drplati

# Configure Nginx
log "Configuring Nginx..."
cat > $NGINX_SITE << EOF
server {
    listen 80;
    server_name $DOMAIN;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Static files
    location /static/ {
        alias $APP_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable Nginx site
ln -sf $NGINX_SITE /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Configure firewall
log "Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'
ufw allow mysql

# Configure fail2ban
log "Setting up fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Setup SSL (if domain is not localhost)
if [ "$DOMAIN" != "localhost" ]; then
    log "Setting up SSL certificate with Let's Encrypt..."
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
fi

# Setup backups
log "Setting up automated backups..."
mkdir -p /opt/backups
cat > /etc/cron.daily/drplati-backup << 'EOF'
#!/bin/bash
# Daily backup script for Dr. PLATI

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="drplati_backup_$DATE.sql"

# Create backup
mysqldump -u root drplati > "$BACKUP_DIR/$BACKUP_FILE"
gzip "$BACKUP_DIR/$BACKUP_FILE"

# Keep only last 30 days
find $BACKUP_DIR -name "drplati_backup_*.sql.gz" -mtime +30 -delete

# Log backup
logger "Dr. PLATI backup completed: $BACKUP_FILE.gz"
EOF

chmod +x /etc/cron.daily/drplati-backup

# Create admin user
log "Creating initial admin user..."
sudo -u $APP_USER bash -c "cd $APP_DIR && source venv/bin/activate && python run.py admin"

# Final status check
log "Checking services status..."
systemctl is-active --quiet drplati && echo "✅ Dr. PLATI service: Running" || echo "❌ Dr. PLATI service: Failed"
systemctl is-active --quiet nginx && echo "✅ Nginx: Running" || echo "❌ Nginx: Failed"
systemctl is-active --quiet mysql && echo "✅ MySQL: Running" || echo "❌ MySQL: Failed"
systemctl is-active --quiet redis && echo "✅ Redis: Running" || echo "❌ Redis: Failed"

echo -e "${GREEN}"
echo "========================================="
echo "🎉 Dr. PLATI DEPLOYMENT COMPLETED! 🎉"
echo "========================================="
echo -e "${NC}"
echo "🌐 Website: http://$DOMAIN"
if [ "$DOMAIN" != "localhost" ]; then
    echo "🔒 HTTPS: https://$DOMAIN"
fi
echo "👤 Admin login:"
echo "   Username: admin"
echo "   Password1: admin123"  
echo "   Password2: kp020716"
echo ""
echo "📁 Application directory: $APP_DIR"
echo "📊 Logs: $APP_DIR/logs/"
echo "💾 Backups: /opt/backups/"
echo ""
echo "🔧 Useful commands:"
echo "   sudo systemctl status drplati    # Check service status"
echo "   sudo systemctl restart drplati   # Restart service"
echo "   sudo tail -f $APP_DIR/logs/app.log  # View logs"
echo ""
warning "Remember to update the email settings in $APP_DIR/.env"
warning "Change default passwords before production use!"
