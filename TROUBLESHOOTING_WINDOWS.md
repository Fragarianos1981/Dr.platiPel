# 🛠️ Dr. PLATI - Windows Troubleshooting Guide

**Λύσεις για συνήθη προβλήματα σε Windows 10 + XAMPP**

---

## ❌ **ΠΡΟΒΛΗΜΑ 1: "Failed to build pandas/numpy"**

**Σφάλμα:**
```
ERROR: Failed to build 'pandas' when installing build dependencies for pandas
```

**💡 ΛΥΣΗ:**
```cmd
# Χρησιμοποιήστε το Windows-compatible requirements
pip install -r requirements_windows.txt

# Ή εγκαταστήστε χειροκίνητα τα βασικά:
pip install Flask Flask-SQLAlchemy Flask-Login Flask-Mail Flask-WTF
pip install PyMySQL python-dotenv bcrypt reportlab requests
```

---

## ❌ **ΠΡΟΒΛΗΜΑ 2: "No module named 'MySQLdb'"**

**💡 ΛΥΣΗ:**
```cmd
# Εγκατάσταση PyMySQL
pip install PyMySQL

# Στο .env βεβαιωθείτε ότι έχετε:
DATABASE_URL=mysql+pymysql://root:@localhost:3306/drplati
```

---

## ❌ **ΠΡΟΒΛΗΜΑ 3: "Access denied for user 'root'@'localhost'"**

**💡 ΛΥΣΗ:**
```cmd
# 1. Ανοίξτε XAMPP Control Panel
# 2. Κάντε κλικ "Admin" δίπλα στο MySQL
# 3. Στο phpMyAdmin:
#    - Κλικ "User accounts" 
#    - Επεξεργασία του root user
#    - Βάλτε password ή αφήστε κενό

# 4. Ενημερώστε το .env:
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/drplati
```

---

## ❌ **ΠΡΟΒΛΗΜΑ 4: "Can't connect to MySQL server"**

**💡 ΛΥΣΗ:**
```cmd
# 1. Βεβαιωθείτε ότι το MySQL τρέχει στο XAMPP
# 2. Ελέγξτε την πόρτα (default: 3306)
# 3. Δοκιμάστε:
telnet localhost 3306

# Αν δεν λειτουργεί:
# - Επανεκκινήστε XAMPP
# - Ελέγξτε logs στο XAMPP/mysql/data/mysql_error.log
```

---

## ❌ **ΠΡΟΒΛΗΜΑ 5: "Permission denied" ή "Access denied"**

**💡 ΛΥΣΗ:**
```cmd
# 1. Εκτελέστε Command Prompt ΩΣ ADMINISTRATOR
# 2. Δώστε δικαιώματα στον φάκελο:
icacls C:\drplati /grant Everyone:F /T

# 3. Ή μετακινήστε τον φάκελο στο Desktop:
mkdir %USERPROFILE%\Desktop\drplati
xcopy C:\drplati\* %USERPROFILE%\Desktop\drplati\ /E /I
```

---

## ❌ **ΠΡΟΒΛΗΜΑ 6: "Port 5000 is already in use"**

**💡 ΛΥΣΗ:**
```cmd
# Βρείτε τι χρησιμοποιεί την πόρτα 5000:
netstat -ano | findstr :5000

# Σκοτώστε τη διαδικασία (αντικαταστήστε το PID):
taskkill /F /PID 1234

# Ή χρησιμοποιήστε άλλη πόρτα:
python run.py --port 5001
```

---

## ❌ **ΠΡΟΒΛΗΜΑ 7: "ModuleNotFoundError: No module named 'app'"**

**💡 ΛΥΣΗ:**
```cmd
# Βεβαιωθείτε ότι είστε στο σωστό φάκελο:
cd C:\drplati\dr_plati_complete

# Και ότι το virtual environment είναι ενεργό:
venv\Scripts\activate

# Ελέγξτε αν το app.py υπάρχει:
dir app.py
```

---

## ❌ **ΠΡΟΒΛΗΜΑ 8: "UnicodeDecodeError"**

**💡 ΛΥΣΗ:**
```cmd
# Ρυθμίστε το encoding στο Command Prompt:
chcp 65001

# Ή χρησιμοποιήστε PowerShell αντί για CMD:
# Κάντε δεξί κλικ στον φάκελο -> "Open PowerShell window here"
```

