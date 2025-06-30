from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Nandhu',
    'database': 'pharmacy',
    'auth_plugin': 'mysql_native_password',
    'port': 3306
}
# ✅ Email Configuration (paste here)
EMAIL_SENDER = 'nandhuburri2005@gmail.com'
EMAIL_PASSWORD = 'pxaecszitguoirvn'  # App password from Gmail
EMAIL_RECEIVER = 'nandhuburri2005@gmail.com'  # Your personal/admin email

# === 3. EMAIL FUNCTION ===
def send_login_notification(username, role):
    subject = f"[Login Alert] {username} ({role}) logged in"
    body = f"User '{username}' with role '{role}' logged into the Pharmacy Management System on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Login alert sent to admin.")
    except Exception as e:
        print("❌ Failed to send login email:", e)


def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        flash(f"Database connection error: {str(e)}", 'danger')
        return None

@app.template_filter('currency')
def format_currency(amount):
    try:
        return f"₹{float(amount or 0):,.2f}"
    except (ValueError, TypeError):
        return f"₹0.00"

@app.template_filter('dateformat')
def format_date(value, format='%Y-%m-%d'):
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                return value
    return value.strftime(format)

# ------------------ Login ------------------
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM employees WHERE username=%s AND PASSWORD=%s", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                session['loggedin'] = True
                session['user_id'] = user['ID']
                session['username'] = user['username']
                session['role'] = user['ROLE']

                send_login_notification(user['username'], user['ROLE'])


                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))  # Replace with your actual dashboard route
            else:
                flash('Invalid username or password', 'danger')

        except Error as e:
            flash(f"Database error: {str(e)}", 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
# ------------------ Dashboard ------------------
@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", "danger")
        return redirect(url_for('login'))

    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) as total_drugs FROM drugs")
        total_drugs = cursor.fetchone()['total_drugs']

        cursor.execute("SELECT IFNULL(SUM(amount), 0) as today_sales FROM sales WHERE DATE(date) = CURDATE()")
        today_sales = cursor.fetchone()['today_sales']

        cursor.execute("SELECT COUNT(*) as expired_products FROM drugs WHERE expiration_date < CURDATE()")
        expired_products = cursor.fetchone()['expired_products']

        cursor.execute("""
            SELECT d.name, s.quantity, s.amount, s.date 
            FROM sales s
            JOIN drugs d ON s.barcode = d.barcode
            ORDER BY s.date DESC
            LIMIT 5
        """)
        recent_sales = cursor.fetchall()

        return render_template(
            'dashboard.html',
            total_drugs=total_drugs,
            today_sales=today_sales,
            expired_products=expired_products,
            recent_sales=recent_sales,
            role=session.get('role'),
            username=session.get('username')
        )

    except Error as e:
        flash(f"Dashboard error: {str(e)}", 'danger')
        return redirect(url_for('login'))
    finally:
        conn.close()

# ------------------ Drugs ------------------
@app.route('/drugs')
def drugs():
    conn = get_db_connection()
    if not conn:
        return render_template('error.html')
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT d.*, c.name as company_name 
            FROM drugs d
            LEFT JOIN company c ON d.company_name = c.name
            ORDER BY d.name
        """)
        drugs_list = cursor.fetchall()
        #print(drugs_list)
        return render_template('drugs.html', drugs=drugs_list)
    except Error as e:
        flash(f"Failed to fetch drugs: {str(e)}", 'danger')
        return render_template('error.html')
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/drugs/add', methods=['GET', 'POST'])
def add_drug():
    fields = ['name', 'type', 'barcode', 'code', 'selling_price', 'cost_price', 'quantity', 'expiration_date', 'expiry', 'company_name', 'dose',  'production_date', 'place']
    conn = get_db_connection()
    if not conn:
        return render_template('error.html')
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT name FROM company")
        companies = [c['name'] for c in cursor.fetchall()]
        
        if request.method == 'POST':
            data = [request.form[field] for field in fields]
            cursor.execute("""
                INSERT INTO drugs (`name`, `type`, `barcode`, `code`, `selling_price`, `cost_price`, `quantity`, `expiration_date`, `expiry`, `company_name`, `dose`, `production_date`, `place`)
                VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, data)

            conn.commit()
            flash('Drug added successfully!', 'success')
            return redirect(url_for('drugs'))
            
        return render_template('add_drug.html', 
                             fields=fields, 
                             companies=companies,
                             submit_url=url_for('add_drug'))
    except Error as e:
        flash(f"Failed to add drug: {str(e)}", 'danger')
        return redirect(url_for('drugs'))
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/drugs/edit/<barcode>', methods=['GET', 'POST'])
def edit_drug(barcode):
    conn = get_db_connection()
    if not conn:
        return render_template('error.html')

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM drugs WHERE barcode = %s", (barcode,))
        drug = cursor.fetchone()

        if not drug:
            flash('Drug not found!', 'danger')
            return redirect(url_for('drugs'))

        # Format the date fields to 'YYYY-MM-DD' for the form
        if drug['EXPIRATION_DATE']:
            drug['EXPIRATION_DATE'] = drug['EXPIRATION_DATE'].strftime('%Y-%m-%d')
        if drug['PRODUCTION_DATE']:
            drug['PRODUCTION_DATE'] = drug['PRODUCTION_DATE'].strftime('%Y-%m-%d')

        cursor.execute("SELECT name FROM company")
        companies = [c['name'] for c in cursor.fetchall()]

        fields = ['name', 'type', 'barcode', 'code', 'selling_price', 'cost_price', 'quantity',
                  'expiration_date', 'production_date', 'place', 'company_name', 'dose']

        if request.method == 'POST':
            data = [request.form[field] for field in fields]
            cursor.execute("""
                UPDATE drugs 
                SET name=%s, type=%s, barcode=%s, code=%s, selling_price=%s, cost_price=%s, quantity=%s, expiration_date=%s, production_date=%s, place=%s, company_name=%s, dose=%s
                WHERE barcode=%s
            """, (*data, barcode))
            conn.commit()
            flash('Drug updated successfully!', 'success')
            return redirect(url_for('drugs'))

        return render_template('edit_drug.html',
                               drug=drug,
                               fields=fields,
                               companies=companies,
                               submit_url=url_for('edit_drug', barcode=barcode))
    except Error as e:
        flash(f"Failed to edit drug: {str(e)}", 'danger')
        return redirect(url_for('drugs'))
    finally:
        if conn and conn.is_connected():
            conn.close()



