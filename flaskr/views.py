from flask import Blueprint, render_template, request, jsonify, json, flash, redirect, url_for, session
from flaskr.forms import PersonalInformationForm
from flaskr.db import get_db
from datetime import datetime, timedelta

views = Blueprint("views", __name__)



@views.route('/', methods=["GET", "POST"])
def main_page():
    form = PersonalInformationForm()
    db = get_db()

    #query_result = db.execute('SELECT datum, cas_zacatku FROM Dostupne_hodiny WHERE stav = "volno" ORDER BY datum, cas_zacatku').fetchall()

    query_result_ind = db.execute("""
        SELECT datum, cas_zacatku, COUNT(*) as count
        FROM dostupne_hodiny
        WHERE stav = 'volno' AND typ_hodiny = 'ind'
        GROUP BY datum, cas_zacatku
        ORDER BY datum, cas_zacatku;
    """).fetchall()

    available_times_ind = {}
    for row in query_result_ind:
        date_str = row['datum'].strftime('%Y-%m-%d')
        time_str = row['cas_zacatku'] 
        count = row['count']
        
        if date_str not in available_times_ind:
            available_times_ind[date_str] = []
        
        # Append a tuple of (time, count) for each cas_zacatku
        available_times_ind[date_str].append((time_str, count))

    query_result_group = db.execute("""
        SELECT datum, cas_zacatku, COUNT(*) as count
        FROM dostupne_hodiny
        WHERE stav = 'volno' AND typ_hodiny = 'group'
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

    print("ind")
    print(available_times_ind)

    print("group")
    print(available_times_group)

    query_result_instructors = db.execute("SELECT DISTINCT jmeno, ID_osoba from instruktor")
    available_instructors = [(0, "Instruktor")]
    for row in query_result_instructors:
        available_instructors.append((row["ID_osoba"] ,row["jmeno"]))

    print(available_instructors)

    form.lesson_instructor_choices.choices = available_instructors

    if form.validate_on_submit():
        db = get_db()

        date = form.date.data
        #print("daate from views " + date)
        time_to_split = form.time.data
        time_parts = time_to_split.split(",")
        time = time_parts[0]
        #print("timeform: view: " + time)

        datetime_str = f"{date} {time}:00"

        name = form.name.data
        surname = form.surname.data
        email = form.email.data
        phone = form.tel_number.data
        lesson_type = form.lesson_type.data
        reservation_note = form.note.data
        lesson_length = form.lesson_length.data

        time_str = time

        datetime_obj = datetime.strptime(time_str, '%H:%M')
        datetime_obj_plus_one_hour = datetime_obj + timedelta(hours=1)
        time_plus_one = datetime_obj_plus_one_hour.strftime('%H:%M')

        
        def get_or_create_klient(db, name, surname, email, phone):
            # Step 1: Check if the user already exists
            cursor = db.execute('SELECT ID_osoba FROM klient WHERE email = ?', (email,))
            result = cursor.fetchone()
    
            if result:
                # User exists, return existing ID
                klient_id = result[0]
            else:
                # Step 2: Insert new user since it doesn't exist
                cursor = db.execute('INSERT INTO klient (jmeno, prijmeni, email, tel_cislo) VALUES (?, ?, ?, ?)', (name, surname, email, phone))
                db.commit()  # Commit the insert to make sure the ID is generated
                klient_id = cursor.lastrowid  # Get the newly inserted user's ID
    
            return klient_id

        # Usage example
        klient_id = get_or_create_klient(db, name, surname, email, phone)
        student_count = 0

        cursor = db.execute('INSERT INTO rezervace (ID_osoba, typ_rezervace, termin, doba_vyuky, jazyk, pocet_zaku, poznamka) VALUES (?, ?, ?, ?, ?, ?, ?)', (klient_id, lesson_type, datetime_str , lesson_length, "čeština", student_count, reservation_note))
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
                if client_name_fields[i].data != '':  # Check if field is not empty
                    student_count += 1
                    # Insert each additional student into Zak
                    db.execute('INSERT INTO zak (ID_rezervace, jmeno, prijmeni, zkusenost, vek) VALUES (?, ?, ?, ?, ?)', (reservation_id, client_name_fields[i].data, client_surname_fields[i].data, client_experience_fields[i].data, client_age_fields[i].data))
        
        db.execute('UPDATE rezervace SET pocet_zaku = ? WHERE ID_rezervace = ?', (student_count, reservation_id))

        if lesson_length == "1hodina":
            for student in range(student_count):
                print(student)
                query_result_id_lesson = db.execute('SELECT ID_hodiny FROM dostupne_hodiny WHERE datum = ? AND cas_zacatku = ? AND stav = ?', (date, time, "volno")).fetchone()
                db.execute('UPDATE Dostupne_hodiny SET stav = "obsazeno" WHERE ID_hodiny = ?', (query_result_id_lesson["ID_hodiny"],))
                query_result_id_instructor = db.execute('SELECT ID_osoba FROM ma_vypsane WHERE ID_hodiny = ?', (query_result_id_lesson["ID_hodiny"],)).fetchone()
                db.execute('INSERT INTO ma_vyuku (ID_osoba, ID_rezervace) VALUES (?, ?)', (query_result_id_instructor["ID_osoba"],reservation_id))
                db.execute('INSERT INTO prirazeno (ID_rezervace, ID_hodiny) VALUES (?, ?)', (reservation_id, query_result_id_lesson["ID_hodiny"]))
        else:

            unique_ids = db.execute('SELECT DISTINCT ID_osoba FROM ma_vypsane').fetchall()
            unique_ids = [row['ID_osoba'] for row in unique_ids]
            found = False
            for student in range(student_count):
                for id_osoba in unique_ids:
                    query_result = db.execute('select ID_osoba, ID_hodiny from ma_vypsane left join Dostupne_hodiny using (ID_hodiny) where stav = "volno" and datum = ? and cas_zacatku = ? AND ID_osoba = ? order by ID_osoba', (date, time, id_osoba,)).fetchone()    
                    if query_result is None:
                        continue
                    query_result2 = db.execute('select ID_osoba, ID_hodiny from ma_vypsane left join Dostupne_hodiny using (ID_hodiny) where ID_osoba = ? and datum = ? and cas_zacatku = ?', (id_osoba, date, time_plus_one)).fetchone()        
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
                    break
            if not found:
                flash('No 2 hours lessons', category="danger")
                print("Nothing was found for the given conditions.")  
                return redirect(url_for('views.main_page'))



        db.commit()

        flash('Reservation submitted successfully!', category="success")
        return redirect(url_for('views.main_page'))  # Redi

    return render_template("blog/reservation_page.html", active_page = "reservation_page", form=form,  available_times_ind=json.dumps(available_times_ind), available_times_group=json.dumps(available_times_group))

@views.route('/reservation-check')
def reservation_check():
    return render_template("blog/reservation_check.html")

@views.route('/reservations-user')
def reservations_user():
    return render_template("blog/reservations_user.html")

@views.route('/login-page-admin')
def login_page_admin():
    return render_template("blog/login_admin.html")

@views.route('/admin-page', methods=["GET", "POST"])
def admin_page():
    db = get_db()

    #db.execute('INSERT INTO instruktor (jmeno, prijmeni, email, tel_cislo, seniorita, datum_narozeni, datum_nastupu) VALUES (?, ?, ?, ?, ?, ?, ?)', ("Petr", "Štípek", "petr@stipek.cz", "123456789", "senior", "2001-08-31", "2020-01-01"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-20", "13:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-20", "14:00", "volno", "ind"))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 1))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 2))

    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-21", "16:00", "volno", "ind"))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 3))

    #db.execute('INSERT INTO instruktor (jmeno, prijmeni, email, tel_cislo, seniorita, datum_narozeni, datum_nastupu) VALUES (?, ?, ?, ?, ?, ?, ?)', ("Natálie", "Dlouhá", "Natalie@Dlouha.cz", "111111111", "senior", "2001-03-31", "2020-01-01"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-21", "16:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-21", "17:00", "volno", "ind"))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 4))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 5))

    #db.execute('INSERT INTO instruktor (jmeno, prijmeni, email, tel_cislo, seniorita, datum_narozeni, datum_nastupu) VALUES (?, ?, ?, ?, ?, ?, ?)', ("Lucie", "Krátká", "lucie@kratka.cz", "111111111", "senior", "2005-03-31", "2020-01-01"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-21", "16:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-21", "17:00", "volno", "ind"))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 6))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 7))

    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-22", "16:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-22", "15:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-22", "14:00", "volno", "ind"))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 8))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 9))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 10))

    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-22", "11:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-22", "12:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-22", "13:00", "volno", "ind"))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 11))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 12))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 13))

    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-22", "11:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-22", "11:00", "volno", "ind"))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 12))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 13))

    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "11:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "11:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "11:00", "volno", "ind"))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 16))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 17))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 18))

    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "12:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "12:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "12:00", "volno", "ind"))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 19))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 21))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 20))

    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "19:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "19:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "19:00", "volno", "ind"))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 22))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 23))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 24))


    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "20:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "20:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "20:00", "volno", "ind"))

    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "21:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "21:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "21:00", "volno", "ind"))

    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 25))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 26))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 27))

    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 28))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 29))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 30))

    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "9:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "9:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "9:00", "volno", "ind"))

    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "10:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "10:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "10:00", "volno", "ind"))

    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 37))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 38))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 39))

    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 40))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 41))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 42))

    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "11:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "11:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-23", "11:00", "volno", "ind"))

    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 43))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 44))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (3, 45))

    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-14", "11:00", "volno", "group"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-14", "13:00", "volno", "group"))

    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 92))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 93))


    #db.execute('INSERT INTO instruktor (jmeno, prijmeni, email, tel_cislo, seniorita, datum_narozeni, datum_nastupu) VALUES (?, ?, ?, ?, ?, ?, ?)', ("Petr", "Štípek", "petr@stipek.cz", "123456789", "senior", "2001-08-31", "2020-01-01"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-18", "12:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-19", "13:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-19", "14:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-18", "12:00", "volno", "ind"))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 2))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 3))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 4))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 5))

    #db.execute('INSERT INTO instruktor (jmeno, prijmeni, email, tel_cislo, seniorita, datum_narozeni, datum_nastupu) VALUES (?, ?, ?, ?, ?, ?, ?)', ("Natálie", "Dlouhá", "Natalie@Dlouha.cz", "111111111", "senior", "2001-03-31", "2020-01-01"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-20", "12:00", "volno", "ind"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny) VALUES (?, ?, ?, ?)', ("2024-02-20", "13:00", "volno", "ind"))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 6))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 7))

    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny, obsazenost, kapacita) VALUES (?, ?, ?, ?, ?, ?)', ("2024-02-21", "9:00", "volno", "skup", 0, 10))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny, obsazenost, kapacita) VALUES (?, ?, ?, ?, ?, ?)', ("2024-02-21", "12:00", "volno", "skup", 0, 10))
    
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 8))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 9))

    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 8))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (2, 9))
    
    db.commit()

    return render_template("blog/admin_page.html")

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

@views.route('/reservations-admin')
def reservations_admin():
    return render_template("blog/reservations_admin.html")

@views.route('/instructors')
def instructors_page():
    return render_template("blog/instructors.html", active_page = "instructors")

@views.route('/school')
def school_page():
    return render_template("blog/school.html", active_page = "school")

@views.route('prices')
def prices_page():
    return render_template("blog/prices.html", active_page = "prices")


@views.route('/handle_selection', methods=['POST'])
def handle_selection():
    selected_option = request.json['selectedOption']
    print(selected_option)
    return jsonify({"message": "Option processed successfully"})

@views.route('/get-available-times/<instructor_id>')
def get_available_times(instructor_id):
    db = get_db()
    print(instructor_id)
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
    
    # Return a valid response (modify as needed)
    return jsonify(available_times_ind)

@views.route('/get-available-times/group')
def get_available_times_group():
    db = get_db()

    query_result_group = db.execute("""
        SELECT datum, cas_zacatku, COUNT(*) as count
        FROM dostupne_hodiny
        WHERE stav = 'volno' AND typ_hodiny = 'group'
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