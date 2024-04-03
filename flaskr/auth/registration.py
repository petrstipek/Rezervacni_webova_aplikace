from flask import Blueprint, render_template, request, flash, redirect, url_for
from flaskr.forms import RegistrationForm
from flaskr.auth.services import register_new_user
from flaskr.email.email import send_registration_confirmation

registration_bp = Blueprint('registration', __name__, template_folder='templates')

@registration_bp.route("/", methods=["GET", "POST"])
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