@app.route('/drugs/delete/<barcode>', methods=['GET', 'POST'])
def delete_drug(barcode):
    conn = get_db_connection()
    if not conn:
        return render_template('error.html')
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM drugs WHERE barcode = %s", (barcode,))
        drug = cursor.fetchone()
        
        if not drug:
            flash('Drug not found!', 'danger')
            return redirect(url_for('drugs'))
            
        if request.method == 'POST':
            cursor.execute("DELETE FROM drugs WHERE barcode = %s", (barcode,))
            conn.commit()
            flash('Drug deleted successfully!', 'success')
            return redirect(url_for('drugs'))
            
        return render_template('delete_drug.html', 
                             drug=drug,
                             cancel_url=url_for('drugs'))
    except Error as e:
        flash(f"Failed to delete drug: {str(e)}", 'danger')
        return redirect(url_for('drugs'))
    finally:
        if conn and conn.is_connected():
            conn.close()

# ------------------ Sales ------------------

@app.route('/sales')
def sales():
    conn = get_db_connection()
    if not conn:
        return render_template('error.html')

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.barcode, s.name, s.type, s.dose, s.quantity, s.price, s.amount, s.DATE as sale_date, d.name as drug_name 
            FROM sales s
            JOIN drugs d ON s.barcode = d.barcode
            ORDER BY s.DATE DESC
        """)
        sales_list = cursor.fetchall()

        # Convert sale_date string to datetime object if needed
        for sale in sales_list:
            date_value = sale.get('sale_date')
            if isinstance(date_value, str):
                try:
                    sale['sale_date'] = datetime.strptime(date_value, '%Y-%m-%d')
                except ValueError:
                    sale['sale_date'] = None

        return render_template('sales.html', sales=sales_list)
    except Error as e:
        flash(f"Failed to fetch sales: {str(e)}", 'danger')
        return render_template('error.html')
    finally:
        if conn and conn.is_connected():
            conn.close()


@app.route('/sales/add', methods=['GET', 'POST'])
def add_sale():
    conn = get_db_connection()
    if not conn:
        return render_template('error.html')
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            barcode = request.form['barcode']
            quantity = int(request.form['quantity'])
            
            # Get drug details (using uppercase keys)
            cursor.execute("SELECT * FROM drugs WHERE BARCODE = %s", (barcode,))
            drug = cursor.fetchone()
            
            if not drug:
                flash('Drug not found!', 'danger')
                return redirect(url_for('add_sale'))
                
            if drug['QUANTITY'] < quantity:
                flash(f'Not enough stock! Only {drug["QUANTITY"]} available', 'danger')
                return redirect(url_for('add_sale'))
                
            amount = float(drug['SELLING_PRICE']) * quantity
            
            # Add sale record
            cursor.execute("""
                INSERT INTO sales (barcode, name, type, dose, quantity, price, amount, date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURDATE())
            """, (barcode, drug['NAME'], drug['TYPE'], drug['DOSE'], quantity, drug['SELLING_PRICE'], amount))

            
            # Update drug quantity
            cursor.execute("""
                UPDATE drugs 
                SET QUANTITY = QUANTITY - %s 
                WHERE BARCODE = %s
            """, (quantity, barcode))
            
            conn.commit()
            flash('Sale recorded successfully!', 'success')
            return redirect(url_for('sales'))
            
        # Get drugs for dropdown (also using uppercase)
        cursor.execute("SELECT BARCODE, NAME FROM drugs WHERE QUANTITY > 0 ORDER BY NAME")
        drugs = cursor.fetchall()
        
        return render_template('add_sale.html', drugs=drugs)
    except Error as e:
        flash(f"Failed to add sale: {str(e)}", 'danger')
        return redirect(url_for('sales'))
    finally:
        if conn and conn.is_connected():
            conn.close()


# ------------------ Companies ------------------
@app.route('/companies')
def companies():
    conn = get_db_connection()
    if not conn:
        return render_template('error.html')
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM company ORDER BY name")
        companies_list = cursor.fetchall()
        return render_template('companies.html', companies=companies_list)
    except Error as e:
        flash(f"Failed to fetch companies: {str(e)}", 'danger')
        return render_template('error.html')
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/companies/add', methods=['GET', 'POST'])
def add_company():
    fields = ['name', 'address', 'phone']
    
    if request.method == 'POST':
        conn = get_db_connection()
        if not conn:
            return render_template('error.html')
        
        try:
            cursor = conn.cursor()
            data = [request.form[field] for field in fields]
            cursor.execute("""
                INSERT INTO company (name, address, phone)
                VALUES (%s, %s, %s)
            """, data)
            conn.commit()
            flash('Company added successfully!', 'success')
            return redirect(url_for('companies'))
        except Error as e:
            flash(f"Failed to add company: {str(e)}", 'danger')
            return redirect(url_for('add_company'))
        finally:
            if conn and conn.is_connected():
                conn.close()
    
    return render_template('add_company.html', fields=fields)

@app.route('/companies/edit/<path:name>', methods=['GET', 'POST'])
def edit_company(name):
    conn = get_db_connection()
    if not conn:
        return render_template('error.html')
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM company WHERE name = %s", (name,))
        company = cursor.fetchone()
        
        if not company:
            flash('Company not found!', 'danger')
            return redirect(url_for('companies'))
            
        fields = ['name', 'address', 'phone']
        
        if request.method == 'POST':
            data = [request.form[field] for field in fields]
            cursor.execute("""
                UPDATE company 
                SET name=%s, address=%s, phone=%s
                WHERE name=%s
            """, (*data, name))
            conn.commit()
            flash('Company updated successfully!', 'success')
            return redirect(url_for('companies'))
            
        return render_template('edit_company.html', 
                             company=company,
                             fields=fields)
    except Error as e:
        flash(f"Failed to edit company: {str(e)}", 'danger')
        return redirect(url_for('companies'))
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/companies/delete/<name>', methods=['GET', 'POST'])
def delete_company(name):
    conn = get_db_connection()
    if not conn:
        return render_template('error.html')
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM company WHERE name = %s", (name,))
        company = cursor.fetchone()
        
        if not company:
            flash('Company not found!', 'danger')
            return redirect(url_for('companies'))
            
        if request.method == 'POST':
            cursor.execute("DELETE FROM company WHERE name = %s", (name,))
            conn.commit()
            flash('Company deleted successfully!', 'success')
            return redirect(url_for('companies'))
            
        return render_template('delete_company.html', 
                             company=company,
                             cancel_url=url_for('companies'))
    except Error as e:
        flash(f"Failed to delete company: {str(e)}", 'danger')
        return redirect(url_for('companies'))
    finally:
        if conn and conn.is_connected():
            conn.close()

# ------------------ Users ------------------
@app.route('/users')
def users():
    # Ensure the user is logged in and is an admin
    if not session.get('loggedin') or session.get('role') != 'admin':
        flash('Access denied: Admins only.', 'danger')
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", 'danger')
        return render_template('error.html')
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users ORDER BY NAME")  # Adjust column case if needed
        users_list = cursor.fetchall()
        return render_template('users.html', users=users_list)
    except Error as e:
        flash(f"Failed to fetch users: {str(e)}", 'danger')
        return render_template('error.html')
    finally:
        if conn and conn.is_connected():
            conn.close()

# ------------------ Inbox ------------------
@app.route('/inbox')
def inbox():
    conn = get_db_connection()
    if not conn:
        flash("Database connection failed.", 'danger')
        return render_template('inbox.html', messages=[])

    try:
        cursor = conn.cursor(dictionary=True)

        # Fetch latest messages
        cursor.execute("""
            SELECT MESSAGE_FROM, MESSAGE_TO, MESSAGE_TEXT
            FROM inbox
            LIMIT 20
        """)
        messages = cursor.fetchall()

        return render_template('inbox.html', messages=messages)
    except Error as e:
        flash(f"Failed to fetch inbox data: {str(e)}", 'danger')
        return render_template('inbox.html', messages=[])
    finally:
        if conn and conn.is_connected():
            conn.close()




if __name__ == '__main__':
    app.run(debug=True)
