from flaskr.db import get_db
from flaskr.extensions import database
from flaskr.models import DostupneHodiny, MaVypsane, Instruktor, Osoba
from datetime import date, time

def get_paginated_lessons(page, per_page, selected_date=None):
    base_query = database.session.query(
            DostupneHodiny.ID_hodiny,
            DostupneHodiny.datum,
            DostupneHodiny.cas_zacatku,
            Osoba.jmeno,
            Osoba.prijmeni,
            DostupneHodiny.stav,
            DostupneHodiny.typ_hodiny,
            (DostupneHodiny.kapacita - DostupneHodiny.obsazenost).label('Zbyvajici')
        ).outerjoin(MaVypsane, DostupneHodiny.ID_hodiny == MaVypsane.ID_hodiny
        ).outerjoin(Instruktor, MaVypsane.ID_osoba == Instruktor.ID_osoba
        ).outerjoin(Osoba, Instruktor.ID_osoba == Osoba.ID_osoba)
    if selected_date:
        filtered_query = base_query.filter(DostupneHodiny.datum == selected_date)
        lessons = filtered_query.limit(per_page).offset((page - 1) * per_page).all()
        total = filtered_query.count()
    else:
        lessons = base_query.limit(per_page).offset((page - 1) * per_page).all()
        total = base_query.count()

    results_list = []
    for lesson in lessons:
        lesson_dict = {
            'ID_hodiny': lesson[0],
            'Termín': lesson[1].strftime('%Y-%m-%d') if isinstance(lesson[1], date) else lesson[1],
            'Čas začátku': lesson[2].strftime('%H:%M') if isinstance(lesson[2], time) else lesson[2], 
            'Jméno': lesson[3],
            'Příjmení': lesson[4],
            'Stav': lesson[5],
            'Typ hodiny': lesson[6],
            'Zbývající kapacita': lesson[7]
        }
        results_list.append(lesson_dict)

    return results_list, total
