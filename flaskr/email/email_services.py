from flaskr.extensions import database
from flaskr.models import Instruktor, Osoba, MaVyuku

def get_instructor_email(reservation_id):
    query_result = database.session.query(Osoba).join(Instruktor, Instruktor.ID_osoba == Osoba.ID_osoba).join(MaVyuku, Osoba.ID_osoba==MaVyuku.ID_osoba).filter(MaVyuku.ID_rezervace==reservation_id).first()
    instructor_name = query_result.jmeno + " " + query_result.prijmeni
    return instructor_name