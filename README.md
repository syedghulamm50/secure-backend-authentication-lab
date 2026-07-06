# Secure Backend Authentication Lab

A hands-on cybersecurity project demonstrating **Google OAuth 2.0 Authentication**, **Two-Factor Authentication (2FA)** using Google Authenticator, and **AES-256-GCM Encryption** in a local Flask application built with Python and SQLite.

---

## Features

- Google OAuth 2.0 Authentication
- Google Authenticator (TOTP)
- AES-256-GCM Encryption
- SQLite Database
- Flask REST API
- Mock User Dataset
- Local Testing Environment

---

## Technologies Used

- Python 3
- Flask
- SQLite3
- Cryptography
- PyOTP
- Google OAuth 2.0
- Google Authenticator
- Mockaroo

---

## Project Structure

```text
security_task_mock/
│
├── app.py
├── crypto_helper.py
├── db_setup.py
├── mock_users.csv
├── app.db
├── requirements.txt
├── README.md
│
└── images/
    ├── initial_setup.png
    ├── data_generation.png
    ├── db_setup.png
    ├── crypto_helper.png
    ├── app.png
    └── encrypted_record.png
```

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/secure-backend-authentication-lab.git

cd secure-backend-authentication-lab
```

## 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Environment Setup

![Environment Setup](images/initial_setup.png)

---

## 3. Install Dependencies

```bash
pip install Flask pyotp cryptography requests google-auth google-auth-oauthlib python-dotenv
```

---

## 4. Generate Mock Dataset

Create a CSV file using **Mockaroo** with the following fields:

| Field | Type |
|--------|------|
| id | Row Number |
| username | Username |
| email | Email Address |
| password_hash | MD5 |
| sensitive_info | Phone |

Save the file as

```
mock_users.csv
```

### Mockaroo Configuration

![Mockaroo](images/data_generation.png)

---

## 5. Initialize Database

Run

```bash
python db_setup.py
```

### Database Setup

![Database Setup](images/db_setup.png)

---

## 6. Start the Flask Server

```bash
python app.py
```

### Flask Backend

![Flask Backend](images/app.png)

---

# Google OAuth 2.0

Start the authentication flow by visiting

```
http://127.0.0.1:5000/login-google
```

Google authenticates the user and redirects back to the Flask application.

---

# AES-256-GCM Encryption

Sensitive information is encrypted before being stored in SQLite.

Encryption uses:

- AES-256
- GCM Mode
- Random Nonce
- Authenticated Encryption

### Encryption Helper

![AES Encryption](images/crypto_helper.png)

---

## Store Encrypted Data

```bash
python3 -c "
import sqlite3
from app import encrypt_data

conn = sqlite3.connect('app.db')

encrypted_blob = encrypt_data('+923001234567')

conn.execute(
'INSERT INTO users(username,email,sensitive_info) VALUES(?,?,?)',
('security_intern','intern-test@example.com',encrypted_blob)
)

conn.commit()
conn.close()
"
```

### Encrypted Database Record

![Encrypted Record](images/encrypted_record.png)

---

# Two-Factor Authentication (2FA)

Generate a secret key

```bash
curl -X POST http://127.0.0.1:5000/setup-2fa \
-H "Content-Type: application/json" \
-d '{"email":"intern-test@example.com"}'
```

Verify the generated code

```bash
curl -X POST http://127.0.0.1:5000/verify-2fa \
-H "Content-Type: application/json" \
-d '{"email":"intern-test@example.com","code":"123456"}'
```

---

# Security Features

- OAuth 2.0 Authentication
- Multi-Factor Authentication (TOTP)
- AES-256-GCM Encryption
- Encryption at Rest
- Secure REST API
- SQLite Integration

---

# Learning Outcomes

This project demonstrates:

- Secure Authentication
- OAuth 2.0 Flow
- Multi-Factor Authentication
- Cryptography using AES-256-GCM
- Secure Storage of Sensitive Data
- Flask API Development
- SQLite Database Integration

---

# Future Improvements

- JWT Authentication
- Password Hashing (Argon2)
- PostgreSQL Support
- Docker Deployment
- QR Code Generation
- Role-Based Access Control (RBAC)

---



## License

This project is intended for educational and learning purposes.
