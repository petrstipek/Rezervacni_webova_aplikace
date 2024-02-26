from flask import Blueprint, render_template, request, jsonify, json, flash, redirect, url_for, session
from flaskr.forms import PersonalInformationForm, ReservationInformationForm, LoginForm, InstructorInsertForm, LessonInsertForm, ReservationInformationAdmin
from flaskr.db import get_db
from .email import send_reservation_confirmation
from datetime import datetime, timedelta
import sqlite3
from flask_login import login_user, logout_user, login_required, current_user
from .models import User
from urllib.parse import urlparse
import random, string
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.extensions import login_manager

views = Blueprint("views", __name__)

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user_result = db.execute('SELECT * FROM Spravce_skoly WHERE ID_osoba = ?', (user_id)).fetchone()
    if user_result:
        user = User(user_result['ID_osoba'], user_result['prijmeni'])
        return user
    return None

@views.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.main_page'))

@views.route('/login-page-admin', methods=['GET', 'POST'])
def login_page_admin():
    form = LoginForm()
    if form.validate_on_submit:
        username = form.username.data
        password = form.password.data
        db = get_db()
        query_result = db.execute('SELECT * FROM Spravce_skoly WHERE prihl_jmeno = ?', (username,)).fetchone()
        if query_result and (query_result['heslo'], password):
            user = User(query_result['ID_osoba'], query_result['prihl_jmeno'])
            login_user(user, remember=request.form.get('remember'))
            return redirect(url_for('views.admin_page'))
        else:
            flash("Invalid parametrs")
    return render_template("blog/admin/login_admin.html", form=form)

def generate_unique_reservation_identifier():
    identifier = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    db = get_db()

    query_result = db.execute('SELECT rezervacni_kod FROM rezervace').fetchall()

    existing_identifiers = [row['rezervacni_kod'] for row in query_result]

    while identifier in existing_identifiers:
        identifier = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    return identifier

