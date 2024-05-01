from flaskr.extensions import database
from flaskr.models.instructor import Instruktor
from flaskr.models.user import Osoba
from flaskr.models.reservation import Rezervace, MaVyuku

def get_instructor_email(reservation_id):
    query_result = database.session.query(Osoba).join(Instruktor, Instruktor.ID_osoba == Osoba.ID_osoba).join(MaVyuku, Osoba.ID_osoba==MaVyuku.ID_osoba).filter(MaVyuku.ID_rezervace==reservation_id).all()
    instructors = []
    for instructor in query_result:
        instructors.append(instructor.jmeno + " " + instructor.prijmeni)   
    return instructors

def get_reservation_code(reservation_id):
    query_result = database.session.query(Rezervace).filter(Rezervace.ID_rezervace==reservation_id).first()
    return query_result.rezervacni_kod