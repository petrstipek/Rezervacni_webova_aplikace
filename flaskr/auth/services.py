import os
import hashlib

from flaskr.models import User
from flaskr.db import get_db

from flask_login import login_user
from flask import request

def hash_password(password):
    salt = os.urandom(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex() + ':' + pwdhash.hex()

def check_password(stored_password, user_password):
    try:
        salt, hash = stored_password.split(':')
        pwdhash = hashlib.pbkdf2_hmac('sha256', user_password.encode(), bytes.fromhex(salt), 100000)
        return pwdhash.hex() == hash
    except ValueError:
        return False 

def authenticate_user(username, password):
    db = get_db()
    query_result = db.execute('SELECT * FROM Spravce_skoly WHERE prihl_jmeno = ?', (username,)).fetchone()
    if query_result and check_password(query_result['heslo'], password):
        user = User(query_result['ID_osoba'], query_result['prihl_jmeno'])
        login_user(user, remember=request.form.get('remember'))
        return True
    return False

def get_user_by_id(user_id):
    db = get_db()
    return db.execute('SELECT * FROM Spravce_skoly WHERE ID_osoba = ?', (user_id,)).fetchone()

def create_user_object(user_result):
    if user_result:
        return User(user_result['ID_osoba'], user_result['prijmeni'])
    return None
