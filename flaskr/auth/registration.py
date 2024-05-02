# FileName: registration.py
# Description: Handles the registration route for regsitration.
# Author: Petr Štípek
# Date: 2024

from flask import render_template, request, flash, redirect, url_for
from flaskr.forms import RegistrationForm
from flaskr.auth.services import register_new_user
from flaskr.email.email import send_registration_confirmation
from flaskr.auth.auth import auth_bp

@auth_bp.route("/registration", methods=["GET", "POST"])
def registration_user():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_registered, message = register_new_user(form)
        if user_registered:
            flash("Registrace proběhla úspěšně, nyní se můžete přihlásit!", category="success")
            send_registration_confirmation(form.email.data)
            return redirect(url_for('auth.login'))
        else:
            flash(message, category="danger")
    return render_template("/auth/registration.html", form=form)
