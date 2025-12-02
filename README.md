# Bank Management System (BMS) - Full-Stack Fintech Application

## Project Overview

This is a comprehensive, full-stack **Bank Management System (BMS)** built using **Python's Flask framework** for the backend and **MySQL** for persistent data storage. It features secure user authentication and authorization for two distinct roles: **Admin** and **Client**.  

The frontend is designed with a modern, responsive "Fintech" aesthetic using **HTML, CSS, and JavaScript**.

This project is structured for portfolio display, showcasing **clean separation of concerns**, **transactional integrity**, and **security best practices** (password hashing, prepared statements).

---

## Features

### Authentication & Roles
- **Secure Login/Registration**: Uses `werkzeug.security` for password hashing and **Flask Sessions** for state management.
- **Roles**: 
  - **Admin** – full system control  
  - **Client** – account holder

### Client Functionality
- **Dashboard**: Displays current account balance and status.
- **Transactions**: Supports Deposit, Withdrawal, and Account Transfer.
- **History**: Dedicated view for personal transaction records.
- **Security**: Requires sufficient balance for withdrawals/transfers; transactions are atomic.

### Admin Functionality
- **Account Management**: View all client accounts (Name, Account Number, Balance, Status).
- **Control**: Activate/Deactivate client accounts.
- **Global View**: View comprehensive history of all transactions.

---

## Technology Stack
- **Backend**: Python (Flask)  
- **Database**: MySQL  
- **Frontend**: HTML5, CSS (custom `styles.css`), JavaScript  
- **Security**: `werkzeug.security` (Password Hashing)

---

## Local Setup Guide

### 1. Prerequisites
- Python 3.x
- MySQL Server (v5.7+)

### 2. Database Configuration
1. **Create Database**  
   ```sql
   CREATE DATABASE bank_management_system_db;
Configure Credentials
Update the database connection in bank_management_system/app.py:

python
Copy code
app.config['MYSQL_USER'] = 'your_mysql_user'
app.config['MYSQL_PASSWORD'] = 'your_mysql_password'  # <-- CHANGE THIS
app.config['MYSQL_DB'] = 'bank_management_system_db'
Run Schema Script
Execute the provided schema file:

bash
Copy code
mysql -u [your_user] -p bank_management_system_db < bank_management_system/db.sql
3. Project Installation
Clone the Repository

bash
Copy code
git clone [your_repo_url]
cd bank_management_system
Create Virtual Environment

bash
Copy code
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
Install Dependencies

bash
Copy code
pip install -r requirements.txt
4. Running the Application
bash
Copy code
python app.py
Open your browser at http://127.0.0.1:5000.

Initial Access
Two users are created in db.sql for immediate testing:

Role	Username	Password	Account No.	Initial Balance
Admin	admin	adminpass123	N/A	N/A
Client	client1	adminpass123	1000000001	$500.00
