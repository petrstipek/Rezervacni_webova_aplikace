from flaskr.db import get_db

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