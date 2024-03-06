from flaskr.db import get_db
from flaskr.extensions import database
from flaskr.models import Osoba, Instruktor

def instructor_has_lessons(instructor_id):
    db = get_db()
    query_result = db.execute('SELECT * FROM ma_vyuku WHERE ID_osoba = ?', (instructor_id,)).fetchone()
    return query_result is not None

def delete_instructor_by_id(instructor_id):
    db = get_db()
    try:
        db.execute('DELETE FROM Instruktor WHERE ID_osoba = ?', (instructor_id,))
        db.commit()
    except Exception as e:
        db.rollback()  
        return False, e
    return True

def get_all_instructors():
    #db = get_db()
    #query_result = db.execute('SELECT * FROM Instruktor').fetchall()
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
    return [dict(row) for row in query_result]