---

## ❌ **ΠΡΟΒΛΗΜΑ 9: "Database doesn't exist"**

**💡 ΛΥΣΗ:**
```cmd
# 1. Ανοίξτε phpMyAdmin: http://localhost/phpmyadmin
# 2. Κλικ "New" στα αριστερά
# 3. Database name: drplati
# 4. Collation: utf8mb4_unicode_ci
# 5. Κλικ "Create"

# Στη συνέχεια:
python init_db.py
```

---

## ❌ **ΠΡΟΒΛΗΜΑ 10: "Virtual environment not working"**

**💡 ΛΥΣΗ:**
```cmd
# Διαγράψτε και ξαναδημιουργήστε το venv:
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements_windows.txt
```

---

## 🔧 **ΓΕΝΙΚΕΣ ΣΥΜΒΟΥΛΕΣ ΑΝΤΙΜΕΤΩΠΙΣΗΣ**

### **1. Έλεγχος Κατάστασης XAMPP**
```cmd
# Ανοίξτε XAMPP Control Panel
# Βεβαιωθείτε ότι είναι πράσινα:
# ✅ Apache (Running)
# ✅ MySQL (Running)
```

### **2. Έλεγχος Database**
```
1. Ανοίξτε: http://localhost/phpmyadmin
2. Βεβαιωθείτε ότι η βάση 'drplati' υπάρχει
3. Ελέγξτε ότι έχει tables (users, patients, κτλ)
```

### **3. Έλεγχος Python Environment**
```cmd
# Ελέγξτε έκδοση Python:
python --version

# Ελέγξτε αν το venv είναι ενεργό:
where python
# Θα πρέπει να δείχνει: C:\drplati\...\venv\Scripts\python.exe

# Ελέγξτε εγκατεστημένα packages:
pip list
```

### **4. Έλεγχος Logs**
```cmd
# Δείτε τα logs της εφαρμογής:
type logs\app.log

# Δείτε MySQL errors:
type C:\xampp\mysql\data\mysql_error.log
```

---

## 🚨 **ΣΕ ΠΕΡΙΠΤΩΣΗ ΑΠΕΛΠΙΣΙΑΣ**

### **Πλήρης Επαναεγκατάσταση:**
```cmd
# 1. Σταματήστε το XAMPP
# 2. Backup της βάσης από phpMyAdmin (Export)
# 3. Διαγράψτε τον φάκελο C:\drplati
# 4. Αποσυμπιέστε ξανά το ZIP
# 5. Τρέξτε το install_windows.bat
# 6. Restore την βάση (Import)
```

### **Ελάχιστη Εγκατάσταση (Αν τίποτα δεν δουλεύει):**
```cmd
cd C:\drplati\dr_plati_complete
python -m venv minimal_venv
minimal_venv\Scripts\activate
pip install Flask==3.0.0
pip install Flask-SQLAlchemy==3.1.1
pip install PyMySQL==1.1.0
pip install python-dotenv==1.0.0
python app.py
```

---

## 📞 **ΥΠΟΣΤΗΡΙΞΗ**

### **Πριν ζητήσετε βοήθεια, συλλέξτε:**
```cmd
1. Έκδοση Python: python --version
2. Κατάσταση XAMPP: screenshot του Control Panel
3. Μήνυμα σφάλματος: copy-paste ολόκληρο το error
4. Περιεχόμενα .env: (χωρίς passwords)
5. Κατάσταση database: screenshot από phpMyAdmin

# Εκτελέστε και αυτό:
python -c "import sys; print('Python:', sys.version); import flask; print('Flask:', flask.__version__)"
```

---

## 🎯 **ΓΡΗΓΟΡΟΣ ΕΛΕΓΧΟΣ ΛΕΙΤΟΥΡΓΙΑΣ**

```cmd
# Τρέξτε αυτά τα tests:

# 1. Database connection:
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.engine.execute('SELECT 1'); print('✅ Database OK')"

# 2. Flask app:
python -c "from app import create_app; app = create_app(); print('✅ Flask OK')"

# 3. Dependencies:
python -c "import flask, flask_sqlalchemy, pymysql; print('✅ Dependencies OK')"
```

---

**🏥 Dr. PLATI - Windows Support Team**

*"Κανένα πρόβλημα δεν είναι μικρό όταν πρόκειται για την υγεία των παιδιών!"*
