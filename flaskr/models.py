from sqlalchemy import create_engine, Column, Integer, String, Date, Time, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin
from flaskr.extensions import database
    
Base = database.Model

class DostupneHodiny(Base):
    __tablename__ = 'dostupne_hodiny'
    ID_hodiny = Column(Integer, primary_key=True)
    datum = Column(Date, nullable=False)
    cas_zacatku = Column(Time, nullable=False)
    stav = Column(String(10), nullable=False)
    typ_hodiny = Column(String(30), nullable=False)
    obsazenost = Column(Integer)
    kapacita = Column(Integer)

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


class SpravceSkoly(Base):
    __tablename__ = 'spravce_skoly'
    ID_osoba = Column(Integer, ForeignKey('osoba.ID_osoba'), primary_key=True)
    osoba = relationship("Osoba", backref=backref("spravce_skoly", uselist=False))

class Instruktor(Base):
    __tablename__ = 'instruktor'
    ID_osoba = Column(Integer, ForeignKey('osoba.ID_osoba'), primary_key=True)
    seniorita = Column(String(10), nullable=False)
    datum_narozeni = Column(Date, nullable=False)
    datum_nastupu = Column(Date, nullable=False)
    image_path = Column(String(255))
    popis = Column(String(255))
    osoba = relationship("Osoba", backref=backref("instruktor", uselist=False))

class Klient(Base):
    __tablename__ = 'klient'
    ID_osoba = Column(Integer, ForeignKey('osoba.ID_osoba'), primary_key=True)
    osoba = relationship("Osoba", backref=backref("klient", uselist=False))

class MaVypsane(Base):
    __tablename__ = 'ma_vypsane'
    ID_osoba = Column(Integer, ForeignKey('instruktor.ID_osoba'), primary_key=True)
    ID_hodiny = Column(Integer, ForeignKey('dostupne_hodiny.ID_hodiny'), primary_key=True)
    instruktor = relationship(Instruktor, backref='ma_vypsane')
    dostupne_hodiny = relationship(DostupneHodiny, backref='ma_vypsane')

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

class Zak(Base):
    __tablename__ = 'zak'
    ID_zak = Column(Integer, primary_key=True, autoincrement=True)
    ID_rezervace = Column(Integer, ForeignKey('rezervace.ID_rezervace'), nullable=False)
    jmeno = Column(String(20), nullable=False)
    prijmeni = Column(String(30), nullable=False)
    zkusenost = Column(String(20), nullable=False)
    vek = Column(Integer, nullable=False)
    rezervace = relationship("Rezervace", backref='zak')