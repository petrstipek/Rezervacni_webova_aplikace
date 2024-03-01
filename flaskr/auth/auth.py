from flask import Blueprint, render_template, request, flash, redirect, url_for
from flaskr.forms import LoginForm
from flask_login import login_user, logout_user
from flaskr.extensions import db
import os
import hashlib
from flaskr.extensions import login_manager
from flaskr.models import Osoba, SpravceSkoly

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@login_manager.user_loader
def load_user(user_id):
    user_result = Osoba.query.filter_by(ID_osoba=user_id).first()
    if user_result:
        user = User(user_result['ID_osoba'], user_result['prijmeni'])
        return user
    return None

@auth_bp.route('/login-page-admin', methods=['GET', 'POST'])
def login_page_admin():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        query_result = SpravceSkoly.query.filter_by(prihl_jmeno=username).first()
        if query_result and check_password(query_result['heslo'], password):
            user = User(query_result['ID_osoba'], query_result['prihl_jmeno'])
            login_user(user, remember=request.form.get('remember'))
            return redirect(url_for('administration.admin_page'))
        else:
            flash("Invalid parameters")
    return render_template("auth/login_admin.html", form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('reservations.main_page'))


def hash_password(password):
    salt = os.urandom(16)
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex() + ':' + pwdhash.hex()

def check_password(stored_password, user_password):
    salt, hash = stored_password.split(':')
    pwdhash = hashlib.pbkdf2_hmac('sha256', user_password.encode(), bytes.fromhex(salt), 100000)
    return pwdhash.hex() == hash