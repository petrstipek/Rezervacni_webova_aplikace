from flaskr.db import get_db
import sqlite3
from datetime import datetime, timedelta, date, time
from flaskr.extensions import database
from flaskr.models import Klient, Rezervace, Instruktor, MaVyuku, Osoba, Prirazeno, DostupneHodiny
from sqlalchemy.orm import aliased
from sqlalchemy.exc import SQLAlchemyError

def delete_reservation_by_reservation_code(reservation_id):
    db = get_db()
    cur = db.cursor()
    
    try:
        cur.execute("SELECT 1 FROM rezervace WHERE rezervacni_kod = ?", (reservation_id,))
        if cur.fetchone() is None:
            return False, "Rezervace nebyla nalezena!"
        query_result = db.execute("SELECT * FROM rezervace WHERE rezervacni_kod = ?", (reservation_id,)).fetchone()

        today = datetime.now().date()
        combined_datetime_str = f'{query_result["termin"]} {query_result["cas_zacatku"]}'
        time_now = datetime.now()
        lesson_time = datetime.strptime(combined_datetime_str, '%Y-%m-%d %H:%M')
        time_difference = lesson_time - time_now

        if time_difference < timedelta(hours=2):
            print("jo jsem tady")
            return False, "Rezervace nemůže být zrušena! Zbývá méně jak 2 hodiny do hodiny."

        lesson_id = db.execute("select * from rezervace left join prirazeno using (ID_rezervace) left join Dostupne_hodiny using (ID_hodiny) where rezervacni_kod = ? ", (reservation_id,)).fetchone()
        reservation_id = query_result["ID_rezervace"]

        if query_result["typ_rezervace"] == "individual":
            lesson_ids = cur.execute("SELECT ID_hodiny from prirazeno WHERE ID_rezervace = ?", (reservation_id,)).fetchall()
            for lesson_id_tuple in lesson_ids:
                cur.execute("UPDATE Dostupne_hodiny SET stav = 'volno' WHERE ID_hodiny = ?", (lesson_id_tuple[0],))
            
            cur.execute("DELETE FROM rezervace WHERE ID_rezervace = ?", (reservation_id,))
            cur.execute("DELETE from prirazeno WHERE ID_rezervace = ?", (reservation_id,))
            cur.execute("DELETE from ma_vyuku WHERE ID_rezervace = ?", (reservation_id,))
            db.commit()
        elif query_result["typ_rezervace"] == "group":
            student_count = query_result["pocet_zaku"]
            lesson = db.execute("SELECT * from Dostupne_hodiny WHERE ID_hodiny = ?", (lesson_id["ID_hodiny"],)).fetchone()
            lesson_occupancy = lesson["obsazenost"]
            new_availability = lesson_occupancy - student_count
            db.execute("UPDATE Dostupne_hodiny SET obsazenost = ? WHERE ID_hodiny = ?", (new_availability, lesson["ID_hodiny"],))

            cur.execute("DELETE FROM rezervace WHERE ID_rezervace = ?", (reservation_id,))
            cur.execute("DELETE from prirazeno WHERE ID_rezervace = ?", (reservation_id,))
            cur.execute("DELETE from ma_vyuku WHERE ID_rezervace = ?", (reservation_id,))

            db.commit()

        return True, "Ok"
    except sqlite3.Error as e:
        db.rollback()
        return False, "nok"
    
def delete_reservation_by_reservation_id(reservation_id):
    try:
        reservation = database.session.query(Rezervace).filter_by(ID_rezervace=reservation_id).first()
        if reservation is None:
            return False, "Rezervace nebyla nalezena!"

        lesson_ids = database.session.query(Prirazeno.ID_hodiny).filter_by(ID_rezervace=reservation_id).all()
        lesson_ids = [id_tuple[0] for id_tuple in lesson_ids]
        
        database.session.query(DostupneHodiny).filter(DostupneHodiny.ID_hodiny.in_(lesson_ids)).update({'stav': 'volno'}, synchronize_session='fetch')
        
        database.session.query(Rezervace).filter_by(ID_rezervace=reservation_id).delete()
        database.session.query(Prirazeno).filter_by(ID_rezervace=reservation_id).delete()
        database.session.query(MaVyuku).filter_by(ID_rezervace=reservation_id).delete()

        database.session.commit()

        return True, "Ok"
    except SQLAlchemyError as e:
        database.session.rollback()
        return False, str(e)
    
