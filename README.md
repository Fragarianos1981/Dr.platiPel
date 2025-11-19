# 🏥 Dr. PLATI - Παιδιατρικό Σύστημα Διαχείρισης

**Production-Ready Pediatric Practice Management System**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-3.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)](README.md)

Πλήρες σύστημα διαχείρισης παιδιατρικού ιατρείου με υποστήριξη Ελληνικών και AMKA validation.

## 🎯 **ΧΑΡΑΚΤΗΡΙΣΤΙΚΑ**

### 🔐 **Ασφάλεια & Πρόσβαση**
- **Dual Password Authentication** - Προσωπικός κωδικός + κοινός κωδικός
- **4-επίπεδη πρόσβαση** - TopUser, Admin, Doctor, Secretary  
- **AMKA Validation** - Επαλήθευση Ελληνικών ΑΜΚΑ
- **Session Management** - Ασφαλείς sessions με auto-logout

### 🏥 **Ιατρικές Λειτουργίες**
- **Διαχείριση Ασθενών** - Πλήρη στοιχεία με ιστορικό
- **Επισκέψεις** - Καταγραφή και παρακολούθηση
- **Εμβολιασμοί** - Ελληνικό εμβολιαστικό πρόγραμμα
- **Ιατρικές Βεβαιώσεις** - 6 τύποι βεβαιώσεων
- **Αύξηση & Ανάπτυξη** - Διαγράμματα BMI και ανάπτυξης

### 💰 **Οικονομική Διαχείριση**
- **Τιμολόγηση** - Επαγγελματικά τιμολόγια με ΦΠΑ
- **Πολλαπλές Πληρωμές** - Μετρητά, κάρτα, έμβασμα, ασφάλεια
- **Φοροτεχνική Συμβατότητα** - Ελληνική νομοθεσία
- **Αναφορές** - Οικονομικές στατιστικές

### 🎨 **Διεπαφή Χρήστη**
- **Pink Pediatric Theme** - Παιδικό φιλικό design
- **Bootstrap 5** - Responsive για mobile
- **Ελληνική Γλώσσα** - Πλήρη UTF-8 υποστήριξη
- **Animated UI** - Smooth transitions

## 📊 **PROJECT STATISTICS**

| Μέτρο | Αξία | Περιγραφή |
|-------|------|-----------|
| **Συνολικά Αρχεία** | 76 | Πλήρης project δομή |
| **Γραμμές Κώδικα** | 8,643+ | Production-quality codebase |
| **Python Files** | 30 | Backend, services, models |
| **HTML Templates** | 24 | Πλήρες frontend coverage |
| **Features** | 20+ | Ολοκληρωμένη λειτουργικότητα |

## 🚀 **ΓΡΗΓΟΡΟΣ ΞΕΚΙΝΗΜΑ**

### **🪟 Windows 10 + XAMPP (ΠΡΟΤΕΙΝΟΜΕΝΟ)**

```cmd
REM ΠΡΟΑΠΑΙΤΟΥΜΕΝΑ:
REM 1. Κατεβάστε XAMPP: https://www.apachefriends.org/download.html
REM 2. Εγκατάσταση Python 3.11+: https://www.python.org/downloads/ 
REM 3. Ξεκινήστε Apache + MySQL στο XAMPP Control Panel
REM 4. Δημιουργήστε database 'drplati' στο phpMyAdmin

REM ΕΓΚΑΤΑΣΤΑΣΗ:
cd C:\
unzip dr_plati_COMPLETE_FINAL_PRODUCTION.zip
cd dr_plati_complete

REM Αυτόματη εγκατάσταση (διπλό κλικ):
install_windows.bat

REM Ή χειροκίνητα:
python -m venv venv
venv\Scripts\activate
pip install -r requirements_windows.txt
copy .env.example .env
python init_db.py
python run.py
```

**🌐 Πρόσβαση:** `http://localhost:5000` | **👤 Login:** admin/admin123/kp020716

⚠️ **ΑΝΤΙΜΕΤΩΠΙΣΗ ΠΡΟΒΛΗΜΑΤΩΝ:** Δείτε το [TROUBLESHOOTING_WINDOWS.md](TROUBLESHOOTING_WINDOWS.md)

### **🐧 Linux/Mac Development**

