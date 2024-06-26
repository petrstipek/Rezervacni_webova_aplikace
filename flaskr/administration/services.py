# FileName: services.py
# Description: Handles the administration logic and database for the web application.
# Author: Petr Štípek
# Date: 2024

from flaskr.extensions import database
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from datetime import datetime, timedelta
from sqlalchemy import func, case
from flaskr.reservations.services import process_reservation, handle_number_student
from flaskr.api.services.reservations_services import delete_reservation_by_reservation_id
from flaskr.auth.services import hash_password
from werkzeug.utils import secure_filename
import os
from flask import current_app
from flask import Response
import csv
from io import StringIO
from sqlalchemy.inspection import inspect
import calendar
import plotly.graph_objects as go
from collections import defaultdict

from flaskr.models.instructor import Instruktor
from flaskr.models.user import Osoba
from flaskr.models.reservation import Rezervace, MaVypsane, MaVyuku, Prirazeno
from flaskr.models.client import Klient
from flaskr.models.student import Zak
from flaskr.models.available_times import DostupneHodiny

def instructor_exists(email):
    query_result = database.session.query(Instruktor) \
                .join(Osoba) \
                .filter(Osoba.email == email) \
                .options(joinedload(Instruktor.osoba)) \
                .first()
    return query_result is not None

def add_instructor(name, surname, email, tel_number, experience, date_birth, date_started, password, file, text):
    new_osoba = Osoba(jmeno=name, prijmeni=surname, email=email, tel_cislo=tel_number, heslo=hash_password(password), prihl_jmeno=email)

    database.session.add(new_osoba)
    database.session.flush()

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{new_osoba.ID_osoba}_{file.filename}")
        filepath = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
    if not file:
        filename = secure_filename(f"test_picture.jpg")

    new_instruktor = Instruktor(
        ID_osoba=new_osoba.ID_osoba, 
        seniorita=experience, 
        datum_narozeni=date_birth, 
        datum_nastupu=date_started, 
        image_path=filename,
        popis=text
    )

    database.session.add(new_instruktor)
    database.session.commit()

    return True

def get_available_instructors():
    query_result_instructors = database.session.query(Instruktor.ID_osoba, Osoba.jmeno, Osoba.prijmeni)\
        .join(Osoba, Instruktor.ID_osoba == Osoba.ID_osoba).distinct()
    
    available_instructors = [(0, "Instruktor")]
    for row in query_result_instructors:
        available_instructors.append((row.ID_osoba ,row.jmeno + " " + row.prijmeni))
    return available_instructors

def add_individual_lesson(date_str, time_start, instructor_id, lesson_type, capacity):

    query_result = database.session.query(DostupneHodiny)\
    .join(MaVypsane, DostupneHodiny.ID_hodiny == MaVypsane.ID_hodiny, isouter=True)\
    .filter(and_(
        DostupneHodiny.datum == date_str, 
        DostupneHodiny.cas_zacatku == time_start,
        MaVypsane.ID_osoba == instructor_id
    ))\
    .first()

    if query_result:
        return False, "Hodina s těmito parametry již existuje!"
    
    new_lesson = DostupneHodiny(
        datum=date_str,
        cas_zacatku=time_start,
        stav="volno",
        typ_hodiny=lesson_type,
        kapacita=capacity
    )
    database.session.add(new_lesson)
    database.session.flush()

    new_ma_vypsane = MaVypsane(
        ID_osoba=instructor_id,
        ID_hodiny=new_lesson.ID_hodiny
    )

    database.session.add(new_ma_vypsane)
    database.session.commit()
    
    return True, "Požadavek byl systémem úspešně zpracován!"

