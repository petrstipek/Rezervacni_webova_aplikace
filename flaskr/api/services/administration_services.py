from flaskr.extensions import database
from flaskr.models import Rezervace, DostupneHodiny, MaVypsane, MaVyuku, Osoba, Zak, Instruktor
from sqlalchemy.orm import aliased
from datetime import datetime


def get_reservation_payment_status(reservation_id):
    reservation = database.session.query(Rezervace.platba).filter_by(ID_rezervace=reservation_id).first()
    return reservation

def get_lesson_status(lesson_id):
    query_result = database.session.query(DostupneHodiny.stav).filter_by(ID_hodiny=lesson_id).first()
    return query_result

def mark_reservation_as_paid(reservation_id):
    database.session.query(Rezervace).filter_by(ID_rezervace=reservation_id).update({"platba" : "zaplaceno"})
    database.session.commit()

def delete_lesson(lesson_id):
    database.session.query(DostupneHodiny).filter_by(ID_hodiny=lesson_id).delete()
    database.session.query(MaVypsane).filter_by(ID_hodiny=lesson_id).delete()
    database.session.commit()

def get_paginated_reservation_details(page, per_page, identifier=None, identifier_type=None, selected_date=None):
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
    if selected_date:
        base_query = base_query.filter(Rezervace.termin == selected_date)

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


def get_reservation_details(reservation_id):
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
            'prijmeni_instruktora' : instructor_query.osoba.prijmeni
        }

    zaks = database.session.query(Zak).filter(Zak.ID_rezervace == reservation_id).all()
    zak_list = [{'ID_zak': zak.ID_zak, 'jmeno_zak': zak.jmeno, 'prijmeni_zak': zak.prijmeni, 'vek_zak': zak.vek, 'zkusenost_zak': zak.zkusenost} for zak in zaks]

    combined_details = {
        **reservation_detail, 
        'Instructor': instructor_detail,
        'Zak': zak_list
    }
    return combined_details


def get_school_information():
    today = datetime.today().date()
    reservation_count = database.session.query(Rezervace).filter(Rezervace.termin==today).count()
    print(reservation_count)

    available_times_count = database.session.query(DostupneHodiny).filter(DostupneHodiny.obsazenost=="volno").count()
    print(available_times_count)

