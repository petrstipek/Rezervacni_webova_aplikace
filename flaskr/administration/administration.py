from flask import Blueprint, render_template, redirect, flash, url_for, jsonify
from flask_login import login_required
from flaskr.db import get_db
from flaskr.forms import InstructorInsertForm, LessonInsertForm, ReservationInformationAdmin

administration_bp = Blueprint('administration', __name__, template_folder='templates')

@administration_bp.route('/admin-page', methods=["GET", "POST"])
@login_required
def admin_page():
    return render_template("blog/admin/admin_page.html")

@administration_bp.route('/instructors-admin', methods=["POST", "GET"])
@login_required
def instructors_admin():
    form = InstructorInsertForm()
    db = get_db()

    name = form.name.data
    surname = form.surname.data
    tel_number = form.tel_number.data
    email = form.email.data
    experience = form.experience.data
    date_birth = form.date_birth.data
    date_started = form.date_started.data

    if form.validate_on_submit():
        query_result = db.execute('SELECT * FROM Instruktor WHERE email = ?', (email, )).fetchone()
        if query_result:
            flash("instructor already exists", category="danger")
        else:
            db.execute('INSERT INTO Instruktor (jmeno, prijmeni, email, tel_cislo, seniorita, datum_narozeni, datum_nastupu) VALUES (?, ?, ?, ?, ?, ?, ?)', (name, surname, email, tel_number, experience, date_birth, date_started) )
            db.commit()
            redirect(url_for("administration.instructors_admin"))
            flash("instructor added", category="success")

    query_result = db.execute('SELECT * FROM Instruktor').fetchall()

    instructors_dict = [dict(row) for row in query_result]

    return render_template("blog/admin/instructors_admin.html", form=form, instructors_dict=instructors_dict)

@administration_bp.route('/lessons-admin', methods=["POST", "GET"])
@login_required
def lessons_admin():
    form = LessonInsertForm()
    db = get_db()

    query_result_instructors = db.execute("SELECT DISTINCT jmeno, prijmeni, ID_osoba from instruktor")
    available_instructors = [(0, "Instruktor")]
    for row in query_result_instructors:
        available_instructors.append((row["ID_osoba"] ,row["jmeno"] + " " + row["prijmeni"]))

    form.lesson_instructor_choices.choices = available_instructors
    form.lesson_instructor_choices2.choices = available_instructors
    form.lesson_instructor_choices3.choices = available_instructors
    form.lesson_instructor_choices4.choices = available_instructors

    date = form.date.data
    time_start = form.time_start.data
    lesson_type = form.lesson_type.data
    capacity = form.capacity.data
    instructor_id = form.lesson_instructor_choices.data

    instructor_ids = [form.lesson_instructor_choices.data, form.lesson_instructor_choices2.data, form.lesson_instructor_choices3.data, form.lesson_instructor_choices4.data]
    instructor_ids = [id for id in instructor_ids if id != "0"]

    if form.validate_on_submit():
        if len(instructor_ids) != len(set(instructor_ids)):
            flash("one instructor twice in form", category="danger")
            return redirect(url_for("views.lessons_admin"))
        #time_str = time_start.strftime("%H:%M")
        date_str = date.strftime("%Y-%m-%d")
        if lesson_type == "ind":
            query_result = db.execute('SELECT * from Dostupne_hodiny left join ma_vypsane using (ID_hodiny) WHERE datum = ? AND cas_zacatku = ? AND ID_osoba = ?', (date_str, time_start, instructor_id)).fetchone()
            if query_result:
                flash("already lesson for these parametrs", category="danger")
                return redirect(url_for("administration.lessons_admin"))
            cursor = db.execute('INSERT INTO Dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny, kapacita) VALUES (?, ?, ?, ?, ?)', (date_str, time_start, "volno", lesson_type, capacity))
            last_row = cursor.lastrowid
            db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)',(int(instructor_id), last_row))
            db.commit()
            flash("lesson added", category="success")
            redirect(url_for("administration.lessons_admin"))
        elif lesson_type == "group":
            for instructor in instructor_ids:
                query_result = db.execute('SELECT * from Dostupne_hodiny left join ma_vypsane using (ID_hodiny) WHERE datum = ? AND cas_zacatku = ? AND ID_osoba != ?', (date_str, time_start, instructor)).fetchone()
                if query_result:
                    flash("already lesson for these parametrs - instructor: " + instructor, category="danger")
                    return redirect(url_for("views.lessons_admin"))
            cursor = db.execute('INSERT INTO Dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny, kapacita) VALUES (?, ?, ?, ?, ?)', (date_str, time_start, "volno", lesson_type, capacity))
            last_row = cursor.lastrowid
            for instructor in instructor_ids:
                print("instruktor id ", instructor)
                print("last row", last_row)
                db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)',(int(instructor), last_row))
            db.commit()
            flash("lesson added", category="success")
            redirect(url_for("administration.lessons_admin"))

    query_result = db.execute('SELECT * FROM dostupne_hodiny LEFT JOIN ma_vypsane USING (ID_hodiny) left join Instruktor USING (ID_osoba)').fetchall()
    lessons_dict = [dict(row) for row in query_result]

    return render_template("blog/admin/lessons_admin.html", form=form, lessons_dict=lessons_dict)

@administration_bp.route('/reservations-admin', methods=["GET", "POST", "DELETE"])
def reservations_admin():
    db = get_db()
    form = ReservationInformationAdmin()

    query_result = db.execute('SELECT * FROM rezervace left join Klient USING (ID_osoba)').fetchall()
    reservations_dict = [dict(row) for row in query_result]

    if form.validate_on_submit():
        pass
    return render_template("blog/admin/reservations_admin.html", form=form, reservations_dict=reservations_dict)

@administration_bp.route('/mark-reservation-paid/<int:reservation_id>', methods=["POST"])
@login_required
def reservation_payment_status(reservation_id):
    db = get_db()
    reservation = db.execute('SELECT platba FROM rezervace WHERE ID_rezervace = ?', (reservation_id,)).fetchone()

    if not reservation:
        return jsonify({'status': 'error', 'message': 'Rezervace nenalezena!'}), 404
    elif reservation["platba"] == "nezaplaceno":
        db.execute('UPDATE rezervace SET platba = "zaplaceno" WHERE ID_rezervace = ?', (reservation_id,))
        db.commit()
        return jsonify({'status': 'success', 'message': 'Rezervace označena jako zaplacená!'}), 200
    else:
        return jsonify({'status': 'warning', 'message': 'Rezervace již je zaplacena'}), 200