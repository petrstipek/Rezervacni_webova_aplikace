# FileName: services.py
# Description: Model file for handling reservation logic, database communication and all form reservation validation.
# Author: Petr Štípek
# Date: 2024

import random, string
from flask_mail import Message
from flaskr.extensions import mail
from datetime import datetime, timedelta
from flaskr.extensions import database
from sqlalchemy.orm.exc import NoResultFound 
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from flaskr.auth.services import register_new_user
from flaskr.email.email import send_reservation_confirmation

from flaskr.models.user import Osoba
from flaskr.models.reservation import Rezervace, MaVypsane, MaVyuku, Prirazeno
from flaskr.models.client import Klient
from flaskr.models.student import Zak
from flaskr.models.available_times import DostupneHodiny

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=[recipients])
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def generate_unique_reservation_identifier():
    while True:
        identifier = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

        try:
            database.session.query(Rezervace).filter_by(rezervacni_kod=identifier).one()
        except NoResultFound:
            break

    return identifier

def get_or_create_klient(name, surname, email, phone):
    query_result = database.session.query(Osoba).filter_by(email=email).first()

    if query_result:
        klient_id = query_result.ID_osoba
    else:
        new_osoba = Osoba(jmeno=name, prijmeni=surname, email=email, tel_cislo=phone,)
        database.session.add(new_osoba)
        database.session.flush()

        klient_id = new_osoba.ID_osoba

        new_client = Klient(ID_osoba=new_osoba.ID_osoba,)
        database.session.add(new_client)
        database.session.commit()

    return klient_id

def process_reservation(form):
    name, surname, email, phone, experience, age, lesson_type, reservation_note, lesson_length, instructor_selected, language_selection, time_plus_one, student_client, more_students, client_name_fields, client_surname_fields, client_age_fields, client_experience_fields, date, time = handle_form(form)
    if date == None or time == None:
        return False, "Je potřeba vyplnit čas a datum lekce!", "danger"
    
    client_id = get_or_create_klient(name, surname, email, phone)
    student_count = handle_number_student(student_client, client_name_fields)
    identifier = generate_unique_reservation_identifier()
    
    termin_date = datetime.strptime(date, '%Y-%m-%d').date()
    cas_zacatku_time = datetime.strptime(time, '%H:%M').time() 

    new_reservation = Rezervace(
        ID_osoba=client_id,
        typ_rezervace=lesson_type,
        termin=termin_date,
        cas_zacatku=cas_zacatku_time,
        doba_vyuky=lesson_length,
        jazyk=language_selection,
        pocet_zaku=student_count,
        platba='nezaplaceno',
        rezervacni_kod=identifier,
        poznamka=reservation_note 
    )

    database.session.add(new_reservation)
    database.session.flush()

    reservation_id = new_reservation.ID_rezervace

    insert_students(student_count, reservation_id, client_name_fields, client_surname_fields, client_age_fields, client_experience_fields, student_client, more_students)

    if lesson_type == "individual":
        result, message, message_type = individual_reservation(reservation_id, instructor_selected, lesson_length, student_count, date, time, time_plus_one)
        
    elif lesson_type =="group":
        result, message, message_type = group_reservation(reservation_id, student_count, date, time)
    elif lesson_type =="group-ind":
        result, message, message_type = individual_group_reservation(reservation_id, instructor_selected, lesson_length, student_count, date, time, time_plus_one)
    
    if result:
        database.session.commit()
        send_reservation_confirmation(email, new_reservation)
        reservation_identifier = new_reservation.rezervacni_kod
        return message, message_type, reservation_identifier
    
    return message, message_type

def individual_reservation(reservation_id, instructor_selected, lesson_length, student_count, date, time, time_plus_one):
    if lesson_length == "1hodina":
        return individual_reservation_1hour(reservation_id, instructor_selected, student_count, date, time)
    elif lesson_length == "2hodiny":
        return individual_reservation_2hour(reservation_id, instructor_selected, student_count, date, time, time_plus_one)
    
def individual_group_reservation(reservation_id, instructor_selected, lesson_length, student_count, date, time, time_plus_one):
    if lesson_length == "1hodina":
        return individual_group_reservation_1hour(reservation_id, instructor_selected, student_count, date, time)
    elif lesson_length == "2hodiny":
        return individual_group_reservation_2hour(reservation_id, instructor_selected, date, time, time_plus_one)
    
