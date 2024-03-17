from flaskr.db import get_db
from flaskr.extensions import database
from flaskr.models import Instruktor, Osoba, MaVypsane, DostupneHodiny, Rezervace, Klient
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import and_


def instructor_exists(email):
    #db = get_db()
    #query_result = db.execute('SELECT * FROM Instruktor WHERE email = ?', (email, )).fetchone()
    query_result = database.session.query(Instruktor) \
                .join(Osoba) \
                .filter(Osoba.email == email) \
                .options(joinedload(Instruktor.osoba)) \
                .first()
    return query_result is not None

def add_instructor(name, surname, email, tel_number, experience, date_birth, date_started):
    #db = get_db()
    #db.execute('INSERT INTO Instruktor (jmeno, prijmeni, email, tel_cislo, seniorita, datum_narozeni, datum_nastupu) VALUES (?, ?, ?, ?, ?, ?, ?)', (name, surname, email, tel_number, experience, date_birth, date_started) )
    #db.commit()

    new_osoba = Osoba(jmeno=name, prijmeni=surname, email=email, tel_cislo=tel_number,)

    database.session.add(new_osoba)
    database.session.flush()

    new_instruktor = Instruktor(ID_osoba=new_osoba.ID_osoba, seniorita=experience, datum_narozeni=date_birth, datum_nastupu=date_started)
    database.session.add(new_instruktor)
    database.session.commit()


def get_available_instructors():
    #db = get_db()
    #query_result_instructors = db.execute("SELECT DISTINCT jmeno, prijmeni, ID_osoba from instruktor")

    query_result_instructors = database.session.query(Instruktor.ID_osoba, Osoba.jmeno, Osoba.prijmeni)\
        .join(Osoba, Instruktor.ID_osoba == Osoba.ID_osoba).distinct()
    
    available_instructors = [(0, "Instruktor")]
    for row in query_result_instructors:
        available_instructors.append((row.ID_osoba ,row.jmeno + " " + row.prijmeni))
    return available_instructors

def add_individual_lesson(db, date_str, time_start, instructor_id, lesson_type, capacity):
    #query_result = db.execute('SELECT * from Dostupne_hodiny left join ma_vypsane using (ID_hodiny) WHERE datum = ? AND cas_zacatku = ? AND ID_osoba = ?', (date_str, time_start, instructor_id)).fetchone()

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
    
    #cursor = db.execute('INSERT INTO Dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny, kapacita) VALUES (?, ?, ?, ?, ?)', (date_str, time_start, "volno", lesson_type, capacity))
    #last_row = cursor.lastrowid
    #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)',(int(instructor_id), last_row))
    #db.commit()
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

    #cursor = db.execute('INSERT INTO Dostupne_hodiny (datum, cas_zacatku, stav, typ_hodiny, kapacita, obsazenost) VALUES (?, ?, ?, ?, ?, ?)', (date_str, time_start, "volno", lesson_type, capacity, 0))
    #last_row = cursor.lastrowid
    for instructor_id in instructor_ids:
        #db.execute('INSERT INTO ma_vypsane (ID_osoba, ID_hodiny) VALUES (?, ?)',(int(instructor_id), last_row))

        new_ma_vypsane = MaVypsane(
            ID_osoba=instructor_id,
            ID_hodiny=new_lesson.ID_hodiny
        )
        database.session.add(new_ma_vypsane)

    #db.commit()
    database.session.commit()
    return True, "Lesson added successfully"

def get_reservations():
    query_result = database.session.query(Rezervace).join(Klient, Rezervace.ID_osoba == Klient.ID_osoba).all()

    return [dict(row) for row in query_result]

def get_reservation_payment_status(reservation_id):
    #db = get_db()
    #reservation = db.execute('SELECT platba FROM rezervace WHERE ID_rezervace = ?', (reservation_id,)).fetchone()
    reservation = database.session.query(Rezervace.platba).filter_by(ID_rezervace=reservation_id).first()
    return reservation

def mark_reservation_as_paid(reservation_id):
    #db = get_db()
    #db.execute('UPDATE rezervace SET platba = "zaplaceno" WHERE ID_rezervace = ?', (reservation_id,))
    #db.commit()

    database.session.query(Rezervace).filter_by(ID_rezervace=reservation_id).update({"platba" : "zaplaceno"})
    database.session.commit()

def get_lesson_status(lesson_id):
    query_result = database.session.query(DostupneHodiny.stav).filter_by(ID_hodiny=lesson_id).first()
    return query_result

def delete_lesson(lesson_id):
    database.session.query(DostupneHodiny).filter_by(ID_hodiny=lesson_id).delete()
    database.session.query(MaVypsane).filter_by(ID_hodiny=lesson_id).delete()
    database.session.commit()


def get_all_lessons():
    #nepouziva se?
    #db = get_db()
    #query_result = db.execute('SELECT * FROM dostupne_hodiny LEFT JOIN ma_vypsane USING (ID_hodiny) left join Instruktor USING (ID_osoba)').fetchall()
    
    query_result = database.session.query(DostupneHodiny) \
        .outerjoin(MaVypsane, DostupneHodiny.ID_hodiny == MaVypsane.ID_hodiny) \
        .outerjoin(Instruktor, MaVypsane.ID_osoba == Instruktor.ID_osoba) \
        .outerjoin(Osoba, Instruktor.ID_osoba == Osoba.ID_osoba) \
        .all()

    lessons_list = []

    for dostupne_hodiny in query_result:
        instructors_list = [
            {
                'ID_osoba': ma_vypsane.instruktor.ID_osoba,
                'jmeno': ma_vypsane.instruktor.osoba.jmeno,
                'prijmeni': ma_vypsane.instruktor.osoba.prijmeni 
            }
            for ma_vypsane in dostupne_hodiny.ma_vypsane if ma_vypsane.instruktor and ma_vypsane.instruktor.osoba
        ]

        lesson_dict = {
            'ID_hodiny': dostupne_hodiny.ID_hodiny,
            'datum': dostupne_hodiny.datum,
            'cas_zacatku': dostupne_hodiny.cas_zacatku,
            'typ_hodiny': dostupne_hodiny.typ_hodiny,
            'kapacita': dostupne_hodiny.kapacita,
            'instruktors': instructors_list
        }
        lessons_list.append(lesson_dict)

    return lessons_list