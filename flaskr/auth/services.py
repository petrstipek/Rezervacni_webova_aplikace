import os
import hashlib
#from flaskr.models import Osoba, Klient
from flaskr.extensions import database
from flask_login import login_user
from flask import request


from flaskr.models.instructor import Instruktor
from flaskr.models.user import Osoba
from flaskr.models.reservation import Rezervace, MaVypsane, MaVyuku, Prirazeno
from flaskr.models.client import Klient
from flaskr.models.student import Zak
from flaskr.models.available_times import DostupneHodiny

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
    user = database.session.query(Osoba).filter(Osoba.prihl_jmeno==username).first()
    if user and check_password(user.heslo, password):
        user = database.session.query(Osoba).filter(Osoba.prihl_jmeno == username).first()
        login_user(user, remember=request.form.get('remember'))
        return user
    return None

def get_user_by_id(user_id):
    return database.session.query(Osoba).filter_by(ID_osoba=user_id).first()

def create_user_object(user_result):
    if user_result:
        return Osoba(user_result.ID_osoba, user_result.prijmeni)
    return None

def register_new_user(form):
    existing_user = database.session.query(Osoba).filter(Osoba.prihl_jmeno == form.email.data).first()

    if existing_user:
        return None, "Registrovaný účet s tímto emailem existuje!"

    existing_non_registered_user = database.session.query(Osoba).filter(Osoba.email == form.email.data).first()
    
    if existing_non_registered_user:
        user = existing_non_registered_user
    else:
        user = Osoba(
            jmeno=form.name.data,
            prijmeni=form.surname.data,
            tel_cislo=form.tel_number.data,
            email=form.email.data,
        )
        database.session.add(user)
        database.session.flush()

        new_client = Klient(ID_osoba=user.ID_osoba)
        database.session.add(new_client)

    user.prihl_jmeno = form.email.data
    hashed_password = hash_password(form.password.data)
    user.heslo = hashed_password

    try:
        database.session.commit()
        return user, "Registrace proběhla úspěšně!"
    except Exception as e:
        database.session.rollback()
        print(f"Error during registration: {e}")
        return False, "Při registraci došlo k chybě!"

def check_email(email):
    existing_user = database.session.query(Osoba).filter(Osoba.email==email).first()
    if existing_user:
        return existing_user
    else:
        return False
    
def change_password(email, password):
    existing_user = database.session.query(Osoba).filter(Osoba.email==email).first()
    if existing_user:
        existing_user.heslo = hash_password(password)
    else:
        return False
    try:
        database.session.commit()
        return True
    except Exception as e:
        database.session.rollback()
        return False