def add_group_lesson(date_str, time_start, instructor_ids, lesson_type, capacity):
    for instructor_id in instructor_ids:
        #query_result = db.execute('SELECT * from Dostupne_hodiny left join ma_vypsane using (ID_hodiny) WHERE datum = ? AND cas_zacatku = ? AND ID_osoba != ?', (date_str, time_start, instructor_id)).fetchone()
        
        query_result = database.session.query(DostupneHodiny) \
            .join(MaVypsane, DostupneHodiny.ID_hodiny == MaVypsane.ID_hodiny, isouter=True) \
            .filter(and_(
                DostupneHodiny.datum == date_str,
                DostupneHodiny.cas_zacatku == time_start,
                MaVypsane.ID_osoba != instructor_id
            )).first()
        
        if query_result:
            return False, "Hodina s těmito parametry již existuje - instruktor: " + instructor_id
        
    new_lesson = DostupneHodiny(
        datum=date_str,
        cas_zacatku=time_start,
        stav="volno",
        typ_hodiny=lesson_type,
        kapacita=capacity,
        obsazenost=0 
    )

    database.session.add(new_lesson)
    database.session.flush()

    for instructor_id in instructor_ids:
        new_ma_vypsane = MaVypsane(
            ID_osoba=instructor_id,
            ID_hodiny=new_lesson.ID_hodiny
        )
        database.session.add(new_ma_vypsane)
    database.session.commit()
    return True, "Požadavek byl systémem úspešně zpracován!"

def get_reservations():
    query_result = database.session.query(Rezervace).join(Klient, Rezervace.ID_osoba == Klient.ID_osoba).all()
    return [dict(row) for row in query_result]

def get_reservation_counts():
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=6)
    
    counts = (database.session.query(func.date(Rezervace.termin), func.count(Rezervace.ID_rezervace))
            .filter(Rezervace.termin >= start_date)
            .filter(Rezervace.termin <= end_date)
            .group_by(func.date(Rezervace.termin))
            .order_by(func.date(Rezervace.termin))
            .all())
    
    return counts

from datetime import datetime

def prepare_data_for_graph():

    #query_result = database.session.query(Instruktor.osoba.jmeno, func.count(DostupneHodiny.ID_hodiny).label("lesson_count")).join(MaVypsane, Instruktor.ID_osoba == MaVypsane.ID_osoba).join(DostupneHodiny, MaVypsane.ID_hodiny == DostupneHodiny.ID_hodiny).group_by(Instruktor.ID_osoba).all()

    query_result = database.session.query(
    Osoba.jmeno, 
    func.count(DostupneHodiny.ID_hodiny).label("lesson_count")
    ).join(Instruktor, Osoba.ID_osoba == Instruktor.ID_osoba).join(MaVypsane, Instruktor.ID_osoba == MaVypsane.ID_osoba).join(DostupneHodiny, MaVypsane.ID_hodiny == DostupneHodiny.ID_hodiny).group_by(Osoba.jmeno).all()
    
    instructors = [result[0] for result in query_result]
    lesson_counts = [result[1] for result in query_result]

    fig = go.Figure([go.Bar(x=instructors, y=lesson_counts)])
    fig.update_layout(title='Počet lekcí pro instruktora',xaxis_title='Instruktor', yaxis_title='Počet lekcí')

    return fig

def prepare_data_reservations_graph():
    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=end_date.weekday())

    counts = (database.session.query(func.date(Rezervace.termin), Rezervace.typ_rezervace, func.count(Rezervace.ID_rezervace))
            .filter(Rezervace.termin >= start_date)
            .filter(Rezervace.termin <= end_date)
            .group_by(func.date(Rezervace.termin), Rezervace.typ_rezervace)
            .order_by(func.date(Rezervace.termin), Rezervace.typ_rezervace)
            .all())
    
    type_data = defaultdict(lambda: defaultdict(int))
    dates = set()

    for date, typ, count in counts:
        type_data[typ][date.isoformat()] = count
        dates.add(date.isoformat())

    sorted_dates = sorted(dates)
    types = ['individual', 'group-ind', 'group']
    final_data = {typ: [type_data[typ][date] for date in sorted_dates] for typ in types}

    fig = go.Figure()

    for typ in types:
        fig.add_trace(go.Bar(
            x=sorted_dates,
            y=final_data[typ],
            name=typ
        ))

    fig.update_layout(
        barmode='group',
        title='Počet rezervací dle data a typu',
        xaxis_title='Datum',
        yaxis_title='Počet rezervací',
        xaxis=dict(
            type='category',
            tickformat='%Y-%m-%d'
        )
    )
    
    return fig