@views.route('/', methods=["GET", "POST"])
def main_page():
    form = PersonalInformationForm()
    db = get_db()

    #query_result = db.execute('SELECT datum, cas_zacatku FROM Dostupne_hodiny WHERE stav = "volno" ORDER BY datum, cas_zacatku').fetchall()

    query_result_instructors = db.execute("SELECT DISTINCT jmeno, ID_osoba from instruktor")
    available_instructors = [(0, "Instruktor")]
    for row in query_result_instructors:
        available_instructors.append((row["ID_osoba"] ,row["jmeno"]))

    form.lesson_instructor_choices.choices = available_instructors

    if form.validate_on_submit():
        db = get_db()

        date = form.date.data
        time_to_split = form.time.data
        time_parts = time_to_split.split(",")
        time = time_parts[0]

        print(time)

        datetime_str = f"{date} {time}:00"

        name = form.name.data
        surname = form.surname.data
        email = form.email.data
        phone = form.tel_number.data
        lesson_type = form.lesson_type.data
        reservation_note = form.note.data
        lesson_length = form.lesson_length.data
        instructor_selected = form.lesson_instructor_choices.data
        language_selection = form.language_selection.data

        time_str = time

        datetime_obj = datetime.strptime(time_str, '%H:%M')
        datetime_obj_plus_one_hour = datetime_obj + timedelta(hours=1)
        time_plus_one = datetime_obj_plus_one_hour.strftime('%H:%M')

        print("lesson instructor choices")
        print(instructor_selected)

        
        def get_or_create_klient(db, name, surname, email, phone):
            cursor = db.execute('SELECT ID_osoba FROM klient WHERE email = ?', (email,))
            result = cursor.fetchone()
    
            if result:
                klient_id = result[0]
            else:
                cursor = db.execute('INSERT INTO klient (jmeno, prijmeni, email, tel_cislo) VALUES (?, ?, ?, ?)', (name, surname, email, phone))
                db.commit()
                klient_id = cursor.lastrowid
    
            return klient_id

        klient_id = get_or_create_klient(db, name, surname, email, phone)
        student_count = 0
        identifier = generate_unique_reservation_identifier()

        cursor = db.execute('INSERT INTO rezervace (ID_osoba, typ_rezervace, termin, cas_zacatku, doba_vyuky, jazyk, pocet_zaku, platba, rezervacni_kod, poznamka) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (klient_id, lesson_type, date, time , lesson_length, language_selection, student_count, "nezaplaceno", identifier, reservation_note))
        reservation_id = cursor.lastrowid

        if form.student_client.data:
            student_count += 1
            db.execute('INSERT INTO zak (ID_rezervace, jmeno, prijmeni, zkusenost, vek) VALUES (?, ?, ?, ?, ?)', (reservation_id, name, surname, form.experience_client.data, form.age_client.data))
        if form.more_students.data:
            print("vice studentu")
            client_name_fields = [form.name_client1, form.name_client2]
            client_surname_fields = [form.surname_client1, form.surname_client2]
            client_age_fields = [form.age_client1, form.age_client2, form.age_client3]
            client_experience_fields = [form.experience_client1, form.experience_client2]

            for i in range(len(client_name_fields)):
                if client_name_fields[i].data != '':
                    student_count += 1
                    db.execute('INSERT INTO zak (ID_rezervace, jmeno, prijmeni, zkusenost, vek) VALUES (?, ?, ?, ?, ?)', (reservation_id, client_name_fields[i].data, client_surname_fields[i].data, client_experience_fields[i].data, client_age_fields[i].data))
        print("student count",student_count)
        print("lesson type", lesson_type)
        db.execute('UPDATE rezervace SET pocet_zaku = ? WHERE ID_rezervace = ?', (student_count, reservation_id))
        if lesson_type == "group":
            lessons_found = False
            for student in range(student_count):
                query_result = db.execute('SELECT ID_hodiny, ID_osoba, obsazenost, kapacita FROM dostupne_hodiny left join ma_vypsane using (ID_hodiny) WHERE datum = ? AND cas_zacatku = ? AND stav = ? AND typ_hodiny = ? AND obsazenost < kapacita', (date, time, "volno", "group")).fetchone()
                print(query_result["ID_hodiny"])
                if query_result == None:
                    flash('Alert - capacity exceeded', category="danger")
                    print("Nothing was found for the given conditions.")  
                    return redirect(url_for('views.main_page'))
                obsazenost = query_result["obsazenost"] + 1
                db.execute('UPDATE Dostupne_hodiny SET obsazenost = ? WHERE ID_hodiny = ?', (obsazenost, query_result["ID_hodiny"],))
            db.execute('INSERT INTO ma_vyuku (ID_osoba, ID_rezervace) VALUES (?, ?)', (query_result["ID_osoba"],reservation_id))
            db.execute('INSERT INTO prirazeno (ID_rezervace, ID_hodiny) VALUES (?, ?)', (reservation_id, query_result["ID_hodiny"]))
            if query_result["obsazenost"] == query_result["kapacita"]:
                db.execute('UPDATE Dostupne_hodiny SET stav = "obsazeno" WHERE ID_hodiny = ?', (query_result["ID_hodiny"],))

        if lesson_type == "individual":
            if lesson_length == "1hodina":
                if instructor_selected == "0":
                    #Logic for 1hodina and any available instructor
                    found_number = 0
                    for student in range(student_count):
                        print("ted jsem tady - 1hodina 0instruktor")
                        query_result_id_lesson = db.execute('SELECT ID_hodiny FROM dostupne_hodiny WHERE datum = ? AND cas_zacatku = ? AND stav = ? AND typ_hodiny = ?', (date, time, "volno", "ind")).fetchone()
                        if query_result_id_lesson == None:
                            flash('Alert', category="danger")
                            print("Nothing was found for the given conditions.")  
                            return redirect(url_for('views.main_page'))
                        print(query_result_id_lesson["ID_hodiny"])
                        db.execute('UPDATE Dostupne_hodiny SET stav = "obsazeno" WHERE ID_hodiny = ?', (query_result_id_lesson["ID_hodiny"],))
                        query_result_id_instructor = db.execute('SELECT ID_osoba FROM ma_vypsane WHERE ID_hodiny = ?', (query_result_id_lesson["ID_hodiny"],)).fetchone()
                        print("instructor print out", query_result_id_instructor["ID_osoba"])
                        db.execute('INSERT INTO ma_vyuku (ID_osoba, ID_rezervace) VALUES (?, ?)', (query_result_id_instructor["ID_osoba"],reservation_id))
                        db.execute('INSERT INTO prirazeno (ID_rezervace, ID_hodiny) VALUES (?, ?)', (reservation_id, query_result_id_lesson["ID_hodiny"]))
                        found_number += 1
                    if found_number < student_count:
                        flash('Alert', category="danger")
                        print("Nothing was found for the given conditions.")  
                        return redirect(url_for('views.main_page'))
                else:
                    #Logic for 1hodina and selected instructor
                    found_number = 0
                    if student_count > 1:
                        flash('cannot have more than one student for one instructor', category="danger")
                        print("Nothing was found for the given conditions.")  
                        return redirect(url_for('views.main_page'))
                    for student in range(student_count):
                        query_result = db.execute('SELECT ID_hodiny, ID_osoba from dostupne_hodiny left join ma_vypsane using("ID_hodiny") WHERE ID_osoba = ? AND datum = ? AND cas_zacatku = ? and stav = ? AND typ_hodiny = ?', (instructor_selected, date, time, "volno", "ind")).fetchone()
                        #query_result_id_lesson = db.execute('SELECT ID_hodiny FROM dostupne_hodiny WHERE datum = ? AND cas_zacatku = ? AND stav = ?', (date, time, "volno")).fetchone()
                        db.execute('UPDATE Dostupne_hodiny SET stav = "obsazeno" WHERE ID_hodiny = ?', (query_result["ID_hodiny"],))
                        query_result_id_instructor = db.execute('SELECT ID_osoba FROM ma_vypsane WHERE ID_hodiny = ?', (query_result["ID_hodiny"],)).fetchone()
                        db.execute('INSERT INTO ma_vyuku (ID_osoba, ID_rezervace) VALUES (?, ?)', (query_result["ID_osoba"],reservation_id))
                        db.execute('INSERT INTO prirazeno (ID_rezervace, ID_hodiny) VALUES (?, ?)', (reservation_id, query_result["ID_hodiny"]))
                        found_number += 1
                    if found_number < student_count:
                        flash('No 2 hours lessons', category="danger")
                        print("Nothing was found for the given conditions.")  
                        return redirect(url_for('views.main_page'))

            else:
                if instructor_selected == "0":
                    unique_ids = db.execute('SELECT DISTINCT ID_osoba FROM ma_vypsane').fetchall()
                    unique_ids = [row['ID_osoba'] for row in unique_ids]
                    found = False
                    found_number = 0
                    for student in range(student_count):
                        for id_osoba in unique_ids:
                            query_result = db.execute('select ID_osoba, ID_hodiny from ma_vypsane left join Dostupne_hodiny using (ID_hodiny) where stav = "volno" and datum = ? and cas_zacatku = ? AND ID_osoba = ? AND typ_hodiny = ? order by ID_osoba', (date, time, id_osoba, "ind")).fetchone()    
                            if query_result is None:
                                continue
                            query_result2 = db.execute('select ID_osoba, ID_hodiny from ma_vypsane left join Dostupne_hodiny using (ID_hodiny) where ID_osoba = ? and datum = ? and cas_zacatku = ? AND typ_hodiny = ?', (id_osoba, date, time_plus_one, "ind")).fetchone()        
                            if query_result2 is None:
                                continue
                            found = True
                            id_instructor = query_result["ID_osoba"]
                            id_lessons = (query_result["ID_hodiny"], query_result2["ID_hodiny"])

                            db.execute('UPDATE Dostupne_hodiny SET stav = "obsazeno" WHERE ID_hodiny = ?', (id_lessons[0],))
                            db.execute('UPDATE Dostupne_hodiny SET stav = "obsazeno" WHERE ID_hodiny = ?', (id_lessons[1],))
                            db.execute('INSERT INTO ma_vyuku (ID_osoba, ID_rezervace) VALUES (?, ?)', (id_instructor,reservation_id))
                            db.execute('INSERT INTO prirazeno (ID_rezervace, ID_hodiny) VALUES (?, ?)', (reservation_id, id_lessons[0]))
                            db.execute('INSERT INTO prirazeno (ID_rezervace, ID_hodiny) VALUES (?, ?)', (reservation_id, id_lessons[1]))
                            found_number += 1
                            break
                    if not found or found_number < (student_count) :
                        flash('No 2 hours lessons', category="danger")
                        print("Nothing was found for the given conditions.")
                        return redirect(url_for('views.main_page'))
                else:
                    print("selected instructor not 0")
                    found = False
                    found_number = 0
                    for student in range(student_count):
                        for i in range(2):
                            query_result = db.execute('select ID_osoba, ID_hodiny from ma_vypsane left join Dostupne_hodiny using (ID_hodiny) where stav = "volno" and datum = ? and cas_zacatku = ? AND ID_osoba = ? AND typ_hodiny = ? order by ID_osoba', (date, time, instructor_selected, "ind")).fetchone()    
                            if query_result is None:
                                continue
                            query_result2 = db.execute('select ID_osoba, ID_hodiny from ma_vypsane left join Dostupne_hodiny using (ID_hodiny) where ID_osoba = ? and datum = ? and cas_zacatku = ? AND typ_hodiny = ?', (instructor_selected, date, time_plus_one, "ind")).fetchone()        
                            if query_result2 is None:
                                continue
                            found = True
                            id_instructor = query_result["ID_osoba"]
                            id_lessons = (query_result["ID_hodiny"], query_result2["ID_hodiny"])

                            db.execute('UPDATE Dostupne_hodiny SET stav = "obsazeno" WHERE ID_hodiny = ?', (id_lessons[0],))
                            db.execute('UPDATE Dostupne_hodiny SET stav = "obsazeno" WHERE ID_hodiny = ?', (id_lessons[1],))
                            db.execute('INSERT INTO ma_vyuku (ID_osoba, ID_rezervace) VALUES (?, ?)', (id_instructor,reservation_id))
                            db.execute('INSERT INTO prirazeno (ID_rezervace, ID_hodiny) VALUES (?, ?)', (reservation_id, id_lessons[0]))
                            db.execute('INSERT INTO prirazeno (ID_rezervace, ID_hodiny) VALUES (?, ?)', (reservation_id, id_lessons[1]))
                            found_number += 1
                            break
                    if not found or found_number < (student_count):
                        flash('No 2 hours lessons', category="danger")
                        print("Nothing was found for the given conditions.")  
                        return redirect(url_for('views.main_page'))

        user_email = "felixgrent@gmail.com"  # Example user email
        reservation_details = "haha email funguje"
    
        # Send confirmation email
        #send_reservation_confirmation(user_email, reservation_details)

        db.commit()

        flash('Reservation submitted successfully!', category="success")
        return redirect(url_for('views.main_page'))  # Redi

    return render_template("blog/user/reservation_page.html", active_page = "reservation_page", form=form)

@views.route('/reservation-check')
def reservation_check():
    form = ReservationInformationForm()

    return render_template("blog/user/reservation_check.html", form=form)

@views.route('/reservations-user')
def reservations_user():
    return render_template("blog/reservations_user.html")


@views.route('/admin-page', methods=["GET", "POST"])
@login_required
def admin_page():
    db = get_db()

    db.execute('INSERT INTO Spravce_skoly (jmeno, prijmeni, email, tel_cislo, prihl_jmeno, heslo) VALUES (?, ?, ?, ?, ?, ?)', ("Ředitel", "Dlouhý", "reditel@dlouhy.cz", "123456789", "reditel", "reditel123"))
    #db.execute('INSERT INTO instruktor (jmeno, prijmeni, email, tel_cislo, seniorita, datum_narozeni, datum_nastupu) VALUES (?, ?, ?, ?, ?, ?, ?)', ("Petr", "Štípek", "petr@stipek.cz", "123456789", "senior", "2001-08-31", "2020-01-01"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-21", "13:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-21", "14:00", "volno", "ind"))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 1))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 2))

    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny, obsazenost, kapacita) VALUES (?, ?, ?, ?, ?, ?)', ("2024-02-11", "10:00", "volno", "group", 0, 10))
    
    #db.execute('INSERT INTO instruktor (jmeno, prijmeni, email, tel_cislo, seniorita, datum_narozeni, datum_nastupu) VALUES (?, ?, ?, ?, ?, ?, ?)', ("Natálie", "Dlouhá", "Natalie@Dlouha.cz", "111111111", "senior", "2001-03-31", "2020-01-01"))
    
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-13", "10:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-13", "11:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-12", "12:00", "volno", "ind"))

    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 1))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 2))

    db.commit()

    return render_template("blog/admin/admin_page.html")

