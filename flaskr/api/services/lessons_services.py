from flaskr.db import get_db

def get_paginated_lessons(page, per_page, selected_date=None):
    db = get_db()
    base_query = 'SELECT datum, cas_zacatku, jmeno, prijmeni, stav, typ_hodiny, obsazenost FROM dostupne_hodiny LEFT JOIN ma_vypsane USING (ID_hodiny) LEFT JOIN Instruktor USING (ID_osoba)'
    columns = ["Termín", "Čas začátku", "Jméno", "Příjmení", "Stav", "Typ hodiny", "Obsazenost"]
    if selected_date:
        lessons = db.execute(f"{base_query} WHERE datum = ? LIMIT ? OFFSET ?", (selected_date, per_page, (page - 1) * per_page)).fetchall()
        total = db.execute('SELECT COUNT(*) FROM dostupne_hodiny WHERE datum = ?', (selected_date,)).fetchone()[0]
    else:
        lessons = db.execute(f"{base_query} LIMIT ? OFFSET ?", (per_page, (page - 1) * per_page)).fetchall()
        total = db.execute('SELECT COUNT(*) FROM dostupne_hodiny').fetchone()[0]

    results_list = [{column: row[i] for i, column in enumerate(columns)} for row in lessons]
    return results_list, total