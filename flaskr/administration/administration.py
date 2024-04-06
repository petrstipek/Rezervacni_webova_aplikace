from flask import Blueprint, render_template, redirect, flash, url_for, request
from flask_login import login_required
from flaskr.forms import InstructorInsertForm, LessonInsertForm, ReservationInformationAdmin, ChangeReservation, LessonChangeForm
from flaskr.administration.services import *
from flaskr.reservations.services import handle_all_instructors
from flaskr.api.services.instructor_services import get_all_instructors
from datetime import datetime
from flaskr.auth.login_decorators import admin_required
from flaskr.administration.services import get_reservation_details
from flaskr.administration.services import process_reservation_change, get_available_lessons, lesson_capacity_change, lesson_instructor_change
from flaskr.api.services.lessons_services import get_lesson_detail

administration_bp = Blueprint('administration', __name__, template_folder='templates')

@administration_bp.route('/reservation-change', methods=["GET", "POST"])
@login_required
@admin_required
def reservation_change():
    form = ChangeReservation()
    
    reservation_id = request.args.get('reservation_id', '') or request.form.get('reservation_id', '')
    form.reservation_id.data = reservation_id
    change_time = form.change_time.data
    
    reservation_details = get_reservation_details(reservation_id)
    available_instructors = get_all_instructors()
    available_instructors = handle_all_instructors(available_instructors)
    form.lesson_instructor_choices.choices = available_instructors

    time_reservation = reservation_details.get('cas_zacatku', '')
    form.time_reservation.choices = [(time_reservation, time_reservation)]

    print("reservation_choices", form.time_reservation.choices)

    if request.method == "POST":
        date_str = form.date.data.strftime('%Y-%m-%d')
        available_lessons = get_available_lessons(date_str)
        choices = [(lesson.cas_zacatku.strftime('%H:%M'), lesson.cas_zacatku.strftime('%H:%M')) for lesson in available_lessons]
        choices.append((time_reservation, time_reservation))
        form.time_reservation.choices = choices
    if form.validate_on_submit():
        result = process_reservation_change(form, reservation_id)

        if len(result) == 3:
            update_success, update_message, reservation_id = result
        elif len(result) == 2:
            update_success, update_message = result

        if update_success:
            flash(update_message, category="success")
            return redirect(url_for('administration.reservation_change', reservation_id=reservation_id))
        else:
            flash(update_message, category="danger")
            #return redirect(url_for('administration.reservation_change', reservation_id=reservation_id))
            return
    else:
        print("form errors: ", form.errors)
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
    
    return render_template('/blog/admin/reservation_change.html', form=form, reservation_code=reservation_details.get("rez_kod"), reservation_date=reservation_details.get("termin_rezervace"), reservation_time=reservation_details.get("cas_zacatku"), reservation_payment=reservation_details.get("platba"), student_count=reservation_details.get("pocet_zaku"), reservation_duration=reservation_details.get("doba_vyuky"), active_page="reservation_change")

@administration_bp.route('/reservations-overview')
@login_required
@admin_required
def reservations_overview():
    return render_template('/blog/admin/reservation_overview.html', active_page="reservations_overview")

@administration_bp.route('/admin-page', methods=["GET", "POST"])
@login_required
@admin_required
def admin_page():
    fig = prepare_data_for_graph()
    graph_html = fig.to_html(full_html=False)
    return render_template("blog/admin/admin_page.html", active_page="admin_page", graph_html=graph_html)

@administration_bp.route('/instructors-admin', methods=["POST", "GET"])
@login_required
@admin_required
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
        password = form.password.data

        text = form.text.data
        file = form.image.data

        changes = False
        instructor = change_instructor_check(email)
        if instructor:
            state, message =  update_instructor(instructor.ID_osoba, form)      
            if state:
                flash(message, category="success")
                changes = True
            else:
                flash(message, category="danger")
                changes = True

        if instructor_exists(email) and changes == False:
            flash("Instruktor již je veden v databázi! V případě změn byla provedena aktualizace.", category="warning")
        elif changes == False:
            add_instructor(name, surname, email, tel_number, experience, date_birth, date_started, password, file, text)
            redirect(url_for("administration.instructors_admin"))
            flash("Instruktor byl úspěšně přidán, můžete vkládat dostupné hodiny.", category="success")
    else:
        print("form errors: ", form.errors)

    instructors_dict = get_all_instructors()
    instructors = [{'full_name': f"{instructor['jmeno']} {instructor['prijmeni']}", 'ID_osoba': instructor['ID_osoba']} for instructor in instructors_dict]
    return render_template("blog/admin/instructors_admin.html", form=form, active_page="instructors_admin")

