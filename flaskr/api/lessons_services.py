from flaskr.db import get_db

def get_paginated_lessons(page, per_page, selected_date=None):
    db = get_db()
    base_query = 'SELECT ID_hodiny, datum, cas_zacatku, prijmeni, stav, typ_hodiny, obsazenost FROM dostupne_hodiny LEFT JOIN ma_vypsane USING (ID_hodiny) LEFT JOIN Instruktor USING (ID_osoba)'
    
    if selected_date:
        lessons = db.execute(f"{base_query} WHERE datum = ? LIMIT ? OFFSET ?", (selected_date, per_page, (page - 1) * per_page)).fetchall()
        total = db.execute('SELECT COUNT(*) FROM dostupne_hodiny WHERE datum = ?', (selected_date,)).fetchone()[0]
    else:
        lessons = db.execute(f"{base_query} LIMIT ? OFFSET ?", (per_page, (page - 1) * per_page)).fetchall()
        total = db.execute('SELECT COUNT(*) FROM dostupne_hodiny').fetchone()[0]

    return lessons, total