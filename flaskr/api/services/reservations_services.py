from flaskr.db import get_db
import sqlite3
from datetime import datetime, timedelta, date, time
from flaskr.extensions import database
from flaskr.models import Klient, Rezervace, Instruktor, MaVyuku, Osoba, Prirazeno, DostupneHodiny, MaVypsane, Zak
from sqlalchemy.orm import aliased
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

def delete_reservation_by_reservation_code(reservation_id):
    try:
        reservation = database.session.query(Rezervace).filter_by(rezervacni_kod=reservation_id).first()
        if reservation is None:
            return False, "Rezervace nebyla nalezena!"

        today = datetime.now().date()
        combined_datetime_str = f'{reservation.termin} {reservation.cas_zacatku}'
        time_now = datetime.now()
        lesson_time = datetime.strptime(combined_datetime_str, '%Y-%m-%d %H:%M:%S')
        time_difference = lesson_time - time_now

        if time_difference < timedelta(hours=2):
            return False, "Rezervace nemůže být zrušena! Zbývá méně jak 2 hodiny do hodiny."

        reservation_id = reservation.ID_rezervace

        if reservation.typ_rezervace == "individual":
            lessons = database.session.query(Prirazeno).filter_by(ID_rezervace=reservation_id).all()
            for lesson in lessons:
                database.session.query(DostupneHodiny).filter_by(ID_hodiny=lesson.ID_hodiny).update({"stav" : "volno"})

            zak_ids = database.session.query(Zak).filter_by(ID_rezervace=reservation_id).all()
            zak_ids = [id_tuple.ID_zak for id_tuple in zak_ids]

            for zak_id in zak_ids:
                database.session.query(Zak).filter_by(ID_zak=zak_id).delete()
            
            database.session.query(Rezervace).filter_by(ID_rezervace=reservation_id).delete()
            database.session.query(Prirazeno).filter_by(ID_rezervace=reservation_id).delete()
            database.session.query(MaVyuku).filter_by(ID_rezervace=reservation_id).delete()

            database.session.commit()

        elif reservation.typ_rezervace == "group":
            student_count = reservation.pocet_zaku
            lesson_group = database.session.query(Prirazeno).filter_by(ID_rezervace=reservation_id).first()
            lesson = database.session.query(DostupneHodiny).filter_by(ID_hodiny=lesson_group.ID_hodiny).first()
            lesson_occupancy = lesson.obsazenost
            new_availability = lesson_occupancy - student_count
            database.session.query(DostupneHodiny).filter_by(ID_hodiny=lesson_group.ID_hodiny).update({"obsazenost": new_availability})

            zak_ids = database.session.query(Zak).filter_by(ID_rezervace=reservation_id).all()
            zak_ids = [id_tuple.ID_zak for id_tuple in zak_ids]

            for zak_id in zak_ids:
                database.session.query(Zak).filter_by(ID_zak=zak_id).delete()

            database.session.query(Rezervace).filter_by(ID_rezervace=reservation_id).delete()
            database.session.query(Prirazeno).filter_by(ID_rezervace=reservation_id).delete()
            database.session.query(MaVyuku).filter_by(ID_rezervace=reservation_id).delete()

            database.session.commit()

        return True, "Ok"
    except sqlite3.Error as e:
        database.session.rollback()
        return False, "nok"
    