@administration_bp.route('/lessons-admin', methods=["POST", "GET"])
@login_required
@admin_required
def lessons_admin():
    form_lesson_change = LessonChangeForm()
    form = LessonInsertForm()

    available_instructors = get_available_instructors()
    form.lesson_instructor_choices.choices = available_instructors
    form.lesson_instructor_choices2.choices = available_instructors
    form.lesson_instructor_choices3.choices = available_instructors
    form.lesson_instructor_choices4.choices = available_instructors
    form_lesson_change.instructor.choices = available_instructors

    form_type = request.form.get('form_type')

    if form_type == 'lesson_change' and form_lesson_change.validate_on_submit():
        lesson_id = form_lesson_change.lesson_id.data
        lesson_detail = get_lesson_detail(lesson_id)

        if form_lesson_change.capacity.data and form_lesson_change.capacity.data != 0 and lesson_detail.typ_hodiny == "group":
            if lesson_detail.kapacita != form_lesson_change.capacity.data:
                state, message = lesson_capacity_change(lesson_id, form_lesson_change.capacity.data)
                if state:
                    flash(message, category="success")
                else:
                    flash(message, category="danger")
                return redirect(url_for("administration.lessons_admin", show_modal='true', lesson_id=lesson_id))

            if lesson_detail.kapacita == form_lesson_change.capacity.data:
                flash("Nebyly provedeny žádné změny, zadali jste stejnou kapacitu!", category="warning")
                return redirect(url_for("administration.lessons_admin", show_modal='true', lesson_id=lesson_id))
        elif lesson_detail.typ_hodiny == "group":
            flash("Zadejte prosím validní kapacitu! Rozpětí 1-20.", category="warning")
            return redirect(url_for("administration.lessons_admin", show_modal='true', lesson_id=lesson_id))
    
        if form_lesson_change.instructor.data:
            state, message = lesson_instructor_change(lesson_id, form_lesson_change.instructor.data)
            if state:
                flash(message, category="success")
            else:
                flash(message, category="danger")
        
        return redirect(url_for("administration.lessons_admin", show_modal='true', lesson_id=lesson_id))
    else:
        print("form errors: ", form_lesson_change.errors)

    if form_type == 'lesson_insert' and form.validate_on_submit():
        date = form.date.data
        time_start = form.time_start.data
        lesson_type = form.lesson_type.data
        capacity = form.capacity.data
        instructor_id = form.lesson_instructor_choices.data

        if lesson_type == "group":
            instructor_ids = [form.lesson_instructor_choices.data, form.lesson_instructor_choices2.data, form.lesson_instructor_choices3.data, form.lesson_instructor_choices4.data,]
            instructor_ids = [id for id in instructor_ids if id != "0"]

            if len(instructor_ids) != len(set(instructor_ids)):
                flash("Stejný instruktor je vybrán více krát!", category="danger")
                return redirect(url_for("administration.lessons_admin"))

        date_str = date.strftime("%Y-%m-%d")
        time_obj = datetime.strptime(time_start, '%H:%M').time()

        if lesson_type == "ind":
            success, message = add_individual_lesson(date, time_obj, instructor_id, lesson_type, capacity)
        elif lesson_type == "group":
            success, message = add_group_lesson(date, time_obj, instructor_ids, lesson_type, capacity)

        if success:
            flash(message, category="success")
        else:
            flash(message, category="danger")
    else:
        print("form errors: ", form.errors)

    return render_template("blog/admin/lessons_admin.html", show_modal="false", form=form, active_page="lessons_admin", form_lesson_change=form_lesson_change)

@administration_bp.route('/reservations-admin', methods=["GET", "POST", "DELETE"])
@login_required
@admin_required
def reservations_admin():
    form = ReservationInformationAdmin()
    return render_template("blog/admin/reservation_search.html", form=form, active_page="reservations_admin")
    
@administration_bp.route('/export-data', methods=["GET"])
@login_required
@admin_required
def export_data():
    return render_template("blog/admin/export.html")

@administration_bp.route('/export-instructors', methods=["GET"])
@login_required
@admin_required
def export_instructors():
    response = generate_instructors_data()
    return response

@administration_bp.route('/export-reservations', methods=["GET"])
@login_required
@admin_required
def export_reservations():
    response = generate_reservations_data()
    return response

@administration_bp.route('/export-reservations-overview', methods=["GET"])
@login_required
@admin_required
def export_reservations_overview():
    response = generate_reservations_overview()
    return response

@administration_bp.route('/export-instructors-overview', methods=["GET"])
@login_required
@admin_required
def export_instructors_overview():
    response = generate_instructors_overview()
    return response