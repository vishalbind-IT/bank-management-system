import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import random
from decimal import Decimal


# --- Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_secure_random_key_for_session_management'
# Your MySQL credentials
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bank_management_system_db'
app.config['MYSQL_PORT'] = 3306

# --- Database Connection Utility ---

def get_db():
    """Establishes a connection to the MySQL database or returns the existing connection."""
    if 'db' not in g:
        try:
            g.db = mysql.connector.connect(
                host=app.config['MYSQL_HOST'],
                user=app.config['MYSQL_USER'],
                password=app.config['MYSQL_PASSWORD'],
                database=app.config['MYSQL_DB'],
                port=app.config['MYSQL_PORT']
            )
        except mysql.connector.Error as err:
            print(f"Database connection error: {err}")
            flash('Database connection failed. Check server status and credentials.', 'danger')
            return None
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None and db.is_connected():
        db.close()

# --- Authentication and Authorization Decorators ---

def login_required(f):
    """Decorator to require login for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You must be logged in to view this page.', 'info')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require Admin role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return login_required(decorated_function)

def client_required(f):
    """Decorator to require Client role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'client':
            flash('Access denied. Client privileges required.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return login_required(decorated_function)

# --- Account Helpers ---

def get_client_account(user_id):
    """Fetches the client's account details."""
    db = get_db()
    if not db: return None
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM accounts WHERE user_id = %s", (user_id,))
    account = cursor.fetchone()
    cursor.close()
    return account

def generate_unique_account_number(cursor):
    """Generates a unique 10-digit account number."""
    while True:
        # Simple 10-digit generation for example purposes
        account_number = str(random.randint(1000000000, 9999999999))
        cursor.execute("SELECT account_number FROM accounts WHERE account_number = %s", (account_number,))
        if not cursor.fetchone():
            return account_number

# --- Routes ---

@app.route('/')
def index():
    """Redirects authenticated users to their respective dashboards."""
    if 'user_id' in session:
        if session['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('client_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        if not db: return redirect(url_for('login'))
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("SELECT id, password_hash, role FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = username
            session['role'] = user['role']
            flash(f"Welcome back, {username}!", 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('client_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    """Handles new client registration and automatic account opening."""
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        flash('Username and password are required.', 'danger')
        return redirect(url_for('login'))
    
    db = get_db()
    if not db: return redirect(url_for('login'))
    cursor = db.cursor()

    try:
        # 1. Create User
        hashed_password = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'client')",
                       (username, hashed_password))
        user_id = cursor.lastrowid
        
        # 2. Create Account
        account_number = generate_unique_account_number(cursor)
        cursor.execute("INSERT INTO accounts (user_id, account_number, balance, status) VALUES (%s, %s, %s, 'active')",
                       (user_id, account_number, 0.00))
        
        db.commit()
        flash(f'Registration successful! Account {account_number} created with $0.00 balance.', 'success')
    except mysql.connector.Error as err:
        db.rollback()
        if err.errno == 1062: # Duplicate entry for username
            flash('Username already exists. Please choose another.', 'danger')
        else:
            print(f"Database error during registration: {err}")
            flash('An unexpected error occurred during registration.', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    """Logs the user out and clears the session."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- ADMIN ROUTES ---

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Displays the admin dashboard with all accounts and transactions."""
    db = get_db()
    if not db: return render_template('admin_dashboard.html', accounts=[], transactions=[])
    cursor = db.cursor(dictionary=True)

    # Fetch all accounts
    cursor.execute("""
        SELECT a.id, a.account_number, a.balance, a.status, u.username
        FROM accounts a
        JOIN users u ON a.user_id = u.id
        ORDER BY u.username
    """)
    accounts = cursor.fetchall()

    # Fetch all transactions
    cursor.execute("""
        SELECT t.id, t.type, t.amount, t.timestamp, t.related_account_number, t.description, a.account_number
        FROM transactions t
        JOIN accounts a ON t.account_id = a.id
        ORDER BY t.timestamp DESC
    """)
    transactions = cursor.fetchall()
    
    cursor.close()
    return render_template('admin_dashboard.html', accounts=accounts, transactions=transactions)

@app.route('/admin/create_account', methods=['POST'])
@admin_required
def create_account():
    """Admin creates a bank account for an existing client user."""
    username = request.form['username']
    initial_balance = request.form['initial_balance']
    
    db = get_db()
    if not db: return redirect(url_for('admin_dashboard'))
    cursor = db.cursor()

    # 1. Find the user ID
    cursor.execute("SELECT id FROM users WHERE username = %s AND role = 'client'", (username,))
    user = cursor.fetchone()
    if not user:
        flash(f"User '{username}' not found or is not a client.", 'danger')
        cursor.close()
        return redirect(url_for('admin_dashboard'))

    user_id = user[0]

    try:
        # 2. Check if user already has an active account (optional restriction)
        cursor.execute("SELECT account_number FROM accounts WHERE user_id = %s AND status = 'active'", (user_id,))
        if cursor.fetchone():
            flash(f"User '{username}' already has an active account.", 'danger')
            cursor.close()
            return redirect(url_for('admin_dashboard'))

        # 3. Create Account
        account_number = generate_unique_account_number(cursor)
        cursor.execute("INSERT INTO accounts (user_id, account_number, balance, status) VALUES (%s, %s, %s, 'active')",
                       (user_id, account_number, initial_balance))
        
        db.commit()
        flash(f'Account {account_number} created for {username} with initial balance ${initial_balance}.', 'success')
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Database error during account creation: {err}")
        flash('Error creating account. Ensure initial balance is valid.', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_status/<int:account_id>', methods=['POST'])
@admin_required
def toggle_account_status(account_id):
    """Toggles the status of a client account (active/inactive)."""
    db = get_db()
    if not db: return redirect(url_for('admin_dashboard'))
    cursor = db.cursor()
    
    try:
        cursor.execute("SELECT status, account_number FROM accounts WHERE id = %s", (account_id,))
        account = cursor.fetchone()
        
        if not account:
            flash("Account not found.", 'danger')
            cursor.close()
            return redirect(url_for('admin_dashboard'))
        
        new_status = 'inactive' if account[0] == 'active' else 'active'
        account_number = account[1]

        cursor.execute("UPDATE accounts SET status = %s WHERE id = %s", (new_status, account_id))
        db.commit()
        flash(f"Account {account_number} status changed to {new_status.upper()}.", 'info')
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Database error during status toggle: {err}")
        flash('Error updating account status.', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('admin_dashboard'))


# --- CLIENT ROUTES ---

@app.route('/client')
@client_required
def client_dashboard():
    """Displays the client dashboard with balance and transaction forms."""
    user_id = session['user_id']
    account = get_client_account(user_id)

    if not account:
        flash('No active account found. Contact admin.', 'danger')
        # Log out or redirect to a placeholder page if no account is found
        return redirect(url_for('logout')) 
        
    return render_template('client_dashboard.html', account=account)

@app.route('/client/deposit', methods=['POST'])
@client_required
def deposit():
    """Handles a deposit transaction."""
    user_id = session['user_id']
    amount = float(request.form.get('amount', 0))

    account = get_client_account(user_id)
    if not account or account['status'] != 'active':
        flash("Account is inactive or not found. Deposit failed.", 'danger')
        return redirect(url_for('client_dashboard'))

    if amount <= 0:
        flash("Deposit amount must be positive.", 'danger')
        return redirect(url_for('client_dashboard'))

    db = get_db()
    if not db: return redirect(url_for('client_dashboard'))
    cursor = db.cursor()
    
    try:
        # 1. Update Account Balance
        new_balance = account['balance'] + Decimal(str(amount))

        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_balance, account['id']))
        
        # 2. Record Transaction
        cursor.execute("""
            INSERT INTO transactions (account_id, type, amount, description) 
            VALUES (%s, 'deposit', %s, 'Direct deposit')
        """, (account['id'], amount))
        
        db.commit()
        flash(f"Successfully deposited ${amount:,.2f}. New balance: ${new_balance:,.2f}", 'success')
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Database error during deposit: {err}")
        flash('Deposit transaction failed due to a system error.', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('client_dashboard'))

@app.route('/client/withdraw', methods=['POST'])
@client_required
def withdraw():
    """Handles a withdrawal transaction."""
    user_id = session['user_id']
    amount = float(request.form.get('amount', 0))

    account = get_client_account(user_id)
    if not account or account['status'] != 'active':
        flash("Account is inactive or not found. Withdrawal failed.", 'danger')
        return redirect(url_for('client_dashboard'))

    if amount <= 0:
        flash("Withdrawal amount must be positive.", 'danger')
        return redirect(url_for('client_dashboard'))

    if account['balance'] < amount:
        flash("Insufficient funds for withdrawal.", 'danger')
        return redirect(url_for('client_dashboard'))

    db = get_db()
    if not db: return redirect(url_for('client_dashboard'))
    cursor = db.cursor()
    
    try:
        # 1. Update Account Balance
        new_balance = account['balance'] - Decimal(str(amount))

        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_balance, account['id']))
        
        # 2. Record Transaction
        cursor.execute("""
            INSERT INTO transactions (account_id, type, amount, description) 
            VALUES (%s, 'withdrawal', %s, 'ATM/Cash withdrawal')
        """, (account['id'], amount))
        
        db.commit()
        flash(f"Successfully withdrew ${amount:,.2f}. Remaining balance: ${new_balance:,.2f}", 'success')
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Database error during withdrawal: {err}")
        flash('Withdrawal transaction failed due to a system error.', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('client_dashboard'))


@app.route('/client/transfer', methods=['POST'])
@client_required
def transfer():
    """Handles a transfer transaction using a database transaction."""
    user_id = session['user_id']
    target_account_number = request.form['target_account_number']
    amount = float(request.form.get('amount', 0))

    source_account = get_client_account(user_id)

    # Validation Checks
    if not source_account or source_account['status'] != 'active':
        flash("Your account is inactive or not found. Transfer failed.", 'danger')
        return redirect(url_for('client_dashboard'))
    if amount <= 0:
        flash("Transfer amount must be positive.", 'danger')
        return redirect(url_for('client_dashboard'))
    if source_account['balance'] < amount:
        flash("Insufficient funds for transfer.", 'danger')
        return redirect(url_for('client_dashboard'))
    if source_account['account_number'] == target_account_number:
        flash("Cannot transfer funds to the same account.", 'danger')
        return redirect(url_for('client_dashboard'))

    db = get_db()
    if not db: return redirect(url_for('client_dashboard'))
    cursor = db.cursor(dictionary=True)
    
    # 1. Find Target Account
    cursor.execute("SELECT id, balance, status FROM accounts WHERE account_number = %s", (target_account_number,))
    target_account = cursor.fetchone()

    if not target_account:
        flash(f"Target account number {target_account_number} not found.", 'danger')
        cursor.close()
        return redirect(url_for('client_dashboard'))
    if target_account['status'] != 'active':
        flash("Target account is inactive. Transfer failed.", 'danger')
        cursor.close()
        return redirect(url_for('client_dashboard'))

    # Start Database Transaction
    try:
        # 2. Debit Source Account
        new_source_balance = source_account['balance'] - Decimal(str(amount))
        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_source_balance, source_account['id']))

        # 3. Credit Target Account
        new_target_balance = target_account['balance'] + Decimal(str(amount))

        cursor.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_target_balance, target_account['id']))

        # 4. Record Source Transaction (Transfer OUT)
        cursor.execute("""
            INSERT INTO transactions (account_id, type, amount, related_account_number, description) 
            VALUES (%s, 'transfer', %s, %s, 'Transfer Out')
        """, (source_account['id'], amount, target_account_number))

        # 5. Record Target Transaction (Transfer IN) - Uses the source account's number as the related account for logging
        cursor.execute("""
            INSERT INTO transactions (account_id, type, amount, related_account_number, description) 
            VALUES (%s, 'deposit', %s, %s, 'Transfer In')
        """, (target_account['id'], amount, source_account['account_number']))

        db.commit()
        flash(f"Successfully transferred ${amount:,.2f} to account {target_account_number}.", 'success')
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Database error during transfer: {err}")
        flash('Transfer failed due to a system error. Funds have been returned.', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('client_dashboard'))

