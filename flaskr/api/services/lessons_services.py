from flaskr.db import get_db
from flaskr.extensions import database
from flaskr.models import DostupneHodiny, MaVypsane, Instruktor, Osoba
from datetime import date, time

def get_paginated_lessons(page, per_page, selected_date=None):
    base_query = database.session.query(
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
    print(base_query, "base qeury here")
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
            'Termín': lesson[0].strftime('%Y-%m-%d') if isinstance(lesson[0], date) else lesson[0],
            'Čas začátku': lesson[1].strftime('%H:%M') if isinstance(lesson[1], time) else lesson[1], 
            'Jméno': lesson[2],
            'Příjmení': lesson[3],
            'Stav': lesson[4],
            'Typ hodiny': lesson[5],
            'Zbývající kapacita': lesson[6]
        }
        results_list.append(lesson_dict)

    return results_list, total
