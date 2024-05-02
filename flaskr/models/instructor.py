# FileName: instructor.py
# Description: Defines the database model for instructors.
# Author: Petr Štípek
# Date: 2024

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship, backref
from flaskr.database_models import Base

class Instruktor(Base):
    __tablename__ = 'instruktor'
    ID_osoba = Column(Integer, ForeignKey('osoba.ID_osoba'), primary_key=True)
    seniorita = Column(String(10), nullable=False)
    datum_narozeni = Column(Date, nullable=False)
    datum_nastupu = Column(Date, nullable=False)
    image_path = Column(String(255))
    popis = Column(String(255))
    osoba = relationship("Osoba", backref=backref("instruktor", uselist=False))