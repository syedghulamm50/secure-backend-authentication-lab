import os
import sqlite3
import requests
import pyotp
from flask import Flask, request, jsonify, redirect
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

app = Flask(__name__)
app.secret_key = "DEVELOPMENT_ONLY_SUPER_SECRET_KEY"

# Bypass HTTPS enforcement strictly for localized loopback testing
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# ==========================================
# 1. LIVE GOOGLE CREDENTIAL CONFIGURATION
# ==========================================
CLIENT_ID = "(Insert you won)"
CLIENT_SECRET = "(Insert you won)"
REDIRECT_URI = "http://127.0.0.1:5000/callback"

SCOPES = [
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

# Cryptographically sound 32-byte key (256 bits) for AES-256-GCM data masking
AES_KEY = b'sixteen_byte_key_sixteen_byte_kk' 

def get_db_connection():
    conn = sqlite3.connect('app.db')
    conn.row_factory = sqlite3.Row
    return conn

# ==========================================
# 2. AES-256 DATA SECURITY ENGINES
# ==========================================
def encrypt_data(plaintext: str) -> bytes:
    aesgcm = AESGCM(AES_KEY)
    nonce = os.urandom(12)  # Unique 96-bit Initialization Vector (IV) per transaction
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return nonce + ciphertext

def decrypt_data(ciphertext_with_nonce: bytes) -> str:
    aesgcm = AESGCM(AES_KEY)
    nonce = ciphertext_with_nonce[:12]
    ciphertext = ciphertext_with_nonce[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()


# ==========================================
# 3. GOOGLE OAUTH 2.0 FLOW ROUTES
# ==========================================
@app.route('/login-google')
def login_google():
    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    if 'code' not in request.args:
        return jsonify({"status": "Error", "message": "Missing authorization code."}), 400

    flow = Flow.from_client_config(
        client_config={
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES
    )
    flow.redirect_uri = REDIRECT_URI
    
    try:
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        user_info = id_token.verify_oauth2_token(credentials.id_token, google_requests.Request(), CLIENT_ID)
        
        return jsonify({
            "status": "OAuth 2.0 Verification Success!",
            "user": {
                "name": user_info.get('name'),
                "email": user_info.get('email')
            }
        })
    except Exception as e:
        return jsonify({"status": "Token Exchange Failed", "error": str(e)}), 400


# ==========================================
# 4. GOOGLE AUTHENTICATOR (2FA) ROUTES
# ==========================================
@app.route('/setup-2fa', methods=['POST'])
def setup_2fa():
    email = request.json.get('email')
    secret = pyotp.random_base32()
    
    conn = get_db_connection()
    conn.execute('UPDATE users SET two_factor_secret = ?, is_2fa_enabled = 1 WHERE email = ?', (secret, email))
    conn.commit()
    conn.close()
    
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(name=email, issuer_name="InterneePKMock")
    
    return jsonify({
        "status": "2FA Configured",
        "secret_key": secret,
        "totp_uri": provisioning_uri
    })

@app.route('/verify-2fa', methods=['POST'])
def verify_2fa():
    email = request.json.get('email')
    code = request.json.get('code')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if not user or not user['two_factor_secret']:
        return jsonify({"error": "2FA not configured for this user account."}), 400
        
    totp = pyotp.TOTP(user['two_factor_secret'])
    if totp.verify(code):
        return jsonify({"status": "Success", "message": "2FA Code Accepted!"})
    return jsonify({"status": "Failed", "message": "Invalid 2FA token."}), 401


# ==========================================
# 5. ENGINE INITIALIZATION
# ==========================================
if __name__ == '__main__':
    conn = sqlite3.connect('app.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT, email TEXT UNIQUE, password_hash TEXT,
            sensitive_info BLOB, two_factor_secret TEXT, is_2fa_enabled INTEGER DEFAULT 0
        )
    ''')
    conn.close()
    
    app.run(host="127.0.0.1", port=5000, debug=True)