def process_reservation_change(form, reservation_id):
    query_result = database.session.query(Rezervace).filter(Rezervace.ID_rezervace == reservation_id).first()
    instructor_query = database.session.query(MaVyuku).filter(MaVyuku.ID_rezervace == reservation_id).first()

    not_changed_time = query_result.cas_zacatku
    not_changed_date = query_result.termin
    initial_reservation_id = query_result.ID_rezervace
    initial_student_count = query_result.pocet_zaku


    client_name_fields = [form.name.data, form.name_client1.data, form.name_client2.data]

    student_array = [form.name.data, form.name_client1.data, form.name_client2.data]
    filtered_array = [student for student in student_array if student != ""]
    length = len(filtered_array)

    student_count = handle_number_student(form.student_client.data, client_name_fields)

    client = database.session.query(Osoba).filter(Osoba.ID_osoba == query_result.ID_osoba).first()
    students = database.session.query(Zak).filter(Zak.ID_rezervace == reservation_id).all()

    updated = False
    students_info = []
    for student in students:
        student_dict = {
            "id_student": student.ID_zak,
            "name": student.jmeno,
            "surname": student.prijmeni,
            "age": student.vek,
            "experience": student.zkusenost
        }
        students_info.append(student_dict)

    if not query_result:
        return False, "Rezervace nebyla nalezena, opakujte akci!"

    if form.change_time.data:
        time_str = form.time_reservation.data
        datetime_obj = datetime.strptime(time_str, "%H:%M")
        formatted_time = datetime_obj.time()

    if not form.change_time.data and query_result.pocet_zaku == length:
        print("prvni if")
        form_students = [
            {"name" : form.name.data , "surname" : form.surname.data, "age": form.age_client.data, "experience": form.experience_client.data},
            {"name" : form.name_client1.data, "surname" : form.surname_client1.data, "age": form.age_client1.data, "experience": form.experience_client1.data},
            {"name" : form.name_client2.data, "surname" : form.surname_client2.data,  "age": form.age_client2.data, "experience": form.experience_client2.data}
        ]

        if form.email.data != client.email and form.email.data != "":
            client.email = form.email.data
            updated = True
        if form.tel_number.data != client.tel_cislo and form.tel_number.data != "":
            client.tel_cislo = form.tel_number.data
            updated = True
        if form.name.data != client.jmeno and form.name.data != "":
            client.jmeno = form.name.data
            updated = True
        if form.surname.data != client.prijmeni and form.surname.data != "":
            client.prijmeni = form.surname.data
            updated = True

        for form_student, student_info in zip(form_students, students_info):
            student = database.session.query(Zak).filter(Zak.ID_zak == student_info["id_student"]).first()
            if student:
                if form_student["name"] != student.jmeno and form_student["name"] != "":
                    student.jmeno = form_student["name"]
                    updated = True
                if form_student["surname"] != student.prijmeni and form_student["surname"] != "":
                    student.prijmeni = form_student["surname"]
                    updated = True
                if form_student["age"] != student.vek and form_student["age"] != "":
                    student.vek = form_student["age"]
                    updated = True
                if form_student["experience"] != student.zkusenost and form_student["experience"] != "":
                    student.zkusenost = form_student["experience"]
                    updated = True
    else:
        print("else")
        old_reservation_code = query_result.rezervacni_kod
        old_reservation_student_count = query_result.pocet_zaku

        deleted_reservation = False
        if student_count == initial_student_count:
            print("delete1")
            delete_reservation_by_reservation_id(reservation_id)
            deleted_reservation = True

        if not form.change_time.data and initial_student_count != length:
            print("delete2")
            check_available_lessons = database.session.query(DostupneHodiny).filter(DostupneHodiny.datum == not_changed_date, DostupneHodiny.cas_zacatku == not_changed_time, DostupneHodiny.stav == "volno").all()
            if len(check_available_lessons) >= length-1 and not deleted_reservation:
                delete_reservation_by_reservation_id(reservation_id)
                deleted_reservation = True

        #delete_reservation_by_reservation_id(reservation_id)
        form.date.data = form.date.data.strftime('%Y-%m-%d')

        if not form.change_time.data:
            print("jo jsem tady")
            form.time_reservation.data = not_changed_time.strftime('%H:%M')
            result = process_reservation(form)
        else:
            print("jsem bych se měl dostat")
            form.lesson_instructor_choices.data = "0"
            result = process_reservation(form)

        if len(result) == 3:
            message, message_type, reservation_code = result
        elif len(result) == 2:
            message, message_type = result

        print("message", message)
        print("message type", message_type)


        if message_type == "success":
            reservation = database.session.query(Rezervace).filter(Rezervace.rezervacni_kod == reservation_code).first()

            reservation.rezervacni_kod = old_reservation_code
            database.session.commit()

            if reservation.pocet_zaku > old_reservation_student_count and reservation.platba == "nezaplaceno":
                coun_student_difference = reservation.pocet_zaku - old_reservation_student_count
                return True, "Rezervace byla úspěšně aktualizována. Proběhla změna počtu žáků. Počet žáků navýšen o: " + str(coun_student_difference), str(reservation.ID_rezervace)

            if reservation.pocet_zaku < old_reservation_student_count and reservation.platba == "zaplaceno":
                coun_student_difference = old_reservation_student_count - reservation.pocet_zaku
                return True, "Rezervace byla úspěšně aktualizována. Proběhla změna počtu žáků a rezervace byla zaplacena. Počet žáků snížen o: " + str(coun_student_difference), str(reservation.ID_rezervace)

            if not deleted_reservation:
                delete_reservation_by_reservation_id(reservation_id)
            return True, "Rezervace byla úspěšně aktualizována.", reservation.ID_rezervace
        else:
            return False, message

    if updated:
        reservation_id = query_result.ID_rezervace
        try:
            database.session.commit()
            return True, "Rezervace byla úspěšně aktualizována.", reservation_id
        except Exception as e:
            database.session.rollback()
            return False, "Nepodařilo se aktualizovat rezervaci.", reservation_id

    return True, "Nebyly provedeny žádné změny."


