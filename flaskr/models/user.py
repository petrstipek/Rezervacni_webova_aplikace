# FileName: user.py
# Description: Defines the database model for users.
# Author: Petr Štípek
# Date: 2024

from sqlalchemy import Column, Integer, String, DateTime
from flaskr.database_models import Base

from flaskr.models.instructor import Instruktor
from flaskr.models.reservation import Rezervace, MaVypsane, MaVyuku, Prirazeno
from flaskr.models.client import Klient
from flaskr.models.student import Zak
from flaskr.models.available_times import DostupneHodiny
from flaskr.models.school_admin import SpravceSkoly

class Osoba(Base):
    __tablename__ = 'osoba'
    ID_osoba = Column(Integer, primary_key=True)
    jmeno = Column(String(20), nullable=False)
    prijmeni = Column(String(30), nullable=False)
    email = Column(String(255), nullable=False)
    tel_cislo = Column(String(15), nullable=False)
    prihl_jmeno = Column(String(255))
    heslo = Column(String(255))

    password_change_attempts = Column(Integer, default=0, nullable=False)
    last_password_change_attempt = Column(DateTime)

    def get_id(self):
        return str(self.ID_osoba)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_role(self):
        if self.spravce_skoly:
            return 'admin'
        elif self.instruktor:
            return 'instructor'
        elif self.klient:
            return 'client'
        else:
            return 'unknown'