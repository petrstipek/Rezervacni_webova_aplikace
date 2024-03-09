from flask import Blueprint, render_template, redirect, flash, url_for, jsonify
from flask_login import login_required
from flaskr.db import get_db
from flaskr.forms import InstructorInsertForm, LessonInsertForm, ReservationInformationAdmin
from flaskr.administration.services import *
from flaskr.api.services.instructor_services import get_all_instructors
from datetime import datetime

administration_bp = Blueprint('administration', __name__, template_folder='templates')

@administration_bp.route('/admin-page', methods=["GET", "POST"])
@login_required
def admin_page():
    return render_template("blog/admin/admin_page.html")

@administration_bp.route('/instructors-admin', methods=["POST", "GET"])
@login_required
def instructors_admin():
    form = InstructorInsertForm()

    if form.validate_on_submit():
        name = form.name.data
        surname = form.surname.data
        tel_number = form.tel_number.data
        email = form.email.data
        experience = form.experience.data
        date_birth = form.date_birth.data
        date_started = form.date_started.data

        if instructor_exists(email):
            flash("instructor already exists", category="danger")
        else:
            add_instructor(name, surname, email, tel_number, experience, date_birth, date_started)
            redirect(url_for("administration.instructors_admin"))
            flash("instructor added", category="success")

    instructors_dict = get_all_instructors()

    return render_template("blog/admin/instructors_admin.html", form=form, instructors_dict=instructors_dict, active_page="instructors_admin")

@administration_bp.route('/lessons-admin', methods=["POST", "GET"])
@login_required
def lessons_admin():
    form = LessonInsertForm()
    db = get_db()

    available_instructors = get_available_instructors()
    form.lesson_instructor_choices.choices = available_instructors
    form.lesson_instructor_choices2.choices = available_instructors
    form.lesson_instructor_choices3.choices = available_instructors
    form.lesson_instructor_choices4.choices = available_instructors

    if form.validate_on_submit():
        date = form.date.data
        time_start = form.time_start.data
        lesson_type = form.lesson_type.data
        capacity = form.capacity.data
        instructor_id = form.lesson_instructor_choices.data

        if lesson_type == "group":
            instructor_ids = [form.lesson_instructor_choices.data, form.lesson_instructor_choices2.data, form.lesson_instructor_choices3.data, form.lesson_instructor_choices4.data]
            instructor_ids = [id for id in instructor_ids if id != "0"]

            if len(instructor_ids) != len(set(instructor_ids)):
                flash("One instructor selected multiple times in the form", category="danger")
                return redirect(url_for("administration.lessons_admin"))

        date_str = date.strftime("%Y-%m-%d")
        time_obj = datetime.strptime(time_start, '%H:%M').time()

        if lesson_type == "ind":
            success, message = add_individual_lesson(db, date, time_obj, instructor_id, lesson_type, capacity)
        elif lesson_type == "group":
            success, message = add_group_lesson(db, date, time_obj, instructor_ids, lesson_type, capacity)

        if success:
            flash(message, category="success")
        else:
            flash(message, category="danger")

    #lessons_dict = get_all_lessons()

    return render_template("blog/admin/lessons_admin.html", form=form, active_page="lessons_admin")

@administration_bp.route('/reservations-admin', methods=["GET", "POST", "DELETE"])
@login_required
def reservations_admin():
    form = ReservationInformationAdmin()
    #reservations_dict = get_reservations()
    return render_template("blog/admin/reservations_admin.html", form=form, active_page="reservations_admin")

@administration_bp.route('/mark-reservation-paid/<int:reservation_id>', methods=["POST"])
@login_required
def reservation_payment_status(reservation_id):
    try:
        reservation = get_reservation_payment_status(reservation_id)

        if not reservation:
            return jsonify({'status': 'error', 'message': 'Rezervace nenalezena!'}), 404
        payment_status = reservation[0]
        if payment_status == "nezaplaceno":
            mark_reservation_as_paid(reservation_id)
            return jsonify({'status': 'success', 'message': 'Rezervace označena jako zaplacená!'}), 200
        elif payment_status == "zaplaceno":
            return jsonify({'status': 'warning', 'message': 'Rezervace již je zaplacena'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Error!'}), 500
    
@administration_bp.route('/delete_lesson_admin/<int:lesson_id>', methods=["POST"])
@login_required
def delete_lesson_admin(lesson_id):
    try:
        lesson_status = get_lesson_status(lesson_id)
        if lesson_status and lesson_status[0] == "obsazeno":
            return jsonify({"error": True, "message": "Hodina je obsazena, nelze smazat, nejdřív smažte rezervaci."}), 400
        elif lesson_status and lesson_status[0] == "volno":
            delete_lesson(lesson_id)
            return jsonify({"success": True, "message": "Dostupná hodina byla úspěšně smazána!"})
    except Exception as e:
        return jsonify({"error": True, "message": "Nastala chyba."}), 500