@views.route('/lectures')
def lectures():
    db = get_db()

    unique_ids = db.execute('SELECT DISTINCT ID_osoba FROM ma_vypsane').fetchall()
    unique_ids = [row['ID_osoba'] for row in unique_ids]

    found = False
    for id_osoba in unique_ids:
        query_result = db.execute('select ID_osoba, ID_hodiny from ma_vypsane left join Dostupne_hodiny using (ID_hodiny) where stav = "volno" and datum = "2024-02-21" and cas_zacatku = "16:00" AND ID_osoba = ? order by ID_osoba', (id_osoba,)).fetchone()    
        if query_result == None:
            continue
        
        query_result2 = db.execute('select ID_osoba, ID_hodiny from ma_vypsane left  join Dostupne_hodiny using (ID_hodiny) where ID_osoba = ? and datum = "2024-02-21" and cas_zacatku = "17:00"', (id_osoba,)).fetchone()        
        if query_result2 == None:
            continue
        found = True
        id_instructor = query_result["ID_osoba"]
        id_lessons = (query_result["ID_hodiny"], query_result2["ID_hodiny"])
        print("id found ")
        print("id osoby")
        print(id_instructor)
        print("ID dostupne hodiny")
        print(id_lessons[0])
        print(id_lessons[1])
        break
    if not found:
        print("Nothing was found for the given conditions.")           

    #print("query result")
    #query_result = db.execute('select ID_osoba from ma_vypsane left join Dostupne_hodiny using (ID_hodiny) where stav = "volno" and datum = "2024-02-19" and cas_zacatku = "13:00" order by ID_osoba').fetchone()
    #print(query_result["ID_osoba"])
    #query_resutl2 = db.execute('select * from ma_vypsane left  join Dostupne_hodiny using (ID_hodiny) where ID_osoba = 1 and cas_zacatku = "14:00"').fetchone()

    return render_template("blog/lectures.html")