def individual_group_reservation_1hour(reservation_id, instructor_selected, student_count, date, time):
    termin_date = datetime.strptime(date, '%Y-%m-%d').date()
    cas_zacatku_time = datetime.strptime(time, '%H:%M').time() 

    if instructor_selected == "0":
        lesson_id = database.session.query(DostupneHodiny.ID_hodiny).filter(
                        DostupneHodiny.datum == termin_date,
                        DostupneHodiny.cas_zacatku == cas_zacatku_time,
                        DostupneHodiny.stav == 'volno',
                        DostupneHodiny.typ_hodiny == 'ind'
                        ).first()
        if lesson_id == None:
                message, message_type = "Pro zvolená kritéria dostupná hodina neexistuje", "danger"
                return False, message, message_type
        specific_instructor = False
        assign_instructor_lesson_1hour(lesson_id, reservation_id, specific_instructor)
    elif instructor_selected != "0":
        lesson = database.session.query(DostupneHodiny).outerjoin(MaVypsane, DostupneHodiny.ID_hodiny == MaVypsane.ID_hodiny).filter(and_(MaVypsane.ID_osoba==instructor_selected, DostupneHodiny.datum==termin_date, DostupneHodiny.cas_zacatku==cas_zacatku_time, DostupneHodiny.stav=="volno", DostupneHodiny.typ_hodiny=="ind")).first()
        if lesson == None:
            message, message_type = "Pro zvolená kritéria dostupná hodina neexistuje", "danger"
            return False, message, message_type
        specific_instructor = True
        assign_instructor_lesson_1hour(lesson.ID_hodiny, reservation_id, specific_instructor)

    message, message_type = "Rezervace proběhla úspěšně!", "success"
    return True, message, message_type

def individual_group_reservation_2hour(reservation_id, instructor_selected, date, time, time_plus_one):
    if instructor_selected == "0":
        instructors = unique_instructors()
        availability_result = check_two_hour_availability(False, reservation_id, date, time, time_plus_one, instructors)
        if availability_result:
                instructor_id, lessons_id = availability_result
                assign_instructor_lesson_2hour(instructor_id, lessons_id, reservation_id)
        else:
            message, message_type = "Nebyly nalezeny dvě po sobě jdoucí hodiny se stejným instruktorem!", "danger"
            return False, message, message_type
    elif instructor_selected != "0":
        availability_result = check_two_hour_availability(True, instructor_selected, date, time, time_plus_one)
        if availability_result:
            instructor_id, lessons_id = availability_result
            assign_instructor_lesson_2hour(instructor_id, lessons_id, reservation_id)
        else:
            message, message_type = "Nebyly nalezeny dvě po sobě jdoucí hodiny se stejným instruktorem!", "danger"
            return False, message, message_type

    message, message_type = "Dvouhodinové lekce zarezervovány!", "success"
    return True, message, message_type

def individual_reservation_1hour(reservation_id, instructor_selected, student_count, date, time):
    termin_date = datetime.strptime(date, '%Y-%m-%d').date()
    cas_zacatku_time = datetime.strptime(time, '%H:%M').time() 
    if instructor_selected == "0":
        found_number = 0
        for student in range(student_count):
            lesson_id = database.session.query(DostupneHodiny.ID_hodiny).filter(
                        DostupneHodiny.datum == termin_date,
                        DostupneHodiny.cas_zacatku == cas_zacatku_time,
                        DostupneHodiny.stav == 'volno',
                        DostupneHodiny.typ_hodiny == 'ind'
                        ).first()
            if lesson_id == None:
                message, message_type = "Pro zvolená kritéria dostupná hodina neexistuje", "danger"
                return False, message, message_type
            specific_instructor = False
            assign_instructor_lesson_1hour(lesson_id, reservation_id, specific_instructor)
            found_number += 1
        if found_number < student_count:
            message, message_type = "Nedostatečný počet dostupných hodin pro zvolený počet žáků!", "danger"
            return False, message, message_type
    elif instructor_selected != "0":
        if student_count > 1:
            message, message_type = "Pro volbu instruktora je možné mít pouze jednoho žáka!", "danger"
            return False, message, message_type
        lesson = database.session.query(DostupneHodiny).outerjoin(MaVypsane, DostupneHodiny.ID_hodiny == MaVypsane.ID_hodiny).filter(and_(MaVypsane.ID_osoba==instructor_selected, DostupneHodiny.datum==termin_date, DostupneHodiny.cas_zacatku==cas_zacatku_time, DostupneHodiny.stav=="volno", DostupneHodiny.typ_hodiny=="ind")).first()
        if lesson == None:
            message, message_type = "Pro zvolená kritéria dostupná hodina neexistuje", "danger"
            return False, message, message_type
        specific_instructor = True
        assign_instructor_lesson_1hour(lesson.ID_hodiny, reservation_id, specific_instructor)
    
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
    message, message_type = "Dvouhodinové lekce zarezervovány!", "success"
    return True, message, message_type

