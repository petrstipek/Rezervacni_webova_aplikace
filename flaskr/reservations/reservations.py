from flask import Blueprint, render_template, flash, redirect, url_for, session, request
from flaskr.forms import PersonalInformationForm, ReservationInformationForm
from flaskr.reservations.services import *
from flaskr.api.services.instructor_services import get_all_instructors

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
    print(available_instructors)
    print(form.validate_on_submit())
    if request.method == "POST":
        if form.validate_on_submit():
            message, message_type = process_reservation(form)
            flash(message, category=message_type)
            return redirect(url_for('reservations.main_page'))
        else:
            flash("Rezervace neproběhla úspěšně!", category="danger")
            print(form.errors)

    return render_template("blog/user/reservation_page.html", active_page="reservation_page", form=form)
