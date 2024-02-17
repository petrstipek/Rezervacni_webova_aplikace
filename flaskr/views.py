from flask import Blueprint, render_template, request, jsonify, json, flash, redirect, url_for
from flaskr.forms import PersonalInformationForm
from flaskr.db import get_db

views = Blueprint("views", __name__)


@views.route('/', methods=["GET", "POST"])
def main_page():
    db = get_db()

    query_result = db.execute('SELECT datum, cas_zacatku FROM Dostupne_hodiny WHERE stav = "volno" ORDER BY datum, cas_zacatku').fetchall()

    # Organize the fetched times by date
    available_times = {}
    for row in query_result:
        date_str = row['datum'].strftime('%Y-%m-%d')  # Assuming 'datum' is a date object
        if date_str not in available_times:
            available_times[date_str] = []
        available_times[date_str].append(row['cas_zacatku'])  # Assuming 'cas_zacatku' is a time object

    form = PersonalInformationForm()

    if form.validate_on_submit():
        db = get_db()

        date = form.date.data
        #print("daate from views " + date)
        time = form.time.data
        #print("timeform: view: " + time)

        datetime_str = f"{date} {time}:00"

        name = form.name.data
        surname = form.surname.data
        email = form.email.data
        phone = form.tel_number.data
        lesson_type = form.lesson_type.data
        reservation_note = form.note.data


        
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

        cursor = db.execute('INSERT INTO rezervace (ID_osoba, typ_rezervace, termin, doba_vyuky, jazyk, pocet_zaku, poznamka) VALUES (?, ?, ?, ?, ?, ?, ?)', (klient_id, lesson_type, datetime_str , 1, "čeština", student_count, reservation_note))
        reservation_id = cursor.lastrowid

        query_result_id_lesson = db.execute('SELECT ID_hodiny FROM dostupne_hodiny WHERE datum = ? AND cas_zacatku = ?', (date, time)).fetchone()
        db.execute('UPDATE Dostupne_hodiny SET stav = "obsazeno" WHERE ID_hodiny = ?', (query_result_id_lesson["ID_hodiny"],))
        query_result_id_instructor = db.execute('SELECT ID_osoba FROM ma_vypsane WHERE ID_hodiny = ?', (query_result_id_lesson["ID_hodiny"],)).fetchone()
        db.execute('INSERT INTO ma_vyuku (ID_osoba, ID_rezervace) VALUES (?, ?)', (query_result_id_instructor["ID_osoba"],reservation_id))
    

        if form.student_client.data:
            student_count += 1
            db.execute('INSERT INTO zak (ID_rezervace, jmeno, prijmeni, zkusenost, vek) VALUES (?, ?, ?, ?, ?)', (reservation_id, name, surname, form.experience_client.data, form.age_client.data))
        if form.more_students.data:
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
        db.commit()

        flash('Reservation submitted successfully!', 'success')
        return redirect(url_for('views.main_page'))  # Redi

    return render_template("blog/reservation_page.html", active_page = "reservation_page", form=form,  available_times=json.dumps(available_times))

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
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav) VALUES (?, ?, ?)', ("2024-02-18", "12:00", "volno"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav) VALUES (?, ?, ?)', ("2024-02-19", "13:00", "volno"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav) VALUES (?, ?, ?)', ("2024-02-19", "13:00", "volno"))
    #db.execute('INSERT INTO dostupne_hodiny (datum, cas_zacatku, stav) VALUES (?, ?, ?)', ("2024-02-19", "14:00", "volno"))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 2))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 3))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 4))
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)', (1, 5))

    db.commit()

    return render_template("blog/admin_page.html")

@views.route('/lectures')
def lectures():
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