def check_two_hour_availability(fixed_iteration_type, instructor_selected, date, time, time_plus_one, instructors=None):
    termin_date = datetime.strptime(date, '%Y-%m-%d').date()
    cas_zacatku_time = datetime.strptime(time, '%H:%M').time()
    cas_zacatku_time_plus_one = datetime.strptime(time_plus_one, '%H:%M').time()
    if fixed_iteration_type:
        for i in range(2):
            query_result = database.session.query(DostupneHodiny).outerjoin(MaVypsane, DostupneHodiny.ID_hodiny==MaVypsane.ID_hodiny).filter(and_(DostupneHodiny.stav=="volno", DostupneHodiny.datum==termin_date, DostupneHodiny.cas_zacatku==cas_zacatku_time, MaVypsane.ID_osoba==instructor_selected, DostupneHodiny.typ_hodiny=="ind")).order_by(MaVypsane.ID_osoba).first()
            if query_result is None:
                continue
            query_result2 = database.session.query(DostupneHodiny).outerjoin(MaVypsane, DostupneHodiny.ID_hodiny==MaVypsane.ID_hodiny).filter(and_(DostupneHodiny.stav=="volno", DostupneHodiny.datum==termin_date, DostupneHodiny.cas_zacatku==cas_zacatku_time_plus_one, MaVypsane.ID_osoba==instructor_selected, DostupneHodiny.typ_hodiny=="ind")).order_by(MaVypsane.ID_osoba).first()
            if query_result2 is None:
                continue
            instructor_id = instructor_selected
            lessons_id = (query_result.ID_hodiny, query_result2.ID_hodiny)
            return instructor_id, lessons_id
    else:
        for id_osoba in instructors:
            query_result = database.session.query(DostupneHodiny).outerjoin(MaVypsane, DostupneHodiny.ID_hodiny==MaVypsane.ID_hodiny).filter(and_(DostupneHodiny.stav=="volno", DostupneHodiny.datum==termin_date, MaVypsane.ID_osoba==id_osoba, DostupneHodiny.cas_zacatku==cas_zacatku_time, DostupneHodiny.typ_hodiny=="ind")).order_by(MaVypsane.ID_osoba).first()
            if query_result is None:
                continue
            query_result2 = database.session.query(DostupneHodiny).outerjoin(MaVypsane, DostupneHodiny.ID_hodiny==MaVypsane.ID_hodiny).filter(and_(DostupneHodiny.stav=="volno", DostupneHodiny.datum==termin_date, DostupneHodiny.cas_zacatku==cas_zacatku_time_plus_one, MaVypsane.ID_osoba==id_osoba, DostupneHodiny.typ_hodiny=="ind")).order_by(MaVypsane.ID_osoba).first()
            if query_result2 is None:
                continue
            instructor_id = id_osoba
            lessons_id = (query_result.ID_hodiny, query_result2.ID_hodiny)
            return instructor_id, lessons_id
    return False     


def assign_instructor_lesson_2hour(instructor_id, lessons_id, reservation_id):
    try:
        for lesson_id in lessons_id:
            lesson = database.session.query(DostupneHodiny).filter_by(ID_hodiny=lesson_id).first()
            if lesson:
                lesson.stav = 'obsazeno'

        new_ma_vyuku = MaVyuku(ID_osoba=instructor_id, ID_rezervace=reservation_id)
        database.session.add(new_ma_vyuku)

        for lesson_id in lessons_id:
            new_prirazeno = Prirazeno(ID_rezervace=reservation_id, ID_hodiny=lesson_id)
            database.session.add(new_prirazeno)

        #database.session.commit()
    
    except Exception as e:
        database.session.rollback()
        raise e 


def unique_instructors():
    unique_ids = database.session.query(MaVypsane.ID_osoba).distinct().all()
    return [row.ID_osoba for row in unique_ids]

def assign_instructor_lesson_1hour(lesson_id, reservation_id, specific_instructor):
    if not specific_instructor:
        lesson_id = lesson_id[0]
    try:
        database.session.query(DostupneHodiny)\
            .filter(DostupneHodiny.ID_hodiny == lesson_id)\
            .update({DostupneHodiny.stav: "obsazeno"})
        
        instructor_result = database.session.query(MaVypsane.ID_osoba)\
            .filter(MaVypsane.ID_hodiny == lesson_id).first()
        
        if instructor_result is None:
            raise Exception("Nenalezen instruktor pro tuto hodinu")
        
        instructor_id = instructor_result.ID_osoba

        new_ma_vyuku = MaVyuku(ID_osoba=instructor_id, ID_rezervace=reservation_id)
        database.session.add(new_ma_vyuku)

        new_prirazeno = Prirazeno(ID_rezervace=reservation_id, ID_hodiny=lesson_id)
        database.session.add(new_prirazeno)
        
    except SQLAlchemyError as e:
        database.session.rollback()
        raise e