def get_paginated_reservation_details(page, per_page, identifier=None, identifier_type=None):
    KlientOsoba = aliased(Osoba)
    InstruktorOsoba = aliased(Osoba)

    base_query = database.session.query(
        Rezervace.ID_rezervace,
        KlientOsoba.jmeno.label('jméno klienta'),
        KlientOsoba.prijmeni.label('příjmení klienta'),
        Rezervace.termin.label('termín rezervace'),
        Rezervace.cas_zacatku.label('čas začátku'),
        Rezervace.doba_vyuky.label('doba výuky'),
        InstruktorOsoba.jmeno.label('jméno instruktora'),
        InstruktorOsoba.prijmeni.label('příjmení instruktora')
    ).join(KlientOsoba, Rezervace.ID_osoba == KlientOsoba.ID_osoba)\
    .outerjoin(MaVyuku, Rezervace.ID_rezervace == MaVyuku.ID_rezervace)\
    .outerjoin(InstruktorOsoba, MaVyuku.ID_osoba == InstruktorOsoba.ID_osoba)

    if identifier_type and identifier:
        if identifier_type == 'reservationID':
            base_query = base_query.filter(Rezervace.rezervacni_kod == identifier)
        elif identifier_type == 'name':
            base_query = base_query.filter(KlientOsoba.prijmeni == identifier)
        elif identifier_type == 'email':
            base_query = base_query.filter(KlientOsoba.email == identifier)
        elif identifier_type == 'tel-number':
            base_query = base_query.filter(KlientOsoba.tel_cislo == identifier)

    total_items = base_query.count()
    lessons = base_query.order_by(Rezervace.termin, Rezervace.cas_zacatku)\
                        .limit(per_page)\
                        .offset((page - 1) * per_page)\
                        .all()

    results_list = [{
        'jméno klienta': lesson[1],
        'příjmení klienta': lesson[2],
        'termín rezervace': lesson[3].isoformat() if lesson[3] else '',
        'čas začátku': lesson[4].strftime('%H:%M') if lesson[4] else '',
        'doba výuky': lesson[5],
        'jméno instruktora': lesson[6],
        'příjmení instruktora': lesson[7]
    } for lesson in lessons]

    return {
        "reservations": results_list,
        "total_items": total_items,
        "total_pages": (total_items + per_page - 1) // per_page,
        "current_page": page
    }, None
    
def fetch_available_group_times():
    db = get_db()
    query_result = db.execute("""
        SELECT datum, cas_zacatku, (kapacita - obsazenost) as count
        FROM dostupne_hodiny
        WHERE stav = 'volno' AND typ_hodiny = 'group' AND obsazenost < kapacita
        GROUP BY datum, cas_zacatku
        ORDER BY datum, cas_zacatku;
    """).fetchall()
    return query_result

def format_available_times(query_results):
    available_times = {}
    for row in query_results:
        date_str = row['datum'].strftime('%Y-%m-%d')
        time_str = row['cas_zacatku']
        count = row['count']
        
        if date_str not in available_times:
            available_times[date_str] = []
        
        available_times[date_str].append((time_str, count))
    
    return available_times

def fetch_available_times_for_individual_instructor(instructor_id=None):
    db = get_db()
    base_query = """
        SELECT datum, cas_zacatku, COUNT(*) as count
        FROM dostupne_hodiny LEFT JOIN ma_vypsane USING (ID_hodiny)
        WHERE stav = 'volno' AND typ_hodiny = 'ind'
    """
    parameters = ()
    if instructor_id and instructor_id != 0:
        base_query += " AND ID_osoba = ?"
        parameters = (instructor_id,)
    
    base_query += " GROUP BY datum, cas_zacatku ORDER BY datum, cas_zacatku"
    query_result = db.execute(base_query, parameters).fetchall()
    return query_result

def get_reservation_detail(identifier):
    query_result = database.session.query(
        Rezervace.termin,
        Rezervace.cas_zacatku,
        Rezervace.pocet_zaku,
        Rezervace.doba_vyuky,
        Rezervace.platba
    ).outerjoin(Instruktor, Rezervace.ID_osoba == Instruktor.ID_osoba)\
    .filter(Rezervace.rezervacni_kod == identifier)\
    .first()

    columns = ["Termín", "Čas začátku", "Počet žáků", "Doba výuky", "Stav platby"]
    
    if query_result:
        result_dict = {}
        attrs = ['termin', 'cas_zacatku', 'pocet_zaku', 'doba_vyuky', 'platba']
        for i, column in enumerate(columns):
            value = getattr(query_result, attrs[i])
            if isinstance(value, date):
                formatted_date = value.strftime('%d.%m.%Y')
                result_dict[column] = formatted_date
            elif isinstance(value, time):
                formatted_time = value.strftime('%H:%M')
                result_dict[column] = formatted_time
            else:
                result_dict[column] = value
        return result_dict

    return False