@views.route('/instructors-admin', methods=["POST", "GET"])
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
            redirect(url_for("views.instructors_admin"))
            flash("instructor added", category="success")

    query_result = db.execute('SELECT * FROM Instruktor').fetchall()

    instructors_dict = [dict(row) for row in query_result]

    return render_template("blog/admin/instructors_admin.html", form=form, instructors_dict=instructors_dict)

@views.route('/delete_instructor_admin/<int:instructor_id>', methods=["POST"])
def delete_instructor_admin(instructor_id):
    db = get_db()

    query_result = db.execute('SELECT * from ma_vyuku WHERE ID_osoba = ?', (instructor_id,))
    if query_result:
        flash("instructor has occupied lessons", category="danger")
        return redirect(url_for("views.instructors_admin"))

    db.execute('DELETE FROM Instruktor WHERE ID_osoba = ?', (instructor_id,))
    db.commit()

    return redirect(url_for("views.instructors_admin"))

@views.route('/lessons-admin', methods=["POST", "GET"])
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
                return redirect(url_for("views.lessons_admin"))
            cursor = db.execute('INSERT INTO Dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny, kapacita) VALUES (?, ?, ?, ?, ?)', (date_str, time_start, "volno", lesson_type, capacity))
            last_row = cursor.lastrowid
            db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)',(int(instructor_id), last_row))
            db.commit()
            flash("lesson added", category="success")
            redirect(url_for("views.lessons_admin"))
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
            redirect(url_for("views.lessons_admin"))

    query_result = db.execute('SELECT * FROM dostupne_hodiny LEFT JOIN ma_vypsane USING (ID_hodiny) left join Instruktor USING (ID_osoba)').fetchall()
    lessons_dict = [dict(row) for row in query_result]

    return render_template("blog/admin/lessons_admin.html", form=form, lessons_dict=lessons_dict)

