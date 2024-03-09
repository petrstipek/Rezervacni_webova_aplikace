from flaskr.extensions import database
from flaskr.models import Osoba, Instruktor, MaVyuku

def instructor_has_lessons(instructor_id):
    query_result = database.session.query(MaVyuku).filter_by(ID_osoba=instructor_id)
    return query_result is not None

def delete_instructor_by_id(instructor_id):
    try:
        database.session.query(Instruktor).filter_by(ID_osoba=instructor_id).delete()
        database.session.commit()
    except Exception as e:
        database.session.rollback()
        return False, e
    return True

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