def group_reservation(reservation_id, student_count, date, time):
    try:
        termin_date = datetime.strptime(date, '%Y-%m-%d').date()
        cas_zacatku_time = datetime.strptime(time, '%H:%M').time()
        
        instructor_id = None
        lesson_id = None

        for student in range(student_count):
            lesson = database.session.query(DostupneHodiny).join(MaVypsane, DostupneHodiny.ID_hodiny==MaVypsane.ID_hodiny).filter(DostupneHodiny.datum == termin_date,
                    DostupneHodiny.cas_zacatku == cas_zacatku_time,
                    DostupneHodiny.stav == 'volno',
                    DostupneHodiny.typ_hodiny == 'group',
                    DostupneHodiny.obsazenost < DostupneHodiny.kapacita).first()

            if lesson is None:
                message, message_type = 'Pozor - kapacita lekce byla překročena. Zvolte menší počet žáků!', "danger"
                return False, message, message_type
            
            lesson_id = lesson.ID_hodiny
            instructor = database.session.query(Osoba).join(MaVypsane, Osoba.ID_osoba == MaVypsane.ID_osoba).filter(MaVypsane.ID_hodiny == lesson_id).first()

            
            lesson.obsazenost += 1
            if student == 0:
                instructor_id = instructor.ID_osoba
                lesson_id = lesson.ID_hodiny

        if instructor_id and lesson_id:
            new_ma_vyuku = MaVyuku(ID_osoba=instructor_id, ID_rezervace=reservation_id)
            new_prirazeno = Prirazeno(ID_rezervace=reservation_id, ID_hodiny=lesson_id)
            database.session.add(new_ma_vyuku)
            database.session.add(new_prirazeno)

        #database.session.commit()
        handle_group_lesson_state(lesson.obsazenost, lesson.kapacita, lesson_id)
        message, message_type = "Rezervace byla úspěšně uložena, detail najdete v emailu!", "success"
        return True, message, message_type

    except SQLAlchemyError as e:
        database.session.rollback()
        return False, "Database error: " + str(e), "danger"

def handle_group_lesson_state(occupancy, capacity, ID_lesson):
    try:
        if occupancy == capacity:
            database.session.query(DostupneHodiny)\
                .filter(DostupneHodiny.ID_hodiny == ID_lesson)\
                .update({DostupneHodiny.stav: 'obsazeno'})
            
            #database.session.commit()

    except SQLAlchemyError as e:
        database.session.rollback()
        raise e

def insert_students(student_count, reservation_id, client_name_fields, client_surname_fields, client_age_fields, client_experience_fields, student_client, more_students):
    #student_count = len(client_name_fields)
    try:
        if (student_client and more_students) or (student_client and not more_students):
            for i in range(student_count):
                if client_age_fields[i] is None:
                    continue
            
                new_student = Zak(
                    ID_rezervace=reservation_id,
                    jmeno=client_name_fields[i],
                    prijmeni=client_surname_fields[i],
                    zkusenost=client_experience_fields[i],
                    vek=client_age_fields[i]
                )
                database.session.add(new_student)
        if not student_client:
            client_name_fields = client_name_fields[1:]
            client_surname_fields = client_surname_fields[1:]
            client_age_fields = client_age_fields[1:]
            client_experience_fields = client_experience_fields[1:]
            for i in range(student_count):
                if client_age_fields[i] is None:
                    continue
            
                new_student = Zak(
                    ID_rezervace=reservation_id,
                    jmeno=client_name_fields[i],
                    prijmeni=client_surname_fields[i],
                    zkusenost=client_experience_fields[i],
                    vek=client_age_fields[i]
                )
                database.session.add(new_student)

        #database.session.commit()
    
    except Exception as e:
        database.session.rollback()
        raise e
    
def handle_number_student(student_client, client_name_fields):
    student_count = 0
    for name_field in client_name_fields:
        if name_field != "":
            student_count += 1
    if student_client == False:
        student_count -= 1
    return student_count

def handle_form(form):
    date = form.date.data
    time_to_split = form.time_reservation.data
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
    return_instructors = [(0, "Kdokoli volný")]
    for row in available_instructors:
        return_instructors.append((row["ID_osoba"], row["jmeno"]))
    return return_instructors

def process_submit_registration(form):
    client_result = database.session.query(Osoba).filter_by(email=form.email.data).first()
    if client_result:
        status, message = True, "Uživatel s tímto emailem již existuje! Pokud jste zapomněli heslo, můžete si ho změnit."
        return status, message
    result = register_new_user(form)
    if result:
        status, message = True, "Registrace proběhla úspěšně! Nyní se můžete přihlásit. Rezervaci najdete ve svém účtu."
    else:
        status, message = False, "Registrace se nezdařila!"
    return status, message