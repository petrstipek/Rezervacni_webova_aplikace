from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flaskr.forms import PersonalInformationForm, ReservationInformationForm
from flaskr.reservations.services import *
from flaskr.api.services.instructor_services import get_all_instructors
import requests
from flaskr.extensions import recaptcha_private

reservations_bp = Blueprint('reservations', __name__, template_folder='templates')

@reservations_bp.route('/reservation-check')
def reservation_check():
    form = ReservationInformationForm()
    return render_template("blog/user/reservation_check.html", form=form)

@reservations_bp.route("/", methods=["GET", "POST"])
def main_page():
    form = PersonalInformationForm()
    #opravit vůči 0?
    available_instructors = get_all_instructors()
    available_instructors = handle_all_instructors(available_instructors)
    form.lesson_instructor_choices.choices = available_instructors

    secret_response = request.form["g-recaptcha-response"]
    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    verify_response = requests.post(url=f'{verify_url}?secret={recaptcha_private}&response={secret_response}').json()
    
    if verify_response["success"] == False:
        abort(401)

    if form.validate_on_submit():
        print("jsem tady")

        message, message_type = process_reservation(form)
        flash(message, category=message_type)

        return redirect(url_for('reservations.main_page'))

    return render_template("blog/user/reservation_page.html", active_page="reservation_page", form=form)