def get_reservation_details(reservation_id):
    reservation_detail = {}
    instructor_detail = {}

    reservation_query = database.session.query(Rezervace).outerjoin(Osoba, Rezervace.ID_osoba==Osoba.ID_osoba).filter(Rezervace.ID_rezervace==reservation_id).first()
    if reservation_query:
        reservation_detail = {
            'rez_kod': reservation_query.rezervacni_kod,
            'termin_rezervace': reservation_query.termin.isoformat() if reservation_query.termin else '',
            'cas_zacatku': reservation_query.cas_zacatku.strftime('%H:%M') if reservation_query.cas_zacatku else '',
            'doba_vyuky': reservation_query.doba_vyuky,
            'platba': reservation_query.platba,
            'jmeno_klienta': reservation_query.klient.osoba.jmeno,
            'prijmeni_klienta': reservation_query.klient.osoba.prijmeni,
            'email_klienta': reservation_query.klient.osoba.email,
            'tel_cislo_klienta': reservation_query.klient.osoba.tel_cislo,
            'poznamka': reservation_query.poznamka,
            'pocet_zaku': reservation_query.pocet_zaku
        }

    instructor_query = database.session.query(Instruktor).outerjoin(Osoba, Instruktor.ID_osoba==Osoba.ID_osoba).outerjoin(MaVyuku, Instruktor.ID_osoba==MaVyuku.ID_osoba).filter(MaVyuku.ID_rezervace==reservation_id).first()
    if instructor_query:
        instructor_detail = {
            'jmeno_instruktora': instructor_query.osoba.jmeno,
            'prijmeni_instruktora': instructor_query.osoba.prijmeni
        }

    zaks = database.session.query(Zak).filter(Zak.ID_rezervace == reservation_id).all()
    zak_list = [{'ID_zak': zak.ID_zak, 'jmeno_zak': zak.jmeno, 'prijmeni_zak': zak.prijmeni, 'vek_zak': zak.vek, 'zkusenost_zak': zak.zkusenost} for zak in zaks]

    combined_details = {
        **reservation_detail, 
        'Instructor': instructor_detail,
        'Zak': zak_list
    }
    return combined_details

def get_available_lessons(date):
    query_result = database.session.query(DostupneHodiny).filter(DostupneHodiny.datum == date, DostupneHodiny.stav=="volno").all()
    return query_result

def lesson_capacity_change(lesson_id, capacity):
    lesson = database.session.query(DostupneHodiny).filter(DostupneHodiny.ID_hodiny == lesson_id).first()

    if lesson:
        if lesson.obsazenost > capacity:
            return False, "Kapacita nemůže být menší než počet obsazených míst."
        else:
            lesson.kapacita = capacity
            database.session.commit()
            return True, "Kapacita byla úspěšně změněna."
        
    return False, "Hodina nebyla nalezena."

