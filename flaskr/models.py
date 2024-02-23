import sqlite3
from flask_login import LoginManager, UserMixin
#from flaskr import login_manager
from flaskr.db import get_db

class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email
    
    @staticmethod
    def get(user_id):
        conn = get_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM spravce_skoly WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return User(id=user['id_osoba'], username=user['prihl_jmeno'], email=user['email'])
        else:
            return None

