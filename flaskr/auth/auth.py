from flask import Blueprint, render_template, request, flash, redirect, url_for
from flaskr.forms import LoginForm
from flask_login import logout_user
from flaskr.db import get_db
from flaskr.models import User
from flaskr.extensions import login_manager
from flaskr.auth.services import *

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@login_manager.user_loader
def load_user(user_id):
    user_result = get_user_by_id(user_id)
    if user_result:
        return create_user_object(user_result)
    return None

@auth_bp.route('/login-page-admin', methods=['GET', 'POST'])
def login_page_admin():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if authenticate_user(username, password):
            return redirect(url_for('administration.admin_page'))
        else:
            flash("Nesprávné přihlašovací údaje", category="danger")
    return render_template("auth/login_admin.html", form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('reservations.main_page'))