def lesson_instructor_change(lesson_id, instructor_id):

    lesson = database.session.query(DostupneHodiny).filter(DostupneHodiny.ID_hodiny == lesson_id).first()

    if lesson:
        query_lesson = database.session.query(DostupneHodiny)\
        .join(MaVypsane, DostupneHodiny.ID_hodiny == MaVypsane.ID_hodiny, isouter=True)\
        .filter(and_(
            DostupneHodiny.datum == lesson.datum, 
            DostupneHodiny.cas_zacatku == lesson.cas_zacatku,
            MaVypsane.ID_osoba == instructor_id
        ))\
        .first()

        if query_lesson:
            if query_lesson.stav == "obsazeno":
                status, message =  False, "Zvolený instruktor má již obsazenou hodinu s těmito parametry! Nelze proto obsadit."
            else:
                #hodina existuje, ale není obsazena, můžeme tak přepsat hodinu
                if lesson.stav == "obsazeno":
                    reservation = database.session.query(Prirazeno).filter(Prirazeno.ID_hodiny == lesson.ID_hodiny).first()
                    ma_vyuku_object = database.session.query(MaVyuku).filter(MaVyuku.ID_rezervace == reservation.ID_rezervace).first()
                    ma_vypsane_object = database.session.query(MaVypsane).filter(MaVypsane.ID_hodiny == lesson.ID_hodiny).first()

                    ma_vyuku_object.ID_osoba = instructor_id
                    ma_vypsane_object.ID_osoba = instructor_id

                if lesson.stav == "volno":
                    ma_vypsane_object = database.session.query(MaVypsane).filter(MaVypsane.ID_hodiny == lesson.ID_hodiny).first()
                    ma_vypsane_object.ID_osoba = instructor_id

                ma_vypsane_object = database.session.query(MaVypsane).filter(MaVypsane.ID_hodiny == query_lesson.ID_hodiny).first()
                database.session.delete(query_lesson)
                database.session.delete(ma_vypsane_object)
                #asi jeste odstraneni zaznamu z MaVypsane
                status, message = True, "Instruktor byl úspěšně změněn."
        else:
            #hodine neexistuje, můžeme vytvořit novou hodinu
            if lesson.stav == "obsazeno":
                reservation = database.session.query(Prirazeno).filter(Prirazeno.ID_hodiny == lesson.ID_hodiny).first()
                ma_vyuku_object = database.session.query(MaVyuku).filter(MaVyuku.ID_rezervace == reservation.ID_rezervace).first()
                ma_vypsane_object = database.session.query(MaVypsane).filter(MaVypsane.ID_hodiny == lesson.ID_hodiny).first()

                ma_vyuku_object.ID_osoba = instructor_id
                ma_vypsane_object.ID_osoba = instructor_id

            if lesson.stav == "volno":
                ma_vypsane_object = database.session.query(MaVypsane).filter(MaVypsane.ID_hodiny == lesson.ID_hodiny).first()
                ma_vypsane_object.ID_osoba = instructor_id
            
            status, message = True, "Instruktor byl úspěšně změněn."

    database.session.commit()
    return status, message

def check_instructor_client(email):
    client = database.session.query(Osoba).filter(Osoba.email == email).first()
    instructor_in_instructors = None
    if client: 
        return True
    #instructor_in_instructors = database.session.query(Instruktor).filter(Instruktor.ID_osoba == client.ID_osoba).first()
    #if instructor_in_instructors:
    #    return False
    return False

def change_instructor_check(email):
    instructor = database.session.query(Osoba).join(Instruktor, Instruktor.ID_osoba == Osoba.ID_osoba).filter(Osoba.email == email).first()
    return instructor

def update_instructor(instructor_id, form):
    fields_to_check = ['name', 'surname', 'email', 'tel_number']

    for field_name in fields_to_check:
        field_data = getattr(form, field_name).data
        if not field_data:
            return False, f"Pole '{field_name}' bylo ponecháno prázdné!"

    file = form.image.data
    filename = None
    if file and file.filename:
        if not allowed_file(file.filename):
            return False, "Soubor není povoleného typu!"
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

    instructor = database.session.query(Instruktor).join(Osoba).filter(Osoba.ID_osoba==instructor_id).first()

    if instructor:
        instructor.osoba.jmeno = form.name.data
        instructor.osoba.prijmeni = form.surname.data
        instructor.osoba.email = form.email.data
        instructor.osoba.tel_cislo = form.tel_number.data
        instructor.osoba.heslo = hash_password(form.password.data)
        if filename:
            instructor.image_path = filename
        instructor.popis = form.text.data
        database.session.commit()
        return True, "Instruktor byl úspěšně aktualizován."
    else:
        return False, "Instruktor nebyl nalezen!"


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_instructors_data():
    data = database.session.query(Instruktor).join(Osoba,Instruktor.ID_osoba==Osoba.ID_osoba).all()

    si = StringIO()
    cw = csv.writer(si)

    cw.writerow(['Name', 'Surname', 'Email'])

    for instructor in data:
        cw.writerow([instructor.osoba.jmeno, instructor.osoba.prijmeni, instructor.osoba.email])

    csv_content = "\ufeff" + si.getvalue()

    response = Response(csv_content, mimetype='text/csv', content_type='text/csv; charset=utf-8')
    response.headers['Content-Disposition'] = 'attachment; filename="instructors.csv"'
    return response

