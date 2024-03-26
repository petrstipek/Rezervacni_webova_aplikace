from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required
from flaskr.auth.login_decorators import client_required
from flaskr.forms import PersonalInformationFormUser
from flask_login import current_user
from flaskr.users.users_services import validate_password, update_personal_information

users_bp = Blueprint('users', __name__, template_folder='templates')

@users_bp.route('/reservations')
@login_required
@client_required
def users_reservations():
    return render_template("/blog/user/user_page.html", active_page="users_reservations")

@users_bp.route('/profile', methods=["GET", "POST"])
@login_required
def users_profile():
    form = PersonalInformationFormUser()

    if not form.validate_on_submit():
        form.name.data = current_user.jmeno
        form.surname.data = current_user.prijmeni
        form.email.data = current_user.email
        form.tel_number.data = current_user.tel_cislo

    if form.validate_on_submit():
        if form.old_password.data:
            valid_password = validate_password(form.old_password.data)
            if valid_password:
                information_update, message = update_personal_information(
                    form.name.data, 
                    form.surname.data, 
                    form.email.data, 
                    form.tel_number.data, 
                    form.new_password.data if form.new_password.data else None
                )
                if information_update:
                    flash(message, category="success")
                    return redirect(url_for('users.users_profile'))
                else:
                    flash(message, category="danger")
            else:
                flash("Zadané aktuální heslo neodpovídá uloženému heslu!", category="danger")
        else:
            information_update, message = update_personal_information(
                form.name.data, 
                form.surname.data, 
                form.email.data, 
                form.tel_number.data, 
                None
            )
            if information_update:
                flash(message, category="success")
                return redirect(url_for('users.users_profile'))
            else:
                flash(message, category="danger")

    return render_template("/blog/user/user_profile.html", form=form, active_page="users_profile")