def delete_reservation_by_reservation_id(reservation_id):
    try:
        reservation = database.session.query(Rezervace).filter_by(ID_rezervace=reservation_id).first()
        if reservation is None:
            return False, "Rezervace nebyla nalezena!"

        today = datetime.now().date()
        combined_datetime_str = f'{reservation.termin} {reservation.cas_zacatku}'
        time_now = datetime.now()
        lesson_time = datetime.strptime(combined_datetime_str, '%Y-%m-%d %H:%M:%S')
        time_difference = lesson_time - time_now

        if time_difference < timedelta(hours=2):
            return False, "Rezervace nemůže být zrušena! Zbývá méně jak 2 hodiny do hodiny."

        if reservation.typ_rezervace == "individual":
            lessons = database.session.query(Prirazeno).filter_by(ID_rezervace=reservation_id).all()
            for lesson in lessons:
                database.session.query(DostupneHodiny).filter_by(ID_hodiny=lesson.ID_hodiny).update({"stav" : "volno"})

            zak_ids = database.session.query(Zak).filter_by(ID_rezervace=reservation_id).all()
            zak_ids = [id_tuple.ID_zak for id_tuple in zak_ids]

            for zak_id in zak_ids:
                database.session.query(Zak).filter_by(ID_zak=zak_id).delete()
            
            database.session.query(Rezervace).filter_by(ID_rezervace=reservation_id).delete()
            database.session.query(Prirazeno).filter_by(ID_rezervace=reservation_id).delete()
            database.session.query(MaVyuku).filter_by(ID_rezervace=reservation_id).delete()

            database.session.commit()

        elif reservation.typ_rezervace == "group":
            student_count = reservation.pocet_zaku
            lesson_group = database.session.query(Prirazeno).filter_by(ID_rezervace=reservation_id).first()
            lesson = database.session.query(DostupneHodiny).filter_by(ID_hodiny=lesson_group.ID_hodiny).first()
            lesson_occupancy = lesson.obsazenost
            new_availability = lesson_occupancy - student_count
            database.session.query(DostupneHodiny).filter_by(ID_hodiny=lesson_group.ID_hodiny).update({"obsazenost": new_availability})

            zak_ids = database.session.query(Zak).filter_by(ID_rezervace=reservation_id).all()
            zak_ids = [id_tuple.ID_zak for id_tuple in zak_ids]

            for zak_id in zak_ids:
                database.session.query(Zak).filter_by(ID_zak=zak_id).delete()

            database.session.query(Rezervace).filter_by(ID_rezervace=reservation_id).delete()
            database.session.query(Prirazeno).filter_by(ID_rezervace=reservation_id).delete()
            database.session.query(MaVyuku).filter_by(ID_rezervace=reservation_id).delete()

            database.session.commit()

        return True, "Ok"
    except sqlite3.Error as e:
        database.session.rollback()
        return False, "nok"
    
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
        InstruktorOsoba.prijmeni.label('příjmení instruktora'),
        Rezervace.platba.label('stav platby')
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
        'ID_rezervace': lesson[0],
        'jméno klienta': lesson[1],
        'příjmení klienta': lesson[2],
        'termín rezervace': lesson[3].isoformat() if lesson[3] else '',
        'čas začátku': lesson[4].strftime('%H:%M') if lesson[4] else '',
        'doba výuky': lesson[5],
        'jméno instruktora': lesson[6],
        'příjmení instruktora': lesson[7],
        'stav platby': lesson[8]
    } for lesson in lessons]

    return {
        "reservations": results_list,
        "total_items": total_items,
        "total_pages": (total_items + per_page - 1) // per_page,
        "current_page": page
    }, None
    
def fetch_available_group_times():

    query_result = database.session.query(
        DostupneHodiny.datum,
        DostupneHodiny.cas_zacatku,
        (DostupneHodiny.kapacita - DostupneHodiny.obsazenost).label('count')
    ).filter(
        DostupneHodiny.stav == 'volno',
        DostupneHodiny.typ_hodiny == 'group',
        DostupneHodiny.obsazenost < DostupneHodiny.kapacita
    ).group_by(
        DostupneHodiny.datum, DostupneHodiny.cas_zacatku
    ).order_by(
        DostupneHodiny.datum, DostupneHodiny.cas_zacatku
    ).all()

    return query_result

def format_available_times(query_results):
    available_times = {}
    for row in query_results:
        date_str = row[0].strftime('%Y-%m-%d')  
        time_str = row[1].strftime('%H:%M')   
        count = row[2]                        

        if date_str not in available_times:
            available_times[date_str] = []

        available_times[date_str].append((time_str, count))

    return available_times

def fetch_available_times_for_individual_instructor(instructor_id=None):
    base_query = database.session.query(
        DostupneHodiny.datum,
        DostupneHodiny.cas_zacatku,
        func.count().label('count')
    ).outerjoin(MaVypsane, DostupneHodiny.ID_hodiny == MaVypsane.ID_hodiny)\
    .filter(DostupneHodiny.stav == 'volno', DostupneHodiny.typ_hodiny == 'ind')
    
    if instructor_id and instructor_id != 0:
        base_query = base_query.filter(MaVypsane.ID_osoba == instructor_id)

    query_result = base_query.group_by(DostupneHodiny.datum, DostupneHodiny.cas_zacatku).order_by(DostupneHodiny.datum, DostupneHodiny.cas_zacatku).all()
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