def generate_reservations_data():
    data = database.session.query(Rezervace).all()

    si = StringIO()
    cw = csv.writer(si)

    mapper = inspect(Rezervace)
    headers = [column.key for column in mapper.attrs]
    cw.writerow(headers)

    for instructor in data:
        row = [getattr(instructor, header) for header in headers]
        cw.writerow(row)

    csv_content = "\ufeff" + si.getvalue()
    response = Response(csv_content, mimetype='text/csv', content_type='text/csv; charset=utf-8')
    response.headers['Content-Disposition'] = 'attachment; filename="reservations.csv"'
    return response

def generate_instructors_overview():
    today = datetime.today()
    first_day_of_month = datetime(today.year, today.month, 1)
    last_day_of_month = datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

    query = database.session.query(
        Osoba.jmeno.label('first_name'),
        Osoba.prijmeni.label('last_name'),
        func.count().label('total_lessons'),
        func.sum(case((DostupneHodiny.typ_hodiny == 'ind', 1), else_=0)).label('individual_lessons'),
        func.sum(case((DostupneHodiny.typ_hodiny == 'group', 1), else_=0)).label('group_lessons'),
        func.sum(case((DostupneHodiny.typ_hodiny == 'group-ind', 1), else_=0)).label('group_lessons_individual')
    ).join(
        Instruktor, Osoba.ID_osoba == Instruktor.ID_osoba
    ).join(
        MaVypsane, Instruktor.ID_osoba == MaVypsane.ID_osoba
    ).join(
        DostupneHodiny, DostupneHodiny.ID_hodiny == MaVypsane.ID_hodiny
    ).filter(
        DostupneHodiny.stav == 'obsazeno',
        DostupneHodiny.datum >= first_day_of_month,
        DostupneHodiny.datum <= last_day_of_month
    ).group_by(
        Osoba.jmeno, Osoba.prijmeni
    )

    si = StringIO()
    cw = csv.writer(si)

    headers = ['Jméno', 'Příjmení', 'Celkový počet lekcí', 'individuální lekce', 'skupinové lekce', 'skupinové lekce individální']
    cw.writerow(headers)

    for row in query.all():
        cw.writerow([row.first_name, row.last_name, row.total_lessons, row.individual_lessons, row.group_lessons, row.group_lessons_individual])

    csv_content = "\ufeff" + si.getvalue()

    response = Response(csv_content, mimetype='text/csv', content_type='text/csv; charset=utf-8')
    response.headers['Content-Disposition'] = 'attachment; filename="instructors_overview.csv"'

    return response

def generate_reservations_overview():
    query = database.session.query(
        Rezervace.ID_rezervace,
        Rezervace.ID_osoba,
        Rezervace.typ_rezervace,
        Rezervace.termin,
        Rezervace.cas_zacatku,
        Rezervace.doba_vyuky,
        Rezervace.jazyk,
        Rezervace.pocet_zaku,
        Rezervace.platba,
        Rezervace.rezervacni_kod,
        Rezervace.poznamka
    )

    si = StringIO()
    cw = csv.writer(si)

    mapper = inspect(Rezervace)
    headers = [column.key for column in mapper.attrs]
    headers = headers[1:11]
    cw.writerow(headers)

    for reservation in query.all():

        row = [getattr(reservation, header) for header in headers]
        cw.writerow(row)

    csv_content = "\ufeff" + si.getvalue()

    response = Response(csv_content, mimetype='text/csv', content_type='text/csv; charset=utf-8')
    response.headers['Content-Disposition'] = 'attachment; filename="reservations_overview.csv"'

    return response

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