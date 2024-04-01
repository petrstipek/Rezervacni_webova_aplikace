from flaskr.extensions import database
from flaskr.models import Osoba, Instruktor, MaVyuku

def instructor_has_lessons(instructor_id):
    query_result = database.session.query(MaVyuku).filter_by(ID_osoba=instructor_id).first()
    return query_result is not None

def delete_instructor_by_id(instructor_id):
    try:
        database.session.query(Instruktor).filter_by(ID_osoba=instructor_id).delete()
        database.session.query(Osoba).filter_by(ID_osoba=instructor_id).delete()
        database.session.commit()
    except Exception as e:
        database.session.rollback()
        return False, e
    return True

def get_all_paginated_instructors(page, per_page):
    query_result = database.session.query(Instruktor).paginate(page=page, per_page=per_page, error_out=False)

    instructors_list = []
    for instruktor in query_result:
        instruktor_dict = {
            'ID_osoba': instruktor.ID_osoba,
            'jmeno': instruktor.osoba.jmeno if instruktor.osoba else None,
            'prijmeni': instruktor.osoba.prijmeni if instruktor.osoba else None,
            "seniorita": instruktor.seniorita,
            "tel_cislo": instruktor.osoba.tel_cislo,
            "email": instruktor.osoba.email
        }
        instructors_list.append(instruktor_dict)
    print("pagination", instructors_list)
    return instructors_list

def get_all_instructors():
    query_result = database.session.query(Instruktor).all()

    instructors_list = []
    for instruktor in query_result:
        instruktor_dict = {
            'ID_osoba': instruktor.ID_osoba,
            'jmeno': instruktor.osoba.jmeno if instruktor.osoba else None,
            'prijmeni': instruktor.osoba.prijmeni if instruktor.osoba else None,
            "seniorita": instruktor.seniorita,
            "tel_cislo": instruktor.osoba.tel_cislo,
            "email": instruktor.osoba.email
        }
        instructors_list.append(instruktor_dict)
    return instructors_list

from flaskr.extensions import database
from flaskr.models import Rezervace, DostupneHodiny, MaVypsane, MaVyuku, Osoba, Zak, Instruktor
from sqlalchemy.orm import aliased
from flask_login import current_user

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

    
    base_query = base_query.filter(MaVyuku.ID_osoba == current_user.get_id())
    print(base_query)
    

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

def get_instructor_details(instructor_id):
    instructor = database.session.query(Osoba).join(Instruktor, Instruktor.ID_osoba == Osoba.ID_osoba).filter(Instruktor.ID_osoba == instructor_id).first()
    birth_date_str = instructor.instruktor.datum_narozeni.strftime('%Y-%m-%d') if instructor.instruktor.datum_narozeni else None
    start_work_str = instructor.instruktor.datum_nastupu.strftime('%Y-%m-%d') if instructor.instruktor.datum_nastupu else None
    instructor_dict = {
        'ID_osoba': instructor.ID_osoba,
        'jmeno': instructor.jmeno,
        'prijmeni': instructor.prijmeni,
        'seniorita': instructor.instruktor.seniorita,
        'tel_cislo': instructor.tel_cislo,
        'email': instructor.email,
        'birth_date': birth_date_str,
        'start_work': start_work_str,
    }
    return instructor_dict

def instructors_count():
    return database.session.query(Instruktor).count()
