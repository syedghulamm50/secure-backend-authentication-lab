import sqlite3
import csv

def init_db():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    
    # Create a user table matching what we need for the task
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            email TEXT UNIQUE,
            password_hash TEXT,
            sensitive_info TEXT,          -- To store AES-256 encrypted data
            two_factor_secret TEXT,       -- To store the TOTP secret key
            is_2fa_enabled INTEGER DEFAULT 0
        )
    ''')
    
    # Import rows from the mock data CSV
    try:
        with open('mock_users.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cursor.execute('''
                    INSERT OR IGNORE INTO users (id, username, email, password_hash, sensitive_info)
                    VALUES (?, ?, ?, ?, ?)
                ''', (row['id'], row['username'], row['email'], row['password_hash'], row['sensitive_info']))
        conn.commit()
        print("Local database initialized with Mockaroo data successfully!")
    except FileNotFoundError:
        print("Please place 'mock_users.csv' in this folder first.")
        
    conn.close()

if __name__ == '__main__':
    init_db()
