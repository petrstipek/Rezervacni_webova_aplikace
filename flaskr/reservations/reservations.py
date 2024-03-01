from flask import Blueprint, render_template, request, jsonify, json, flash, redirect, url_for, session
from flaskr.forms import PersonalInformationForm, ReservationInformationForm
from flaskr.db import get_db
from datetime import datetime, timedelta
import random, string
from flaskr.extensions import mail
from flask_mail import Message


reservations_bp = Blueprint('reservations', __name__, template_folder='templates')


@reservations_bp.route('/reservation-check')
def reservation_check():
    form = ReservationInformationForm()

    return render_template("blog/user/reservation_check.html", form=form)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=[recipients])
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def generate_unique_reservation_identifier():
    identifier = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    db = get_db()

    query_result = db.execute('SELECT rezervacni_kod FROM rezervace').fetchall()

    existing_identifiers = [row['rezervacni_kod'] for row in query_result]

    while identifier in existing_identifiers:
        identifier = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    return identifier


@reservations_bp.route('/', methods=["GET", "POST"])
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
                if query_result == None:
                    flash('Alert - capacity exceeded', category="danger")
                    print("Nothing was found for the given conditions.")  
                    return redirect(url_for('reservations.main_page'))
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
                        query_result_id_lesson = db.execute('SELECT ID_hodiny FROM dostupne_hodiny WHERE datum = ? AND cas_zacatku = ? AND stav = ? AND typ_hodiny = ?', (date, time, "volno", "ind")).fetchone()
                        if query_result_id_lesson == None:
                            flash('Alert', category="danger")
                            print("Nothing was found for the given conditions.")  
                            return redirect(url_for('reservations.main_page'))
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
                        return redirect(url_for('reservations.main_page'))
                else:
                    #Logic for 1hodina and selected instructor
                    found_number = 0
                    if student_count > 1:
                        flash('cannot have more than one student for one instructor', category="danger")
                        print("Nothing was found for the given conditions.")  
                        return redirect(url_for('reservations.main_page'))
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
                        return redirect(url_for('reservations.main_page'))

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
                        return redirect(url_for('reservations.main_page'))
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
                        return redirect(url_for('reservations.main_page'))

        query_result = db.execute("SELECT rezervacni_kod FROM rezervace WHERE ID_rezervace = ?", (reservation_id,)).fetchone()
        send_email('Rezervace lyžařské hodiny', 'jl6701543@gmail.com', 'felixgrent@gmail.com', 'text body emailu', "Vaše rezervace má ID: "  + query_result["rezervacni_kod"])

        db.commit()

        flash('Reservation submitted successfully!', category="success")
        return redirect(url_for('reservations.main_page'))

    return render_template("blog/user/reservation_page.html", active_page = "reservation_page", form=form)