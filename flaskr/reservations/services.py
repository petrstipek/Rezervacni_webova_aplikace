import random, string
from flask_mail import Message
from flaskr.extensions import mail
from flaskr.db import get_db
from datetime import datetime, timedelta

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

def get_or_create_klient(name, surname, email, phone):
    db = get_db()
    result = db.execute('SELECT ID_osoba FROM klient WHERE email = ?', (email,)).fetchone()

    if result:
        klient_id = result[0]
    else:
        cursor = db.execute('INSERT INTO klient (jmeno, prijmeni, email, tel_cislo) VALUES (?, ?, ?, ?)', (name, surname, email, phone))
        db.commit()
        klient_id = cursor.lastrowid

    return klient_id

def process_reservation(form):
    db = get_db()

    name, surname, email, phone, experience, age, lesson_type, reservation_note, lesson_length, instructor_selected, language_selection, time_plus_one, student_client, more_students, client_name_fields, client_surname_fields, client_age_fields, client_experience_fields, date, time = handle_form(form)
    client_id = get_or_create_klient(name, surname, email, phone)
    student_count = handle_number_student(student_client, more_students, client_name_fields)
    identifier = generate_unique_reservation_identifier()

    cursor = db.execute('INSERT INTO rezervace (ID_osoba, typ_rezervace, termin, cas_zacatku, doba_vyuky, jazyk, pocet_zaku, platba, rezervacni_kod, poznamka) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (client_id, lesson_type, date, time , lesson_length, language_selection, student_count, "nezaplaceno", identifier, reservation_note))
    reservation_id = cursor.lastrowid
    insert_students(student_count, reservation_id, client_name_fields, client_surname_fields, client_age_fields, client_experience_fields)

    if lesson_type == "individual":
        result, message, message_type = individual_reservation(reservation_id, instructor_selected, lesson_length, student_count, date, time, time_plus_one)
        
    elif lesson_type =="group":
        result, message, message_type = group_reservation(reservation_id, student_count, date, time)
    
    if result:
        send_email('Rezervace lyžařské hodiny', 'jl6701543@gmail.com', 'felixgrent@gmail.com', 'text body emailu', "Vaše rezervace má ID: "  + identifier)
        db.commit()
    
    return message, message_type

def individual_reservation(reservation_id, instructor_selected, lesson_length, student_count, date, time, time_plus_one):
    if lesson_length == "1hodina":
        return individual_reservation_1hour(reservation_id, instructor_selected, student_count, date, time)
    elif lesson_length == "2hodiny":
        return individual_reservation_2hour(reservation_id, instructor_selected, student_count, date, time, time_plus_one)

def individual_reservation_1hour(reservation_id, instructor_selected, student_count, date, time):
    db = get_db()
    if instructor_selected == "0":
        found_number = 0
        for student in range(student_count):
            lesson_id = db.execute('SELECT ID_hodiny FROM dostupne_hodiny WHERE datum = ? AND cas_zacatku = ? AND stav = ? AND typ_hodiny = ?', (date, time, "volno", "ind")).fetchone()
            print(student, lesson_id, "jsem tady", student)
            if lesson_id == None:
                message, message_type = "Pro zvolená kritéria dostupná hodina neexistuje", "danger"
                return False, message, message_type
            assign_instructor_lesson_1hour(lesson_id["ID_hodiny"], reservation_id)
            found_number += 1
        if found_number < student_count:
            message, message_type = "Nedostatečný počet dostupných hodin pro zvolený počet žáků!", "danger"
            return False, message, message_type
    elif instructor_selected != "0":
        if student_count > 1:
            message, message_type = "Pro volbu instruktora je možné mít pouze jednoho žáka!", "danger"
            return False, message, message_type
        lesson = db.execute('SELECT ID_hodiny, ID_osoba from dostupne_hodiny left join ma_vypsane using("ID_hodiny") WHERE ID_osoba = ? AND datum = ? AND cas_zacatku = ? and stav = ? AND typ_hodiny = ?', (instructor_selected, date, time, "volno", "ind")).fetchone()
        if lesson == None:
            message, message_type = "Pro zvolená kritéria dostupná hodina neexistuje", "danger"
            return False, message, message_type
        assign_instructor_lesson_1hour(lesson["ID_hodiny"], reservation_id)
    
    message, message_type = "Rezervace proběhla úspěšně!", "success"
    return True, message, message_type

def individual_reservation_2hour(reservation_id, instructor_selected, student_count, date, time, time_plus_one):
    found_number = 0
    if instructor_selected == "0":
        instructors = unique_instructors()
        for student in range(student_count):
            availability_result = check_two_hour_availability(False, reservation_id, date, time, time_plus_one, instructors)
            if availability_result:
                instructor_id, lessons_id = availability_result
                assign_instructor_lesson_2hour(instructor_id, lessons_id, reservation_id)
                found_number += 1
        if found_number < student_count:
            message, message_type = "Nebyly nalezeny dvě po sobě jdoucí hodiny se stejným instruktorem!", "danger"
            return False, message, message_type

    elif instructor_selected != "0":
        availability_result = check_two_hour_availability(True, instructor_selected, date, time, time_plus_one)
        if availability_result:
            instructor_id, lessons_id = availability_result
            assign_instructor_lesson_2hour(instructor_id, lessons_id, reservation_id)
            found_number += 1
        if found_number < student_count:
            message, message_type = "Nebyly nalezeny dvě po sobě jdoucí hodiny se stejným instruktorem!", "danger"
            return False, message, message_type
    message, message_type = "Dvou hodinové lekce zarezervovány!", "succes"
    return False, message, message_type

def check_two_hour_availability(fixed_iteration_type, instructor_selected, date, time, time_plus_one, instructors=None):
    db = get_db()
    if fixed_iteration_type:
        for i in range(2):
            query_result = db.execute('select ID_osoba, ID_hodiny from ma_vypsane left join Dostupne_hodiny using (ID_hodiny) where stav = "volno" and datum = ? and cas_zacatku = ? AND ID_osoba = ? AND typ_hodiny = ? order by ID_osoba', (date, time, instructor_selected, "ind")).fetchone()    
            if query_result is None:
                continue
            query_result2 = db.execute('select ID_osoba, ID_hodiny from ma_vypsane left join Dostupne_hodiny using (ID_hodiny) where ID_osoba = ? and datum = ? and cas_zacatku = ? AND typ_hodiny = ?', (instructor_selected, date, time_plus_one, "ind")).fetchone()        
            if query_result2 is None:
                continue
            instructor_id = query_result["ID_osoba"]
            lessons_id = (query_result["ID_hodiny"], query_result2["ID_hodiny"])
            return instructor_id, lessons_id
    else:
        for id_osoba in instructors:
            query_result = db.execute('select ID_osoba, ID_hodiny from ma_vypsane left join Dostupne_hodiny using (ID_hodiny) where stav = "volno" and datum = ? and cas_zacatku = ? AND ID_osoba = ? AND typ_hodiny = ? order by ID_osoba', (date, time, id_osoba, "ind")).fetchone()    
            if query_result is None:
                continue
            query_result2 = db.execute('select ID_osoba, ID_hodiny from ma_vypsane left join Dostupne_hodiny using (ID_hodiny) where ID_osoba = ? and datum = ? and cas_zacatku = ? AND typ_hodiny = ?', (id_osoba, date, time_plus_one, "ind")).fetchone()        
            if query_result2 is None:
                continue
            instructor_id = query_result["ID_osoba"]
            lessons_id = (query_result["ID_hodiny"], query_result2["ID_hodiny"])
            return instructor_id, lessons_id
    return False     


def assign_instructor_lesson_2hour(instructor_id, lessons_id, reservation_id):
    db = get_db()
    db.execute('UPDATE Dostupne_hodiny SET stav = "obsazeno" WHERE ID_hodiny = ?', (lessons_id[0],))
    db.execute('UPDATE Dostupne_hodiny SET stav = "obsazeno" WHERE ID_hodiny = ?', (lessons_id[1],))
    db.execute('INSERT INTO ma_vyuku (ID_osoba, ID_rezervace) VALUES (?, ?)', (instructor_id,reservation_id))
    db.execute('INSERT INTO prirazeno (ID_rezervace, ID_hodiny) VALUES (?, ?)', (reservation_id, lessons_id[0]))
    db.execute('INSERT INTO prirazeno (ID_rezervace, ID_hodiny) VALUES (?, ?)', (reservation_id, lessons_id[1]))


def unique_instructors():
    db = get_db()
    unique_ids = db.execute('SELECT DISTINCT ID_osoba FROM ma_vypsane').fetchall()
    return [row['ID_osoba'] for row in unique_ids]

def assign_instructor_lesson_1hour(lesson_id, reservation_id):
    db = get_db()

    db.execute('UPDATE Dostupne_hodiny SET stav = "obsazeno" WHERE ID_hodiny = ?', (lesson_id,))
    instructor_id = db.execute('SELECT ID_osoba FROM ma_vypsane WHERE ID_hodiny = ?', (lesson_id,)).fetchone()
    db.execute('INSERT INTO ma_vyuku (ID_osoba, ID_rezervace) VALUES (?, ?)', (instructor_id["ID_osoba"],reservation_id))
    db.execute('INSERT INTO prirazeno (ID_rezervace, ID_hodiny) VALUES (?, ?)', (reservation_id, lesson_id))

def group_reservation(reservation_id, student_count, date, time):
    db = get_db()
    for student in range(student_count):
        query_result = db.execute('SELECT ID_hodiny, ID_osoba, obsazenost, kapacita FROM dostupne_hodiny left join ma_vypsane using (ID_hodiny) WHERE datum = ? AND cas_zacatku = ? AND stav = ? AND typ_hodiny = ? AND obsazenost < kapacita', (date, time, "volno", "group")).fetchone()
        if query_result == None:
            message, message_type = 'Pozor - kapacita lekce byla překročena. Zvolte menší počet žáků!', "danger"
            return False, message, message_type
        obsazenost = query_result["obsazenost"] + 1
        db.execute('UPDATE Dostupne_hodiny SET obsazenost = ? WHERE ID_hodiny = ?', (obsazenost, query_result["ID_hodiny"],))
    db.execute('INSERT INTO ma_vyuku (ID_osoba, ID_rezervace) VALUES (?, ?)', (query_result["ID_osoba"],reservation_id))
    db.execute('INSERT INTO prirazeno (ID_rezervace, ID_hodiny) VALUES (?, ?)', (reservation_id, query_result["ID_hodiny"]))
    handle_group_lesson_state(query_result["obsazenost"], query_result["kapacita"], query_result["ID_hodiny"])
    message, message_type = "Rezervace byla úspěšně uložena, detail najdete v emailu!", "success"
    return True, message, message_type

def handle_group_lesson_state(occupancy, capacity, ID_lesson):
    db = get_db()
    if occupancy == capacity:
        db.execute('UPDATE Dostupne_hodiny SET stav = "obsazeno" WHERE ID_hodiny = ?', (ID_lesson,))

def insert_students(student_count, reservation_id, client_name_fields, client_surname_fields, client_age_fields, client_experience_fields):
    db = get_db()
    for i in range(student_count):
        if client_age_fields[i] == None:
            continue
        db.execute('INSERT INTO zak (ID_rezervace, jmeno, prijmeni, zkusenost, vek) VALUES (?, ?, ?, ?, ?)', (reservation_id, client_name_fields[i], client_surname_fields[i], client_experience_fields[i], client_age_fields[i]))

def handle_number_student(student_client, more_students, client_name_fields):
    student_count = 0
    if student_client:
        student_count += 1
    if more_students:
        for i in range(len(client_name_fields)-1):
            if client_name_fields[i] != "":
                student_count += 1
    return student_count

def handle_form(form):
    date = form.date.data
    time_to_split = form.time.data
    time_parts = time_to_split.split(",")
    time = time_parts[0]
    #datetime_str = f"{date} {time}:00"

    name = form.name.data
    surname = form.surname.data
    email = form.email.data
    phone = form.tel_number.data
    lesson_type = form.lesson_type.data
    reservation_note = form.note.data
    lesson_length = form.lesson_length.data
    instructor_selected = form.lesson_instructor_choices.data
    language_selection = form.language_selection.data
    experience = form.experience_client.data
    age = form.age_client.data

    time_str = time

    datetime_obj = datetime.strptime(time_str, '%H:%M')
    datetime_obj_plus_one_hour = datetime_obj + timedelta(hours=1)
    time_plus_one = datetime_obj_plus_one_hour.strftime('%H:%M')

    student_client = form.student_client.data
    more_students = form.more_students.data

    client_name_fields = [name, form.name_client1.data, form.name_client2.data]
    client_surname_fields = [surname, form.surname_client1.data, form.surname_client2.data]
    client_age_fields = [age, form.age_client1.data, form.age_client2.data]
    client_experience_fields = [experience, form.experience_client1.data, form.experience_client2.data]

    return name, surname, email, phone, experience, age, lesson_type, reservation_note, lesson_length, instructor_selected, language_selection, time_plus_one, student_client, more_students, client_name_fields, client_surname_fields, client_age_fields, client_experience_fields, date, time

def handle_all_instructors(available_instructors):
    return_instructors = [(0, "Instruktor")]
    for row in available_instructors:
        return_instructors.append((row["ID_osoba"], row["jmeno"]))
    return return_instructors