@views.route('/delete_lesson_admin/<int:lesson_id>', methods=["POST"])
def delete_lesson_admin(lesson_id):
    db = get_db()
    print("jsem tady v lesson delte")
    print(type(lesson_id))

    try:
        query_result = db.execute('SELECT stav FROM dostupne_hodiny WHERE ID_hodiny = ?', (lesson_id,)).fetchone()

        if query_result and query_result["stav"] == "obsazeno":
            #flash("Hodina je obsazene, nelze proto smazat", category="danger")
            return jsonify({"error": True, "message": "Hodina je obsazene, nelze proto smazat"}), 400
        else:
            db.execute('DELETE FROM dostupne_hodiny WHERE ID_hodiny = ?', (lesson_id,))
            db.execute('DELETE FROM ma_vypsane WHERE ID_hodiny = ?', (lesson_id,))
            db.commit()
            #flash("Dostupná hodina byla úspěšně smazána!", category="success")
            return jsonify({"success": True, "message": "Dostupná hodina byla úspěšně smazána!"})
    except Exception as e:
        #flash("Error", category="danger")
        return jsonify({"error": True, "message": "An error occurred. Please try again."}), 500
    #return jsonify({"success": True, "message": "Dostupná hodina byla úspěšně smazána!"})

@views.route('/reservations-admin', methods=["GET", "POST", "DELETE"])
def reservations_admin():
    db = get_db()
    form = ReservationInformationAdmin()

    query_result = db.execute('SELECT * FROM rezervace left join Klient USING (ID_osoba)').fetchall()
    reservations_dict = [dict(row) for row in query_result]

    if form.validate_on_submit():
        pass


    return render_template("blog/admin/reservations_admin.html", form=form, reservations_dict=reservations_dict)

