from flaskr.extensions import database
from flaskr.models.instructor import Instruktor
from flaskr.models.user import Osoba

def get_all_instructors():
    query_result = database.session.query(Instruktor).join(Osoba, Instruktor.ID_osoba == Osoba.ID_osoba).all()
    return query_result
