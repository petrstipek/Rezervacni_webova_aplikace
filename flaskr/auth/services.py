import os
import hashlib
from flaskr.models import Osoba
from flaskr.extensions import database
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
    #print(hash_password("password123"))
    user = database.session.query(Osoba).filter_by(prihl_jmeno=username).first()
    if user and check_password(user.heslo, password):
        user = database.session.query(Osoba).filter(Osoba.prihl_jmeno == username).first()
        login_user(user, remember=request.form.get('remember'))
        return True
    return False

def get_user_by_id(user_id):
    return database.session.query(Osoba).filter_by(ID_osoba=user_id).first()

def create_user_object(user_result):
    if user_result:
        return Osoba(user_result.ID_osoba, user_result.prijmeni)
    return None
