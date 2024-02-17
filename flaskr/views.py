from flask import Blueprint, render_template, request, jsonify, json, flash, redirect, url_for
from flaskr.forms import PersonalInformationForm
from flaskr.db import get_db

views = Blueprint("views", __name__)

available_times = {
    "02/16/2024": ["čas 14:00", "čas 15:00", "čas 16:00", "čas 17:00", "čas 18:00", "čas 19:00", "čas 20:00", "čas 21:00", "čas 22:00", "čas 23:00"],  # Added missing comma
    "02/17/2024": ["čas 18:00", "čas 19:00", "čas 20:00", "čas 21:00", "čas 22:00", "čas 23:00"],
    "02/18/2024": ["čas 11:00", "čas 12:00", "čas 18:00", "čas 19:00", "čas 20:00", "čas 21:00", "čas 22:00", "čas 23:00"]
}


@views.route('/', methods=["GET", "POST"])
def main_page():
    form = PersonalInformationForm()

    ##reservation_date_time = request.json
    ##print(reservation_date_time) 
    if request.method == 'POST':
        if request.is_json:
            # Process JSON data
            data = request.get_json()
            print(data)
            # Handle AJAX logic here
            return jsonify({"status": "success"})
        else:
            if form.validate_on_submit():
                db = get_db()

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

                cursor = db.execute('INSERT INTO rezervace (ID_osoba, typ_rezervace, termin, doba_vyuky, jazyk, pocet_zaku, poznamka) VALUES (?, ?, ?, ?, ?, ?, ?)', (klient_id, lesson_type, "2023-01-15" , 2, "čeština", student_count, reservation_note))
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

@views.route('/admin-page')
def admin_page():
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


