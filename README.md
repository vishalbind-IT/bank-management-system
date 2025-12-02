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

## 1. Prerequisites

- **You must have the following installed on your system**:

- **.Python 3.x**

- **. MySQL Server (version 5.7+)**

---
## 2. Database Configuration

- **1. Create Database: Log into your MySQL instance and run**:

`CREATE DATABASE bank_management_system_db;`


- **2. Configure Credentials: Open bank_management_system/app.py and update the database connection details in the app.config section**:

`app.config['MYSQL_USER'] = 'your_mysql_user'`

`app.config['MYSQL_PASSWORD'] = 'your_mysql_password' # <-- CHANGE THIS`

`app.config['MYSQL_DB'] = 'bank_management_system_db'`


- **3. Run Schema Script: Execute the provided schema file to create tables and seed the initial data**:

`mysql -u [your_user] -p bank_management_system_db < bank_management_system/db.sql`

---
## 3. Project Installation

- **1. Clone the Repository**:

`git clone [your_repo_url]`

`cd bank_management_system`


- **2. Create Virtual Environment (Recommended)**:

`python -m venv venv`

`source venv/bin/activate  # On Windows, use: venv\Scripts\activate`


- **3. Install Dependencies**:

`pip install -r requirements.txt`

---
## 4. Running the Application

- **1. Start the Flask server**:

`python app.py`


- **2. Open your browser to** `http://127.0.0.1:5000.`

