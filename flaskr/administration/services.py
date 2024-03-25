from flaskr.extensions import database
from flaskr.models import Instruktor, Osoba, MaVypsane, DostupneHodiny, Rezervace, Klient
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