# FileName: reservation.py
# Description: Defines the database model for reservations.
# Also defines the relationships between reservations and other entities.
# Author: Petr Štípek
# Date: 2024

from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from flaskr.database_models import Base

from flaskr.models.client import Klient
from flaskr.models.available_times import DostupneHodiny
from flaskr.models.instructor import Instruktor

class Rezervace(Base):
    __tablename__ = 'rezervace'
    ID_rezervace = Column(Integer, primary_key=True)
    ID_osoba = Column(Integer, ForeignKey('klient.ID_osoba'), nullable=False)
    typ_rezervace = Column(String(20), nullable=False)
    termin = Column(Date, nullable=False)
    cas_zacatku = Column(Time, nullable=False)
    doba_vyuky = Column(Integer, nullable=False)
    jazyk = Column(String(20), nullable=False)
    pocet_zaku = Column(Integer, nullable=False)
    platba = Column(String(20), nullable=False)
    rezervacni_kod = Column(String(20), nullable=False)
    poznamka = Column(String(255))
    klient = relationship(Klient, backref='rezervace')

class MaVypsane(Base):
    __tablename__ = 'ma_vypsane'
    ID_osoba = Column(Integer, ForeignKey('instruktor.ID_osoba'), primary_key=True)
    ID_hodiny = Column(Integer, ForeignKey('dostupne_hodiny.ID_hodiny'), primary_key=True)
    instruktor = relationship(Instruktor, backref='ma_vypsane')
    dostupne_hodiny = relationship(DostupneHodiny, backref='ma_vypsane')

class MaVyuku(Base):
    __tablename__ = 'ma_vyuku'
    ID_osoba = Column(Integer, ForeignKey('instruktor.ID_osoba'), primary_key=True)
    ID_rezervace = Column(Integer, ForeignKey('rezervace.ID_rezervace'), primary_key=True)
    pohotovost = Column(String(100))
    instruktor = relationship(Instruktor, backref='ma_vyuku')
    rezervace = relationship(Rezervace, backref='ma_vyuku')

class Prirazeno(Base):
    __tablename__ = 'prirazeno'
    ID_rezervace = Column(Integer, ForeignKey('rezervace.ID_rezervace'), primary_key=True)
    ID_hodiny = Column(Integer, ForeignKey('dostupne_hodiny.ID_hodiny'), primary_key=True)
    rezervace = relationship(Rezervace, backref='prirazeno')
    dostupne_hodiny = relationship(DostupneHodiny, backref='prirazeno')