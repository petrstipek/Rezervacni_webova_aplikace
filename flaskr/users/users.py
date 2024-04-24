from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required
from flaskr.auth.login_decorators import client_required
from flaskr.forms import PersonalInformationFormUser, ChangeReservation
from flask_login import current_user
from flaskr.users.users_services import validate_password, update_personal_information, get_reservation_students_status
from flaskr.api.services.instructor_services import get_all_instructors
from flaskr.administration.services import get_reservation_details
from flaskr.reservations.services import handle_all_instructors
from datetime import datetime
from flaskr.administration.services import process_reservation_change, get_available_lessons
import json

users_bp = Blueprint('users', __name__, template_folder='templates')

@users_bp.route('/reservation-change', methods=["GET", "POST"])
@login_required
@client_required
def reservation_change():
    form = ChangeReservation()
    
    reservation_id = request.args.get('reservation_id', '') or request.form.get('reservation_id', '')
    form.reservation_id.data = reservation_id
    
    reservation_details = get_reservation_details(reservation_id)
    available_instructors = get_all_instructors()
    available_instructors = handle_all_instructors(available_instructors)
    form.lesson_instructor_choices.choices = available_instructors

    time_reservation = reservation_details.get('cas_zacatku', '')
    form.time_reservation.choices = [(time_reservation, time_reservation)]

    if request.method == "POST":
        available_lessons = get_available_lessons(form.date.data)
        form.time_reservation.choices = [(lesson.cas_zacatku.strftime('%H:%M'), lesson.cas_zacatku.strftime('%H:%M')) for lesson in available_lessons]

    if form.validate_on_submit():
        result = process_reservation_change(form, reservation_id)


        if len(result) == 3:
            update_success, update_message, reservation_id = result
        elif len(result) == 2:
            update_success, update_message = result

        if update_success:
            flash(update_message, category="success")
            return redirect(url_for('users.reservation_change', reservation_id=reservation_id))
        else:
            flash(update_message, category="danger")
            return redirect(url_for('users.reservation_change', reservation_id=reservation_id))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{error}", category="danger")

    if request.method == "GET" and reservation_details:
        form.name.data = reservation_details.get('jmeno_klienta', '')
        form.surname.data = reservation_details.get('prijmeni_klienta', '')
        form.email.data = reservation_details.get('email_klienta', '')
        form.tel_number.data = reservation_details.get('tel_cislo_klienta', '')
        form.age_client.data = reservation_details['Zak'][0].get('vek_zak', '')
        form.experience_client.data = reservation_details['Zak'][0].get('zkusenost_zak', '')

        date_str = reservation_details.get('termin_rezervace', '')
        form.date.data = datetime.strptime(date_str, '%Y-%m-%d').date()

        time_reservation = reservation_details.get('cas_zacatku', '')
        form.time_reservation.choices = [(time_reservation, time_reservation)]

        if reservation_details['Zak'] and len(reservation_details['Zak']) > 1:
            form.name_client1.data = reservation_details['Zak'][1].get('jmeno_zak', '')
            form.surname_client1.data = reservation_details['Zak'][1].get('prijmeni_zak', '')
            form.age_client1.data = reservation_details['Zak'][1].get('vek_zak', '')
            form.experience_client1.data = reservation_details['Zak'][1].get('zkusenost_zak', '')

        if len(reservation_details['Zak']) > 2:
            form.name_client2.data = reservation_details['Zak'][2].get('jmeno_zak', '')
            form.surname_client2.data = reservation_details['Zak'][2].get('prijmeni_zak', '')
            form.age_client2.data = reservation_details['Zak'][2].get('vek_zak', '')
            form.experience_client2.data = reservation_details['Zak'][2].get('zkusenost_zak', '')

        student_client, students_status = get_reservation_students_status(reservation_id)
        student_client = json.dumps(student_client)
        students_status = json.dumps(students_status)
    
    return render_template('/blog/user/reservation_change.html', form=form, student_client=student_client, students_status=students_status, reservation_code=reservation_details.get("rez_kod"), reservation_date=reservation_details.get("termin_rezervace"), reservation_time=reservation_details.get("cas_zacatku"), reservation_payment=reservation_details.get("platba"), student_count=reservation_details.get("pocet_zaku"), reservation_duration=reservation_details.get("doba_vyuky"), active_page="reservation_change")

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