```bash
# 1. Download & Extract
unzip dr_plati_COMPLETE_FINAL_PRODUCTION.zip
cd dr_plati_complete/

# 2. Setup Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configuration  
cp .env.example .env
# Edit .env with your database settings

# 4. Initialize Database
python init_db.py

# 5. Start Application
python run.py
```

### **Πρώτη Πρόσβαση**
- **URL**: `http://localhost:5000`
- **Admin**: Δημιουργείται αυτόματα
- **Κοινός κωδικός**: `kp020716` (για όλους τους χρήστες)

## 🐳 **DOCKER DEPLOYMENT**

### **Development με Docker**
```bash
docker-compose up -d
```

### **Production με Docker**
```bash
# Update docker-compose.yml with your settings
docker-compose -f docker-compose.yml up -d
```

**Services που ξεκινούν:**
- Web Application (Flask + Gunicorn)
- MySQL Database με Greek collation
- Redis για caching
- Nginx reverse proxy με SSL

## 🖥️ **PRODUCTION DEPLOYMENT**

### **Αυτόματη Εγκατάσταση Ubuntu**
```bash
# Για Ubuntu 20.04+ servers
sudo ./deploy.sh your-domain.com

# Το script θα εγκαταστήσει:
# ✅ System dependencies (Python, MySQL, Nginx, Redis)
# ✅ Application με virtual environment
# ✅ Database setup με Greek UTF-8
# ✅ Systemd service
# ✅ Nginx configuration
# ✅ SSL certificates (Let's Encrypt)
# ✅ Firewall configuration
# ✅ Automated backups
# ✅ Security hardening
```

## ⚙️ **ΔΙΑΜΟΡΦΩΣΗ**

### **Αρχείο .env**
```bash
# Database
DATABASE_URL=mysql+pymysql://user:pass@localhost/drplati

# Security
SECRET_KEY=your-super-secret-key-here
WTF_CSRF_ENABLED=true

# Email (για password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Clinic Settings
CLINIC_NAME=Dr. PLATI
CLINIC_ADDRESS=Your Address
CLINIC_PHONE=+30 210 1234567
CLINIC_EMAIL=info@drplati.gr
```

## 📁 **ΔΟΜΗ PROJECT**

```
dr_plati_complete/                    # Root directory (76 files)
├── 🐍 BACKEND (30 files)
│   ├── app.py                       # Main Flask application
│   ├── run.py                       # Entry point με admin creation
│   ├── config.py                    # Configuration
│   ├── models/                      # Data models (6 files)
│   ├── services/                    # Business logic (6 files)
│   ├── routes/                      # URL routing (2 files)
│   └── utils/                       # Utilities (3 files)
├── 🌐 FRONTEND (24 files)
│   └── templates/                   # Jinja2 templates
│       ├── base.html               # Bootstrap 5 layout
│       ├── dashboard.html          # Main dashboard
│       ├── patient_*.html          # Patient management (3)
│       ├── visit_*.html            # Visit management (4)
│       ├── vaccine_*.html          # Vaccination (2)
│       ├── certificate_*.html      # Certificates (2)
│       └── error pages             # 403, 404, 500
├── 🎨 ASSETS (3 files)
│   └── static/
│       ├── css/style.css          # Pink pediatric theme
│       └── js/app.js              # Client-side JS
├── ⚙️ CONFIG (8 files)
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                # Container config
│   ├── docker-compose.yml        # Multi-service setup
│   ├── nginx.conf                # Production web server
│   └── deploy.sh                 # Deployment script
├── 📚 DOCS (5 files)
│   ├── README.md                 # This file
│   ├── CHANGELOG.md              # Version history
│   └── Various README files
└── 📂 DIRECTORIES
    ├── logs/                     # Application logs
    ├── static/uploads/           # User uploads
    ├── db/                       # Database scripts
    └── ssl/                      # SSL certificates
```

## 👥 **ΧΡΗΣΤΕΣ & ΡΟΛΟΙ**

| Ρόλος | Δικαιώματα | Περιγραφή |
|-------|------------|-----------|
| **TopUser** | Πλήρη πρόσβαση | System administration |
| **Admin** | Όλες οι λειτουργίες εκτός διαγραφής | Practice management |
| **Doctor** | Ιατρικές λειτουργίες | Medical operations |
| **Secretary** | Διοικητικές λειτουργίες | Administrative tasks |

