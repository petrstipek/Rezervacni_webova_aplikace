# FileName: login_decorators.py
# Description: Decorators for login required roles.
# Author: Petr Štípek
# Date: 2024

from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.get_role() != 'admin':
            flash('Tato stránka požaduje administrátorská oprávnění.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def instructor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.get_role() != 'instructor':
            flash('Tato stránka požaduje instruktorská oprávnění.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def client_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.get_role() != 'client':
            flash('Tato stránka požaduje oprávnění registrovaného klienta', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function