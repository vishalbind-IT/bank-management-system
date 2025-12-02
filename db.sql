-- Bank Management System (BMS) MySQL Schema

-- -----------------------------------------------------
-- Table users
-- -----------------------------------------------------
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'client') NOT NULL
);

-- -----------------------------------------------------
-- Table accounts
-- -----------------------------------------------------
CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_number VARCHAR(20) NOT NULL UNIQUE,
    balance DECIMAL(10, 2) DEFAULT 0.00,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- -----------------------------------------------------
-- Table transactions
-- -----------------------------------------------------
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL, -- The account performing the transaction (source for withdrawal/transfer, destination for deposit)
    type ENUM('deposit', 'withdrawal', 'transfer') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    related_account_number VARCHAR(20) NULL, -- For transfer transactions
    description TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

-- -----------------------------------------------------
-- Initial Data Setup
-- -----------------------------------------------------

-- Insert a default Admin user:
-- Username: admin
-- Password: adminpass123
-- The hash is generated from 'adminpass123' using werkzeug.security.generate_password_hash()
INSERT INTO users (username, password_hash, role) VALUES
('admin', 'pbkdf2:sha256:600000$g40eS0g9$615456f3f019688457c37b7713d81b498f395697084511d7f7663f73663a893e', 'admin');

-- Insert a test client user and account
INSERT INTO users (username, password_hash, role) VALUES
('client1', 'pbkdf2:sha256:600000$g40eS0g9$615456f3f019688457c37b7713d81b498f395697084511d7f7663f73663a893e', 'client'); -- Password: adminpass123

INSERT INTO accounts (user_id, account_number, balance, status) VALUES
(LAST_INSERT_ID(), '1000000001', 500.00, 'active');