### **Αρχικός Admin**
- **Username**: `admin`
- **Password1**: `admin123` (προσωπικός)
- **Password2**: `kp020716` (κοινός)

⚠️ **ΣΗΜΑΝΤΙΚΟ**: Αλλάξτε τους προεπιλεγμένους κωδικούς σε production!

## 📈 **FEATURES & MODULES**

### **✅ Διαχείριση Ασθενών**
- Complete patient profiles με family info
- AMKA validation & Greek insurance
- Medical history & allergy tracking
- Photo upload & document management
- Age groups & growth tracking

### **✅ Επισκέψεις & Ιατρικό Ιστορικό**
- Detailed visit records
- Chief complaints & diagnoses
- Treatment plans & prescriptions
- Follow-up scheduling
- Visit statistics & trends

### **✅ Εμβολιαστικό Πρόγραμμα**
- Greek vaccination schedule
- Automatic due date calculations
- Vaccine inventory management
- Immunization certificates
- Coverage statistics

### **✅ Ιατρικές Βεβαιώσεις**
- 6 certificate types: Υγείας, Αθλητισμού, Κατασκήνωσης, Ταξιδιού, Απουσίας, Γενική
- Professional PDF generation
- Digital signatures ready
- Certificate tracking & renewal
- Batch printing capabilities

### **✅ Οικονομικό Σύστημα**
- Professional invoicing με Greek VAT
- Multiple payment methods
- Insurance claim processing
- Revenue analytics & reports
- Tax compliance features

### **✅ Reports & Analytics**
- Patient demographics
- Vaccination coverage statistics
- Revenue reports
- Growth charts
- Custom date ranges

### **✅ System Administration**
- User management με role-based access
- System settings configuration
- Automated backups
- Audit trails & logging
- Health monitoring

## 🔒 **ΑΣΦΑΛΕΙΑ**

### **Implemented Security Measures**
- ✅ **Dual Password Authentication**
- ✅ **CSRF Protection**
- ✅ **SQL Injection Prevention**
- ✅ **XSS Protection**
- ✅ **Secure Session Management**
- ✅ **Input Validation & Sanitization**
- ✅ **Rate Limiting**
- ✅ **SSL/TLS Support**
- ✅ **File Upload Security**
- ✅ **Audit Logging**

## 🔧 **ΧΡΗΣΙΜΕΣ ΕΝΤΟΛΕΣ**

### **Development**
```bash
python run.py                      # Development server
python run.py dev                  # Same as above
python run.py init                 # Initialize database
python run.py admin                # Create admin user
```

### **Production**
```bash
python run.py prod                 # Production με Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

### **System Management**
```bash
# Systemd service (μετά το deploy.sh)
sudo systemctl status drplati     # Check status
sudo systemctl restart drplati    # Restart service

# Logs
tail -f logs/app.log              # Application logs
sudo journalctl -u drplati -f     # Service logs
```

## 💾 **BACKUP & RECOVERY**

### **Automated Backups**
```bash
# Daily backup script (included)
/etc/cron.daily/drplati-backup

# Manual backup
mysqldump -u root drplati > backup.sql
gzip backup.sql
```

## 🐛 **TROUBLESHOOTING**

### **Common Issues**

**Database Connection Error**
```bash
# Check MySQL service
sudo systemctl status mysql

# Test connection
mysql -u drplati -p drplati
```

**Service Won't Start**
```bash
# Check logs
sudo journalctl -u drplati -n 50

# Check configuration
python -c "from app import app; print('Config OK')"
```

## 📧 **CONTACT & SUPPORT**

**Dr. PLATI Development Team**
- 🌐 Project: [GitHub Repository](https://github.com/yourusername/dr_plati)
- 📧 Email: support@drplati.gr
- 📚 Documentation: [Wiki](wiki/)
- 🐛 Issues: [GitHub Issues](issues/)

---

## 🏥 **Dr. PLATI - ΠΛΗΡΕΣ ΠΑΙΔΙΑΤΡΙΚΟ ΣΥΣΤΗΜΑ**

**Production Ready • Greek Healthcare Standards • AMKA Compliant**

*"Από την πρώτη επίσκεψη στην ψηφιακή διαχείριση - μηδέν συμβιβασμός."*

[![Made with ❤️ in Greece](https://img.shields.io/badge/Made%20with%20❤️-in%20Greece-blue.svg)](README.md)
