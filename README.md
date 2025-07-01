# 💊 Pharmacy Management System

A complete web-based Pharmacy Management System built with **Flask** and **MySQL**, designed for managing drug inventory, employee access, sales tracking, and company details — with a clean, professional UI and role-based authentication.

---

## 🚀 Features

- 🔐 Role-Based Login System (Admin & Employee)
- 💊 Drug Management (Add, Edit, Delete, View)
- 💰 Sales Tracking Module
- 🧑‍💼 Employee Management
- 🏢 Company Records
- 📬 Inbox for Notifications & Messages
- 📊 Dashboard with Key Metrics
- 🧼 Professional UI with CSS
- 📅 Date Formatting & ₹ Currency Display
- 📧 Email Notifications on Login

---

## 🛠 Tech Stack

- **Frontend**: HTML5, CSS3
- **Backend**: Python (Flask)
- **Database**: MySQL
- **Authentication**: Session-based login
- **Extras**: SMTP Email Alerts, Clean Folder Structure

---

## 🗂 Project Structure

Pharmacy Management System/
│
├── static/
│   └── css/
│       └── style.css
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── drugs.html
│   ├── sales.html
│   ├── users.html
│   ├── companies.html
│   └── inbox.html
├── app.py
├── .gitignore
├── README.md
└── requirements.txt

---

## ✅ Getting Started

### 🔧 Prerequisites

- Python 3.x
- MySQL Server
- Git (optional but recommended)

### 🔌 Installation Steps

1. Clone the repository:

```bash
git clone https://github.com/navadeepburri/Pharmacy-Management-System.git
cd Pharmacy-Management-System
```

### ⚙️ Set Up Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate      # On Linux/macOS
venv\Scripts\activate         # On Windows
```

### 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

### 🔧 Configure MySQL Database

1. **Create a MySQL database** named `pharmacy_db` (or your preferred name).
2. **Update your database credentials** in `app.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_mysql_username',
    'password': 'your_mysql_password',
    'database': 'pharmacy_db'
}
```

3. **Import the schema** into your database using a tool like phpMyAdmin or MySQL CLI:

```sql
SOURCE path/to/schema.sql;
```

> 💡 If you don't have a schema.sql file, contact the project author or export from an existing database.

---

### ▶️ Run the Application

```bash
python app.py
```

The app will be running at [http://localhost:5000](http://localhost:5000)

---

## 🔐 Default Credentials

| Role     | Username             | Password  |
|----------|----------------------|-----------|
| Admin    | admin@pharma.com     | admin123  |
| Employee | employee@pharma.com  | emp123    |

> ⚠️ Change these credentials after first login for security.

---

## 📸 Screenshots

> Include screenshots of:
- Dashboard
- Drug Management Page
- Sales Page
- Login Page
- Inbox

(You can add them in a `/screenshots/` folder and reference them here.)

---

## 📬 Contact

For issues, suggestions, or contributions, reach out:

- **Author**: Navadeep Burri  
- **GitHub**: [@navadeepburri](https://github.com/navadeepburri)

---

## 📄 License

This project is licensed under the MIT License. See `LICENSE` for details.