@views.route('/handle_selection', methods=['POST'])
def handle_selection():
    selected_option = request.json['selectedOption']
    print(selected_option)
    return jsonify({"message": "Option processed successfully"})

@views.route('/get-available-times/<instructor_id>')
def get_available_times(instructor_id):
    db = get_db()
    query_resuslt_instructor_times = db.execute('select datum, cas_zacatku from dostupne_hodiny left join ma_vypsane using (ID_hodiny) where stav="volno" and typ_hodiny="ind" and ID_osoba= ? order by datum, cas_zacatku', (instructor_id))
    
    available_times_instructor = {}

    for row in query_resuslt_instructor_times:
        date_str = row['datum'].strftime('%Y-%m-%d')
        time_str = row['cas_zacatku']

        if date_str not in available_times_instructor:
            available_times_instructor[date_str] = []

        available_times_instructor[date_str].append((time_str))
    
    print(available_times_instructor)
    return json.dumps(available_times_instructor)

@views.route('/get-available-times/individual/<int:instructor_id>')
def get_available_times_individual_instructor(instructor_id):
    db = get_db()
    base_query = """
        SELECT datum, cas_zacatku, COUNT(*) as count
        FROM dostupne_hodiny LEFT JOIN ma_vypsane USING (ID_hodiny)
        WHERE stav = 'volno' AND typ_hodiny = 'ind'
    """
    
    if instructor_id != 0:
        base_query += " AND ID_osoba = ?"
        query_parameters = (instructor_id,)
        query_result_ind = db.execute(base_query + " GROUP BY datum, cas_zacatku ORDER BY datum, cas_zacatku", query_parameters).fetchall()
    else:
        query_result_ind = db.execute(base_query + " GROUP BY datum, cas_zacatku ORDER BY datum, cas_zacatku").fetchall()
    
    available_times_ind = {}
    for row in query_result_ind:
        date_str = row['datum'].strftime('%Y-%m-%d')
        time_str = row['cas_zacatku']
        count = row['count']
        
        if date_str not in available_times_ind:
            available_times_ind[date_str] = []
        
        available_times_ind[date_str].append((time_str, count))
    
    return jsonify(available_times_ind)