@app.route('/client/history')
@client_required
def history():
    """Displays the client's personal transaction history."""
    user_id = session['user_id']
    account = get_client_account(user_id)

    if not account:
        flash('No active account found. Contact admin.', 'danger')
        return redirect(url_for('logout'))

    db = get_db()
    if not db: return render_template('history.html', transactions=[], account_number=account['account_number'])
    cursor = db.cursor(dictionary=True)

    # Fetch all transactions related to the client's account
    cursor.execute("""
        SELECT id, type, amount, timestamp, related_account_number, description
        FROM transactions
        WHERE account_id = %s
        ORDER BY timestamp DESC
    """, (account['id'],))
    
    transactions = cursor.fetchall()

    # Determine if a transfer is a credit (in) or debit (out) for display purposes
    for tx in transactions:
        if tx['type'] == 'deposit' and tx['description'] == 'Transfer In':
            tx['type'] = 'transfer'
            tx['is_credit'] = True
        elif tx['type'] == 'transfer' and tx['description'] == 'Transfer Out':
            tx['is_credit'] = False
        elif tx['type'] == 'deposit':
            tx['is_credit'] = True
        else:
            tx['is_credit'] = False
        
    cursor.close()
    return render_template('history.html', transactions=transactions, account_number=account['account_number'])


if __name__ == '__main__':
    # NOTE: You MUST change the MYSQL_PASSWORD in the config section above
    print("-------------------------------------------------------------------------")
    print(f"Flask App Initialized. Database: {app.config['MYSQL_DB']}")
    print("1. Ensure your MySQL server is running.")
    print("2. Create the database named 'bank_management_system_db'.")
    print("3. Execute the SQL script 'bank_management_system/db.sql' to set up tables and the initial admin user.")
    print("   Initial Admin Login: Username: admin, Password: adminpass123")
    print("-------------------------------------------------------------------------")
    
    # You can change host='0.0.0.0' to host='127.0.0.1' if you only need local access
    app.run(debug=True, host='0.0.0.0', port=5000)