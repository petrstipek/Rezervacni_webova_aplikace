# FileName: users.py
# Description: Provides Model of users with information from database.
# Author: Petr Štípek
# Date: 2024

from flaskr.extensions import database
from flask_login import current_user
from flaskr.auth.auth import check_password, hash_password

from flaskr.models.user import Osoba
from flaskr.models.reservation import Rezervace
from flaskr.models.student import Zak

def validate_password(old_password):
    user = database.session.query(Osoba).filter(Osoba.ID_osoba==current_user.get_id()).first()
    check_result = check_password(current_user.heslo, old_password)
    if check_result:
        return True
    return False

def update_personal_information(name, surname, email, tel_number, password):
    try:
        if name != current_user.jmeno and name != "":
            current_user.jmeno = name
        if surname != current_user.prijmeni and surname != "":
            current_user.prijmeni = surname
        if email != current_user.email and email != "":
            current_user.email = email
        if tel_number != current_user.tel_cislo and tel_number != "":
            current_user.tel_cislo = tel_number
        if password and password != "":
            if not check_password(current_user.heslo, password):
                current_user.heslo = hash_password(password)
            else:

                return (False, "Nové heslo musí být jiné oproti aktuálnímu heslu!")

        database.session.commit()
        return (True, "Údaje byly úspěšně aktualizovány!")

    except Exception as e:
        database.session.rollback()
        return (False, f"An error occurred: {e}")

def get_reservation_students_status(reservation_id):
    query_result = database.session.query(Rezervace).filter(Rezervace.ID_rezervace==reservation_id).first()

    query_result_client = database.session.query(Osoba).filter(Osoba.ID_osoba==query_result.ID_osoba).first()
    query_result_students = database.session.query(Zak).filter(Zak.ID_rezervace==reservation_id).all()

    client_status = False
    student_status = False

    for student in query_result_students:
        if student.jmeno == query_result_client.jmeno and student.prijmeni == query_result_client.prijmeni:
            client_status = True
        elif student.jmeno == query_result_client.jmeno or student.prijmeni == query_result_client.prijmeni:
            student_status = False

    return client_status, student_status

def get_reservation_details_proper(reservation_id):
    query_result = database.session.query(Rezervace).filter(Rezervace.ID_rezervace==reservation_id).first()
    return query_result