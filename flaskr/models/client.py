# FileName: client.py
# Description: Defines the database model for clients.
# Author: Petr Štípek
# Date: 2024

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from flaskr.database_models import Base

class Klient(Base):
    __tablename__ = 'klient'
    ID_osoba = Column(Integer, ForeignKey('osoba.ID_osoba'), primary_key=True)
    osoba = relationship("Osoba", backref=backref("klient", uselist=False))