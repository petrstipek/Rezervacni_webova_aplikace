from flask import Blueprint, render_template, flash, redirect, url_for, session, request, abort
from flaskr.forms import PersonalInformationForm, ReservationInformationForm
from flaskr.reservations.services import *
from flaskr.api.services.instructor_services import get_all_instructors
from flaskr.extensions import recaptcha_private
import requests
from flaskr.extensions import verify_url
from flask_login import current_user

reservations_bp = Blueprint('reservations', __name__, template_folder='templates')

@reservations_bp.route('/test')
def test():
    return render_template("blog/user/test.html")

@reservations_bp.route('/reservation-check')
def reservation_check():
    form = ReservationInformationForm()
    return render_template("blog/user/user_reservation_check.html", form=form)

@reservations_bp.route("/", methods=["GET", "POST"])
def main_page():
    flash('Informace na této webové stránce jsou pouze testového charakterů a v žádném případě nejsou oficiálním sdělením společnosti!', 'warning')
    form = PersonalInformationForm()
    if current_user.is_authenticated:
        form.name.data = current_user.jmeno
        form.surname.data = current_user.prijmeni
        form.email.data = current_user.email
        form.tel_number.data = current_user.tel_cislo

    #opravit vůči 0?
    available_instructors = get_all_instructors()
    available_instructors = handle_all_instructors(available_instructors)
    form.lesson_instructor_choices.choices = available_instructors

    if request.method == "POST":
        secret_response = request.form.get("g-recaptcha-response")
        if secret_response:
            verify_response = requests.post(url= verify_url, data={'secret': recaptcha_private, 'response': secret_response}).json()
            if not verify_response.get("success"):
                flash("Chyba ve validaci Captcha. Opakujte prosím odeslání!", category="danger")
                return render_template("blog/user/reservation_page.html", form=form, active_page="reservation_page")
        else:
            flash("Captcha chyba. Opakujte odeslání!", category="danger")
            return render_template("blog/user/reservation_page.html", form=form, active_page="reservation_page")
        
        if form.validate_on_submit():
            register_without = form.submit_without_register.data
            register_with = form.submit_with_register.data

            if register_with:
                status_reg, message_reg = process_submit_registration(form)

            result = process_reservation(form)

            if len(result) == 3:
                message, message_type, reservation_code = result
            elif len(result) == 2:
                message, message_type = result
            
            if register_with and message and status_reg:
                flash("Rezervace proběhla úspěšně! " + message_reg, category="success")
                return redirect(url_for('reservations.main_page'))
            if register_with and message and not status_reg:
                flash("Rezervace proběhla úspěšně, ale registrace selhala. Zkuste to znovu.", category="warning")
                return redirect(url_for('reservations.main_page'))
            if register_without and message:
                flash(message, category=message_type)
                return redirect(url_for('reservations.main_page'))


            flash(message, category=message_type)
            return redirect(url_for('reservations.main_page'))
        else:
            print(form.errors, "Form errors")
            custom_messages = {
            'name': 'Doplňtě Vaše jméno.',
            'surname': 'Doplňte Vaše příjmení.',
            'tel_number': 'Doplňte vaše telefonní číslo.',
            'email': 'Doplňte vaší emailovou adresu.',
            'age_client': 'Doplňte věk.',
            'time_reservation': 'Doplňte čas výuky.',
            }
        
            error_messages = []
            for field, errors in form.errors.items():
                message = custom_messages.get(field, '; '.join(errors))
                error_messages.append(f"{message}")
            
            flash("Prosím, opravte následující chyby: " + ", ".join(error_messages), category="danger")
            print("Form errors:", form.errors)
            
    return render_template("blog/user/reservation_page.html", active_page="reservation_page", form=form, is_logged_in=current_user.is_authenticated)