@views.route('/get-available-times/group')
def get_available_times_group():
    db = get_db()

    query_result_group = db.execute("""
        SELECT datum, cas_zacatku, (kapacita - obsazenost) as count
        FROM dostupne_hodiny
        WHERE stav = 'volno' AND typ_hodiny = 'group' AND obsazenost < kapacita
        GROUP BY datum, cas_zacatku
        ORDER BY datum, cas_zacatku;
    """).fetchall()

    available_times_group = {}

    for row in query_result_group:
        date_str = row['datum'].strftime('%Y-%m-%d')
        time_str = row['cas_zacatku'] 
        count = row['count']

        if date_str not in available_times_group:
            available_times_group[date_str] = []

        available_times_group[date_str].append((time_str, count))

    return jsonify(available_times_group)

@views.route('/get-reservation-details/<reservation_identifiers>', defaults={'identifier': None})
@views.route('/get-reservation-details/<reservation_identifiers>/<identifier>')
def get_reservation_details(reservation_identifiers, identifier):
    db = get_db()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    
    def query_db_and_construct_response(sql_query, params):
        offset = (page - 1) * per_page
        
        paginated_sql_query = f"{sql_query} LIMIT ? OFFSET ?"
        paginated_params = params + (per_page, offset)

        query_result = db.execute(paginated_sql_query, paginated_params).fetchall()
        
        if query_result:
            columns = ["ID_rezervace", "ID_osoba", "typ_rezervace", "termin", "platba", "cas_zacatku", "doba_vyuky", "jazyk", "pocet_zaku"]
            results_list = [{column: row[i] for i, column in enumerate(columns)} for row in query_result]
            
            count_sql_query = f"SELECT COUNT(*) FROM ({sql_query})"
            total_items = db.execute(count_sql_query, params).fetchone()[0]
            total_pages = (total_items + per_page - 1) // per_page
            
            return jsonify({
                "reservations": results_list,
                "total_items": total_items,
                "total_pages": total_pages,
                "current_page": page
            })
        else:
            return jsonify({"error": "No reservations found"}), 404

    query_map = {
        "reservationID": ("SELECT * FROM rezervace WHERE rezervacni_kod = ?", (identifier,)),
        "name": ("SELECT * FROM rezervace LEFT JOIN Klient USING (ID_osoba) WHERE prijmeni = ?", (identifier,)),
        "email": ("SELECT * FROM rezervace LEFT JOIN Klient USING (ID_osoba) WHERE email = ?", (identifier,)),
        "tel-number": ("SELECT * FROM rezervace LEFT JOIN Klient USING (ID_osoba) WHERE tel_cislo = ?", (identifier,)),
        "all": ("SELECT * FROM rezervace LEFT JOIN Klient USING (ID_osoba)", ())
    }

    if reservation_identifiers in query_map:
        sql_query, params = query_map[reservation_identifiers]
        return query_db_and_construct_response(sql_query, params)
    else:
        return jsonify({"error": "Invalid reservation identifier"}), 400

