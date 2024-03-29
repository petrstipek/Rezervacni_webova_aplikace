from flaskr.extensions import database
from flaskr.models import Instruktor, Osoba, MaVypsane, DostupneHodiny, Rezervace, Klient, Zak, MaVyuku
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from datetime import datetime, timedelta
from sqlalchemy import func


def instructor_exists(email):
    query_result = database.session.query(Instruktor) \
                .join(Osoba) \
                .filter(Osoba.email == email) \
                .options(joinedload(Instruktor.osoba)) \
                .first()
    return query_result is not None

def add_instructor(name, surname, email, tel_number, experience, date_birth, date_started):
    new_osoba = Osoba(jmeno=name, prijmeni=surname, email=email, tel_cislo=tel_number,)

    database.session.add(new_osoba)
    database.session.flush()

    new_instruktor = Instruktor(ID_osoba=new_osoba.ID_osoba, seniorita=experience, datum_narozeni=date_birth, datum_nastupu=date_started)
    database.session.add(new_instruktor)
    database.session.commit()


def get_available_instructors():
    query_result_instructors = database.session.query(Instruktor.ID_osoba, Osoba.jmeno, Osoba.prijmeni)\
        .join(Osoba, Instruktor.ID_osoba == Osoba.ID_osoba).distinct()
    
    available_instructors = [(0, "Instruktor")]
    for row in query_result_instructors:
        available_instructors.append((row.ID_osoba ,row.jmeno + " " + row.prijmeni))
    return available_instructors

def add_individual_lesson(db, date_str, time_start, instructor_id, lesson_type, capacity):

    query_result = database.session.query(DostupneHodiny)\
    .join(MaVypsane, DostupneHodiny.ID_hodiny == MaVypsane.ID_hodiny, isouter=True)\
    .filter(and_(
        DostupneHodiny.datum == date_str, 
        DostupneHodiny.cas_zacatku == time_start,
        MaVypsane.ID_osoba == instructor_id
    ))\
    .first()

    if query_result:
        return False, "Lesson already exists for these parameters"
    
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
    
    return True, "Lesson added successfully"

def add_group_lesson(db, date_str, time_start, instructor_ids, lesson_type, capacity):
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
            return False, "Lesson already exists for these parameters - instructor: " + instructor_id
        
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
    return True, "Lesson added successfully"

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

def prepare_data_for_graph(counts):
    dates = [datetime.strptime(result[0], "%Y-%m-%d").strftime("%Y-%m-%d") if isinstance(result[0], str) else result[0].strftime("%Y-%m-%d") for result in counts]
    reservation_counts = [result[1] for result in counts]

    return dates, reservation_counts

def process_reservation_change(form, reservation_id):
    print("jsem tady",reservation_id)
    query_result = database.session.query(Rezervace).filter(Rezervace.ID_rezervace == reservation_id).first()

    student_array = [form.name.data, form.name_client1.data, form.name_client2.data]
    filtered_array = [student for student in student_array if student is not None]
    length = len(filtered_array)

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

    print("students_info", students_info)

    if not query_result:
        return False, "Rezervace nebyla nalezena, opakujte akci!"
    zkus = True
    #if query_result.cas_zacatku == form.reservation_time.data and query_result.termin == form.reservation_date.data and query_result.pocet_zaku == length:
    if zkus:   
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
        print("updated before students loop", updated)
        print("form_students", form_students)
        print("students_info", students_info)
        for form_student, student_info in zip(form_students, students_info):
            student = database.session.query(Zak).filter(Zak.ID_zak == student_info["id_student"]).first()
            if student:
                if form_student["name"] != student.jmeno and form_student["name"] != "":
                    print("studentjmeno", student.jmeno)
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
        

    if updated:
        try:
            database.session.commit()
            return True, "Rezervace byla úspěšně aktualizována."
        except Exception as e:
            database.session.rollback()
            return False, "Nepodařilo se aktualizovat rezervaci."

    return True, "Nebyly provedeny žádné změny."


def get_reservation_details(reservation_id):
    reservation_detail = {}
    instructor_detail = {}

    reservation_query = database.session.query(Rezervace).outerjoin(Osoba, Rezervace.ID_osoba==Osoba.ID_osoba).filter(Rezervace.ID_rezervace==reservation_id).first()
    if reservation_query:
        reservation_detail = {
            'ID_rezervace': reservation_query.rezervacni_kod,
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
