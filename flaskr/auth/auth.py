from flask import Blueprint, render_template, flash, redirect, url_for
from flaskr.forms import LoginForm
from flask_login import logout_user
from flaskr.extensions import login_manager
from flaskr.auth.services import *
from functools import wraps

auth_bp = Blueprint('auth', __name__, template_folder='templates')
from flaskr.auth.renew_password import renew_password
from flaskr.auth.renew_password import reset_password
from flaskr.auth.registration import registration_user

@login_manager.user_loader
def load_user(user_id):
    user_result = get_user_by_id(user_id)
    if user_result:
        return user_result
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = authenticate_user(username, password)
        if user:
            if user.get_role() == 'admin':
                return redirect(url_for('administration.admin_page'))
            elif user.get_role() == 'instructor':
                return redirect(url_for('instructor.instructors_reservations'))
            elif user.get_role() == 'client':
                return redirect(url_for('users.users_reservations'))
            else:
                flash("Nepovolený přístup, prosím přihlašte se!", category="danger")
                return redirect(url_for('auth.login'))
        else:
            flash("Nesprávné jméno nebo heslo!", category="danger")
    return render_template("auth/login.html", form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash("Byli jste úspěšně odhlášeni!", category="success")
    return redirect(url_for('reservations.main_page'))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('auth.login'))