@views.route('/mark-reservation-paid/<int:reservation_id>', methods=["POST"])
def reservation_payment_status(reservation_id):
    db = get_db()
    reservation = db.execute('SELECT platba FROM rezervace WHERE ID_rezervace = ?', (reservation_id,)).fetchone()

    if not reservation:
        flash("Rezervace nenalezena!", category="danger")
    elif reservation["platba"] == "nezaplaceno":
        db.execute('UPDATE rezervace SET platba = "zaplaceno" WHERE ID_rezervace = ?', (reservation_id,))
        db.commit()
        flash("Rezervace označena jako zaplacená!", category="success")
    else:
        flash("Rezervace již je zaplacena", category="warning")

    return redirect(url_for("views.reservations_admin"))
    
@views.route('/delete-reservation/<reservation_id>', methods=['DELETE', 'POST'])
def delete_reservation(reservation_id):
    db = get_db()
    cur = db.cursor()

    referer_url = request.headers.get('Referer', 'default_fallback_url')
    parsed_url = urlparse(referer_url)
    path = parsed_url.path
    last_part_url = path.strip('/').split('/')[-1]

    try:   
        lessons_ids = db.execute("SELECT ID_hodiny from prirazeno WHERE ID_rezervace = ?", (reservation_id)).fetchall()
        
        for lesson_id_tuple in lessons_ids:
            lesson_id = lesson_id_tuple[0]
            cur.execute("UPDATE Dostupne_hodiny SET stav = 'volno' WHERE ID_hodiny = ?", (lesson_id,))

        cur.execute("DELETE FROM rezervace WHERE ID_rezervace = ?", (reservation_id,))
        db.execute("DELETE from prirazeno WHERE ID_rezervace = ?", (reservation_id))
        db.execute("DELETE from ma_vyuku WHERE ID_rezervace = ?", (reservation_id))
        db.commit()

        if cur.rowcount > 0:
            response = {"message": "Reservation deleted successfully"}
            status_code = 200
        else:
            response = {"error": "Reservation not found"}
            status_code = 404
    except sqlite3.Error as e:
        response = {"error": str(e)}
        status_code = 500
    
    if last_part_url == "reservations-admin":
        flash("Dostupná hodina byla úspěšně smazána!", category="success")
        return redirect(url_for("views.reservations_admin"))
    else:
        return jsonify(response), status_code

@views.route('/instructors')
def instructors_page():
    return render_template("blog/instructors.html", active_page = "instructors")

@views.route('/school')
def school_page():
    return render_template("blog/school.html", active_page = "school")

@views.route('prices')
def prices_page():
    return render_template("blog/prices.html", active_page = "prices")

@views.route('/get-lessons')
def get_lessons():
    db = get_db()

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 1, type=int)
    selected_date = request.args.get('date', None)

    if selected_date:
        query_result = db.execute('SELECT ID_hodiny, datum, cas_zacatku, prijmeni, stav, typ_hodiny, obsazenost FROM dostupne_hodiny LEFT JOIN ma_vypsane USING (ID_hodiny) left join Instruktor USING (ID_osoba) WHERE datum = ? LIMIT ? OFFSET ?', (selected_date, per_page, (page - 1) * per_page)).fetchall()
        total = db.execute('SELECT COUNT(*) FROM dostupne_hodiny WHERE datum = ?', (selected_date,)).fetchone()[0]
    else:
        query_result = db.execute('SELECT ID_hodiny, datum, cas_zacatku, prijmeni, stav, typ_hodiny, obsazenost FROM dostupne_hodiny LEFT JOIN ma_vypsane USING (ID_hodiny) left join Instruktor USING (ID_osoba) LIMIT ? OFFSET ?', (per_page, (page - 1) * per_page)).fetchall()
        total = db.execute('SELECT COUNT(*) FROM dostupne_hodiny').fetchone()[0]

    lessons_dict = [dict(row) for row in query_result]

    return jsonify({
        'lessons': lessons_dict,
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'current_page': page
    })