from flaskr.db import get_db
import sqlite3
from datetime import datetime, timedelta, date, time
from flaskr.extensions import database
from flaskr.models import Klient, Rezervace, Instruktor, MaVyuku, Osoba, Prirazeno, DostupneHodiny, MaVypsane, Zak
from sqlalchemy.orm import aliased
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from flaskr.email.email import send_reservation_cancelation

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
        reservation_code = reservation.rezervacni_kod
        payment = reservation.platba

        client = database.session.query(Klient).join(Osoba, Klient.ID_osoba==Osoba.ID_osoba).filter(Osoba.ID_osoba==reservation.ID_osoba).first()
        email = client.osoba.email

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

        return True, "Ok", reservation_code, email, payment
    except sqlite3.Error as e:
        database.session.rollback()
        return False, "nok", reservation_code, email, payment
    
def delete_reservation_by_reservation_id(reservation_id):
    try:
        reservation = database.session.query(Rezervace).filter_by(ID_rezervace=reservation_id).first()
        if reservation is None:
            return False, "Rezervace nebyla nalezena!"

        client = database.session.query(Klient).join(Osoba, Klient.ID_osoba==Osoba.ID_osoba).filter(Osoba.ID_osoba==reservation.ID_osoba).first()
        email = client.osoba.email
        reservation_code = reservation.rezervacni_kod
        payment = reservation.platba
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

        print("jsem teaady")
        print(email, reservation_code, payment)
        send_reservation_cancelation(email, reservation_code, payment)

        return True, "Ok"
    except sqlite3.Error as e:
        database.session.rollback()
        return False, "nok"
    
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

def fetch_available_times_for_individual_instructor(instructor_id=None, date=None):
    today = datetime.today()
    base_query = database.session.query(
        DostupneHodiny.datum,
        DostupneHodiny.cas_zacatku,
        func.count().label('count')
    ).outerjoin(MaVypsane, DostupneHodiny.ID_hodiny == MaVypsane.ID_hodiny)\
    .filter(DostupneHodiny.stav == 'volno', DostupneHodiny.typ_hodiny == 'ind').filter(DostupneHodiny.datum >= today).filter(DostupneHodiny.datum==date)
    
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